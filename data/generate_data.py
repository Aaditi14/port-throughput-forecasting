import pandas as pd
import numpy as np

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)

# ── Parameters ───────────────────────────────────────────────────────────────
START_YEAR   = 2015
END_YEAR     = 2024
MONTHS       = pd.date_range(start=f"{START_YEAR}-01-01",
                              end=f"{END_YEAR}-12-31", freq="MS")

# ── 1. Long-term growth trend (JNPT grew ~1.44M TEU in 2015 → ~2.08M in 2024)
#       We model monthly base as a linear ramp from 120k → 173k TEUs
n = len(MONTHS)   # 120 months
trend = np.linspace(120_000, 173_000, n)

# ── 2. Seasonality (ports are busier Oct–Dec, slower Jan–Feb)
#       Amplitude ~8% of the mean value
monthly_factors = np.array([
    -0.07, -0.05, -0.02,  0.00,  0.02,  0.03,
     0.04,  0.05,  0.06,  0.07,  0.05, -0.01
])  # Jan → Dec
seasonality = np.tile(monthly_factors, END_YEAR - START_YEAR + 1) * 150_000

# ── 3. Random noise (±3% realistic operational variance)
noise = np.random.normal(0, 4_500, n)

# ── 4. COVID dip (Apr–Jun 2020 = months 63–65, 0-indexed)
covid_dip = np.zeros(n)
covid_dip[63] = -22_000   # April 2020
covid_dip[64] = -30_000   # May 2020  ← sharpest drop
covid_dip[65] = -18_000   # June 2020

# ── 5. Combine all components
teu_volume = trend + seasonality + noise + covid_dip
teu_volume = np.round(teu_volume).astype(int)
teu_volume = np.clip(teu_volume, 90_000, 210_000)  # hard safety bounds

# ── Build DataFrame ───────────────────────────────────────────────────────────
df = pd.DataFrame({
    "date"       : MONTHS,
    "year"       : MONTHS.year,
    "month"      : MONTHS.month,
    "month_name" : MONTHS.strftime("%b"),
    "teu_volume" : teu_volume
})

# ── Derived columns (useful for SQL & Excel analysis) ────────────────────────
df["yoy_growth_pct"] = df["teu_volume"].pct_change(12).mul(100).round(2)
df["mom_growth_pct"] = df["teu_volume"].pct_change(1).mul(100).round(2)
df["rolling_12m_avg"] = (
    df["teu_volume"].rolling(12).mean().round(0).astype("Int64")
)

# ── Save ─────────────────────────────────────────────────────────────────────
output_path = "jnpt_throughput.csv"
df.to_csv(output_path, index=False)

# ── Validation printout ───────────────────────────────────────────────────────
print("=" * 50)
print(f"✅ Dataset generated → {output_path}")
print(f"   Rows  : {len(df)}")
print(f"   Range : {df['date'].min().date()} to {df['date'].max().date()}")
print(f"   TEU min / max : {df['teu_volume'].min():,} / {df['teu_volume'].max():,}")
print()
print("Annual Totals:")
print(df.groupby("year")["teu_volume"].sum()
        .apply(lambda x: f"{x/1_000_000:.2f}M TEUs"))
print("=" * 50)