import sqlite3
import pandas as pd

# ── Load CSV ──────────────────────────────────────────────────────────────────
df = pd.read_csv("data/jnpt_throughput.csv")

# ── Create in-memory SQLite DB and load data ──────────────────────────────────
conn = sqlite3.connect("data/jnpt_throughput.db")
df.to_sql("throughput", conn, if_exists="replace", index=False)
print("✅ Data loaded into SQLite → data/jnpt_throughput.db")
print(f"   Rows inserted: {len(df)}\n")

# ── Helper function to run and display queries ────────────────────────────────
def run_query(title, sql):
    print(f"{'='*55}")
    print(f"📊 {title}")
    print(f"{'='*55}")
    result = pd.read_sql_query(sql, conn)
    print(result.to_string(index=False))
    print()
    return result

# ── Query 1: Annual throughput summary ───────────────────────────────────────
q1 = run_query("Annual Throughput Summary", """
    SELECT
        year,
        SUM(teu_volume)                          AS total_teu,
        ROUND(AVG(teu_volume), 0)                AS avg_monthly_teu,
        MIN(teu_volume)                          AS min_monthly_teu,
        MAX(teu_volume)                          AS max_monthly_teu
    FROM throughput
    GROUP BY year
    ORDER BY year
""")

# ── Query 2: Best and worst months across all years ───────────────────────────
q2 = run_query("Top 5 Highest Volume Months (All Time)", """
    SELECT
        date,
        year,
        month_name,
        teu_volume
    FROM throughput
    ORDER BY teu_volume DESC
    LIMIT 5
""")

q3 = run_query("Top 5 Lowest Volume Months (All Time)", """
    SELECT
        date,
        year,
        month_name,
        teu_volume
    FROM throughput
    ORDER BY teu_volume ASC
    LIMIT 5
""")

# ── Query 3: Average TEU by month (seasonality pattern) ──────────────────────
q4 = run_query("Seasonality — Avg TEU by Calendar Month", """
    SELECT
        month,
        month_name,
        ROUND(AVG(teu_volume), 0)   AS avg_teu,
        ROUND(MIN(teu_volume), 0)   AS min_teu,
        ROUND(MAX(teu_volume), 0)   AS max_teu
    FROM throughput
    GROUP BY month, month_name
    ORDER BY month
""")

# ── Query 4: Year-over-Year growth rate ───────────────────────────────────────
q5 = run_query("Year-over-Year Growth Rate", """
    SELECT
        year,
        SUM(teu_volume) AS total_teu,
        ROUND(
            (SUM(teu_volume) - LAG(SUM(teu_volume)) OVER (ORDER BY year))
            * 100.0
            / LAG(SUM(teu_volume)) OVER (ORDER BY year),
        2) AS yoy_growth_pct
    FROM throughput
    GROUP BY year
    ORDER BY year
""")

# ── Query 5: COVID impact — 2019 vs 2020 comparison ──────────────────────────
q6 = run_query("COVID Impact — 2019 vs 2020 Monthly Comparison", """
    SELECT
        month,
        month_name,
        SUM(CASE WHEN year = 2019 THEN teu_volume END) AS teu_2019,
        SUM(CASE WHEN year = 2020 THEN teu_volume END) AS teu_2020,
        ROUND(
            (SUM(CASE WHEN year = 2020 THEN teu_volume END) -
             SUM(CASE WHEN year = 2019 THEN teu_volume END))
            * 100.0
            / SUM(CASE WHEN year = 2019 THEN teu_volume END),
        2) AS change_pct
    FROM throughput
    WHERE year IN (2019, 2020)
    GROUP BY month, month_name
    ORDER BY month
""")

# ── Save all query results to SQL file for GitHub ────────────────────────────
sql_text = """-- JNPT Port Throughput SQL Analysis
-- Database: SQLite | Table: throughput

-- Q1: Annual Throughput Summary
SELECT year,
       SUM(teu_volume) AS total_teu,
       ROUND(AVG(teu_volume), 0) AS avg_monthly_teu,
       MIN(teu_volume) AS min_monthly_teu,
       MAX(teu_volume) AS max_monthly_teu
FROM throughput
GROUP BY year ORDER BY year;

-- Q2: Top 5 Highest Volume Months
SELECT date, year, month_name, teu_volume
FROM throughput ORDER BY teu_volume DESC LIMIT 5;

-- Q3: Seasonality Pattern
SELECT month, month_name,
       ROUND(AVG(teu_volume), 0) AS avg_teu
FROM throughput GROUP BY month, month_name ORDER BY month;

-- Q4: YoY Growth Rate
SELECT year, SUM(teu_volume) AS total_teu,
       ROUND((SUM(teu_volume) - LAG(SUM(teu_volume)) OVER (ORDER BY year))
       * 100.0 / LAG(SUM(teu_volume)) OVER (ORDER BY year), 2) AS yoy_growth_pct
FROM throughput GROUP BY year ORDER BY year;

-- Q5: COVID Impact 2019 vs 2020
SELECT month, month_name,
       SUM(CASE WHEN year = 2019 THEN teu_volume END) AS teu_2019,
       SUM(CASE WHEN year = 2020 THEN teu_volume END) AS teu_2020
FROM throughput WHERE year IN (2019, 2020)
GROUP BY month, month_name ORDER BY month;
"""

with open("sql/analysis_queries.sql", "w") as f:
    f.write(sql_text)

print("✅ SQL queries saved → sql/analysis_queries.sql")

conn.close()
print("✅ Step 2 Complete — SQL analysis done!")