import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

# ── Load Data ─────────────────────────────────────────────────────────────────
df = pd.read_csv("data/jnpt_throughput.csv")
df["date"] = pd.to_datetime(df["date"])

# ── Prepare for Prophet ───────────────────────────────────────────────────────
# Prophet requires columns named exactly "ds" (date) and "y" (value)
prophet_df = df[["date", "teu_volume"]].rename(
    columns={"date": "ds", "teu_volume": "y"}
)

print("=" * 55)
print("📦 JNPT Port Throughput Forecasting — Facebook Prophet")
print("=" * 55)
print(f"   Training data : {prophet_df['ds'].min().date()} → "
      f"{prophet_df['ds'].max().date()}")
print(f"   Total months  : {len(prophet_df)}")
print(f"   TEU range     : {prophet_df['y'].min():,} → "
      f"{prophet_df['y'].max():,}")
print()

# ── Train / Test Split ────────────────────────────────────────────────────────
# Use last 12 months as test set to evaluate model accuracy
TEST_MONTHS  = 12
train = prophet_df.iloc[:-TEST_MONTHS]
test  = prophet_df.iloc[-TEST_MONTHS:]

print(f"   Train size : {len(train)} months")
print(f"   Test size  : {len(test)} months (holdout for accuracy eval)")
print()

# ── Build & Train Prophet Model ───────────────────────────────────────────────
# yearly_seasonality — captures Jan/Feb dip, Oct/Nov peak
# changepoint_prior_scale — how flexible the trend line is (0.1 = moderate)
model = Prophet(
    yearly_seasonality      = True,
    weekly_seasonality      = False,   # monthly data, no weekly pattern
    daily_seasonality       = False,
    changepoint_prior_scale = 0.1,
    seasonality_prior_scale = 10,
    interval_width          = 0.95     # 95% confidence interval
)

print("⏳ Training Prophet model on 108 months of data...")
model.fit(train)
print("✅ Model trained successfully!")
print()

# ── Evaluate on Test Set (last 12 months) ────────────────────────────────────
test_future = model.make_future_dataframe(periods=TEST_MONTHS, freq="MS")
test_forecast = model.predict(test_future)

# Extract predictions for test period only
test_preds = test_forecast.tail(TEST_MONTHS)[["ds", "yhat",
                                               "yhat_lower", "yhat_upper"]]
test_preds = test_preds.reset_index(drop=True)
test_actual = test.reset_index(drop=True)

# ── Accuracy Metrics ──────────────────────────────────────────────────────────
mae  = mean_absolute_error(test_actual["y"], test_preds["yhat"])
rmse = np.sqrt(mean_squared_error(test_actual["y"], test_preds["yhat"]))
mape = (np.abs((test_actual["y"] - test_preds["yhat"])
               / test_actual["y"]).mean() * 100)
accuracy = 100 - mape

print("=" * 55)
print("📊 MODEL ACCURACY METRICS (on 12-month holdout)")
print("=" * 55)
print(f"   MAE      : {mae:,.0f} TEUs")
print(f"   RMSE     : {rmse:,.0f} TEUs")
print(f"   MAPE     : {mape:.2f}%")
print(f"   Accuracy : {accuracy:.2f}%")
print()

# ── Forecast Next 6 Months (Jan–Jun 2025) ────────────────────────────────────
# Retrain on FULL dataset for best possible forecast
model_full = Prophet(
    yearly_seasonality      = True,
    weekly_seasonality      = False,
    daily_seasonality       = False,
    changepoint_prior_scale = 0.1,
    seasonality_prior_scale = 10,
    interval_width          = 0.95
)
model_full.fit(prophet_df)

future     = model_full.make_future_dataframe(periods=6, freq="MS")
forecast   = model_full.predict(future)
future_only = forecast.tail(6)[["ds", "yhat",
                                 "yhat_lower", "yhat_upper"]].reset_index(drop=True)
future_only["yhat"]       = future_only["yhat"].round(0).astype(int)
future_only["yhat_lower"] = future_only["yhat_lower"].round(0).astype(int)
future_only["yhat_upper"] = future_only["yhat_upper"].round(0).astype(int)
future_only.columns       = ["Month", "Forecast_TEU",
                              "Lower_95CI", "Upper_95CI"]

print("=" * 55)
print("🔮 6-MONTH FORECAST — Jan 2025 to Jun 2025")
print("=" * 55)
print(future_only.to_string(index=False))
print()
print(f"   Total forecast (6 months) : "
      f"{future_only['Forecast_TEU'].sum():,} TEUs")
print(f"   Avg monthly forecast      : "
      f"{future_only['Forecast_TEU'].mean():,.0f} TEUs")

