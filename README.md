# Port Container Throughput Forecasting
### Targeting GTI – APM Terminals Mumbai (India's Largest Container Terminal)

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Prophet](https://img.shields.io/badge/Facebook_Prophet-Forecasting-orange)
![SQL](https://img.shields.io/badge/SQL-SQLite-green)
![Excel](https://img.shields.io/badge/Excel-Dashboard-darkgreen)
![Accuracy](https://img.shields.io/badge/Model_Accuracy-97.78%25-brightgreen)

---

## Project Overview

An end-to-end data science project simulating a real-world **container throughput
forecasting system** for JNPT (Jawaharlal Nehru Port Trust) — India's busiest
container port handling ~2M TEUs annually.

This project demonstrates the full data pipeline:
**Data Generation → SQL Analysis → Excel Dashboard → ML Forecasting**

---

## Business Context

Gateway Terminals India (GTI) – APM Terminals Mumbai is targeting **2.4M TEUs
by 2028**. Accurate throughput forecasting is critical for:
- Vessel scheduling and berth planning
- Equipment and manpower allocation
- Revenue projection and capacity planning

This project builds a forecasting system that predicts monthly TEU volumes
6 months ahead with **97.78% accuracy.**

---

## Key Results

| Metric | Value |
|--------|-------|
| Model Accuracy | **97.78%** |
| MAPE | **2.22%** |
| MAE | 3,849 TEUs |
| RMSE | 4,547 TEUs |
| Forecast Horizon | 6 months |
| Training Data | 120 months (2015–2024) |
| TEU Scale | 1.5M → 2.08M TEUs/year |
| YoY Growth Captured | 2016–2024 (+38% total) |
| COVID Impact Detected | -14.4% drop in April 2020 |

---

## Project Structure
port-throughput-forecasting/

├── data/

│   ├── generate_data.py          # Synthetic JNPT dataset generator

│   └── jnpt_throughput.csv       # 120 months of TEU data (2015–2024)

├── notebooks/

│   └── forecasting_model.ipynb   # Jupyter notebook version (coming soon)

├── outputs/

│   ├── forecast_plot.png         # 2-panel forecast visualization

│   ├── forecast_6months.csv      # 6-month TEU predictions with CI

│   └── throughput_dashboard.xlsx # 5-sheet Excel dashboard with charts

├── sql/

│   └── analysis_queries.sql      # 5 analytical SQL queries (SQLite)

├── generate_data.py              # Data generation script

├── sql_analysis.py               # SQL analysis via Python + SQLite

├── dashboard.py                  # Excel dashboard generator

├── forecasting_model.py          # Prophet forecasting model

└── README.md

---

## Tech Stack

| Layer | Tools Used |
|-------|-----------|
| Language | Python 3.12 |
| Forecasting | Facebook Prophet |
| Data Analysis | pandas, numpy |
| Visualization | matplotlib, seaborn |
| SQL | SQLite via sqlite3 |
| Excel | openpyxl, xlsxwriter |
| Version Control | Git + GitHub |

---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Aaditi14/port-throughput-forecasting.git
cd port-throughput-forecasting
```

### 2. Install dependencies
```bash
pip install pandas numpy matplotlib openpyxl xlsxwriter prophet scikit-learn
```

### 3. Generate the dataset
```bash
python generate_data.py
```

### 4. Run SQL analysis
```bash
python sql_analysis.py
```

### 5. Generate Excel dashboard
```bash
python dashboard.py
```

### 6. Run forecasting model
```bash
python forecasting_model.py
```

---

## Forecast Output (Jan–Jun 2025)

| Month | Forecast TEU | Lower 95% CI | Upper 95% CI |
|-------|-------------|--------------|--------------|
| Jan 2025 | 164,811 | 155,546 | 174,056 |
| Feb 2025 | 171,234 | 162,349 | 180,251 |
| Mar 2025 | 169,139 | 160,067 | 178,923 |
| Apr 2025 | 174,547 | 166,059 | 182,274 |
| May 2025 | 176,266 | 167,093 | 185,804 |
| Jun 2025 | 183,390 | 174,250 | 191,629 |

**Total 6-month forecast: 1,039,387 TEUs**

---

## SQL Analysis Highlights

5 analytical queries written in SQLite covering:
- Annual throughput summary (2015–2024)
- Top 5 highest and lowest volume months
- Seasonality pattern (avg TEU by calendar month)
- Year-over-year growth rate analysis
- COVID-19 impact: 2019 vs 2020 monthly comparison

---

## Key Insights

- **Seasonality:** ~18% swing between slowest (Jan: 133K avg) and
  busiest (Nov: 158K avg) months
- **COVID Impact:** April 2020 saw a -14.4% drop; recovery by July 2020
- **Growth Trend:** Port grew 38% over 10 years (1.51M → 2.08M TEUs)
- **Post-COVID:** Strongest recovery in 2021 at +6.87% YoY growth

---

## Author

Aaditi Thakur
BE Computer Science (AI & ML Specialization)
Targeting: Data Analyst / Operations Analytics roles in port & logistics

---

## License
MIT License — free to use and reference