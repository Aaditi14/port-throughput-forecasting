-- JNPT Port Throughput SQL Analysis
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