# ── Save Forecast to CSV ──────────────────────────────────────────────────────
future_only.to_csv("outputs/forecast_6months.csv", index=False)
print()
print("✅ Forecast saved → outputs/forecast_6months.csv")

# ── Visualization ─────────────────────────────────────────────────────────────
print()
print("⏳ Generating forecast plot...")

fig, axes = plt.subplots(2, 1, figsize=(14, 12))
fig.patch.set_facecolor("#F8F9FA")

# ── Plot 1: Full historical + forecast ───────────────────────────────────────
ax1 = axes[0]
ax1.set_facecolor("#F8F9FA")

# Historical data
ax1.plot(prophet_df["ds"], prophet_df["y"],
         color="#1F3864", linewidth=2, label="Historical TEU", zorder=3)

# Forecast line (full period including historical fitted values)
ax1.plot(forecast["ds"], forecast["yhat"],
         color="#2E75B6", linewidth=1.5, linestyle="--",
         label="Model Fit / Forecast", zorder=2)

# Confidence interval for forecast period only
future_dates = forecast.tail(6)
ax1.fill_between(future_dates["ds"],
                 future_dates["yhat_lower"],
                 future_dates["yhat_upper"],
                 alpha=0.3, color="#2E75B6", label="95% Confidence Interval")

# Forecast points
ax1.scatter(future_only["Month"], future_only["Forecast_TEU"],
            color="#C55A11", s=80, zorder=5, label="Forecast Points")

# Vertical line separating history and forecast
ax1.axvline(x=prophet_df["ds"].max(), color="#C55A11",
            linestyle=":", linewidth=1.5, alpha=0.7)
ax1.text(prophet_df["ds"].max(), ax1.get_ylim()[0],
         " Forecast\n Start", color="#C55A11", fontsize=9)

ax1.set_title("JNPT Container Throughput — Historical & 6-Month Forecast",
              fontsize=14, fontweight="bold", color="#1F3864", pad=15)
ax1.set_ylabel("TEU Volume", fontsize=11)
ax1.set_xlabel("")
ax1.legend(loc="upper left", fontsize=9)
ax1.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
ax1.grid(True, alpha=0.3, linestyle="--")
ax1.spines[["top", "right"]].set_visible(False)

# ── Plot 2: 6-month forecast bar chart ───────────────────────────────────────
ax2 = axes[1]
ax2.set_facecolor("#F8F9FA")

months_str = future_only["Month"].dt.strftime("%b %Y")
bars = ax2.bar(months_str, future_only["Forecast_TEU"],
               color="#2E75B6", edgecolor="#1F3864",
               linewidth=0.8, zorder=3)

# Error bars for confidence interval
yerr_lower = future_only["Forecast_TEU"] - future_only["Lower_95CI"]
yerr_upper = future_only["Upper_95CI"]   - future_only["Forecast_TEU"]
ax2.errorbar(months_str, future_only["Forecast_TEU"],
             yerr=[yerr_lower, yerr_upper],
             fmt="none", color="#C55A11", capsize=6,
             linewidth=1.5, zorder=4)

# Value labels on bars
for bar, val in zip(bars, future_only["Forecast_TEU"]):
    ax2.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 500,
             f"{val:,}", ha="center", va="bottom",
             fontsize=10, fontweight="bold", color="#1F3864")

ax2.set_title("6-Month TEU Forecast — Jan 2025 to Jun 2025  "
              f"(Model Accuracy: {accuracy:.1f}%)",
              fontsize=13, fontweight="bold", color="#1F3864", pad=15)
ax2.set_ylabel("Forecast TEU Volume", fontsize=11)
ax2.set_xlabel("Month", fontsize=11)
ax2.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
ax2.set_ylim(0, future_only["Upper_95CI"].max() * 1.15)
ax2.grid(True, alpha=0.3, linestyle="--", axis="y")
ax2.spines[["top", "right"]].set_visible(False)

# Accuracy badge
ax2.text(0.98, 0.95,
         f"MAE: {mae:,.0f} TEUs\nRMSE: {rmse:,.0f} TEUs\nMAPE: {mape:.2f}%",
         transform=ax2.transAxes, fontsize=9,
         verticalalignment="top", horizontalalignment="right",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#D6E4F0",
                   edgecolor="#2E75B6", alpha=0.9))

plt.suptitle("GTI – APM Terminals Mumbai | Port Throughput Forecasting System",
             fontsize=12, color="#666666", y=1.01)
plt.tight_layout()

# Save
plt.savefig("outputs/forecast_plot.png", dpi=150,
            bbox_inches="tight", facecolor="#F8F9FA")
print("✅ Forecast plot saved → outputs/forecast_plot.png")

plt.show()
print()
print("=" * 55)
print("✅ Step 4 Complete — Forecasting model done!")
print("=" * 55)