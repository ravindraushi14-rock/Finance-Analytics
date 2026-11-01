-- =====================================================================
-- 02_kpi_views.sql   (PostgreSQL)
-- VIEWS = saved queries. They store no data; every time you read a view
-- it recalculates from the tables, so the KPIs are always current.
-- Power BI connects to PostgreSQL and reads these views directly.
--
-- PostgreSQL tip used below: COUNT(*) FILTER (WHERE ...) counts only the
-- rows that match the condition. It is shorter than SUM(CASE WHEN ...).
-- =====================================================================

-- ---------------------------------------------------------------------
-- v_fact_transactions: the main table for Power BI.
-- JOIN brings each transaction's customer details onto the same row.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_fact_transactions AS
SELECT
    t.transaction_id, t.transaction_date, t.year, t.month,
    t.transaction_type, t.channel, t.merchant_category,
    t.amount, t.fee, t.tax, t.status, t.is_fraud, t.risk_score,
    c.customer_id, c.gender, c.age,
    CASE WHEN c.age < 25 THEN 'Under 25'
         WHEN c.age < 40 THEN '25-39'
         WHEN c.age < 60 THEN '40-59'
         ELSE '60+' END                                          AS age_group,
    c.state, c.city, c.occupation, c.customer_segment
FROM transactions AS t
JOIN customers   AS c ON c.customer_id = t.customer_id;

-- ---------------------------------------------------------------------
-- v_kpi_by_year: the KPI cards, one row per year.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_kpi_by_year AS
SELECT
    year,
    SUM(amount)                                                  AS total_amount,
    COUNT(*)                                                     AS total_transactions,
    ROUND(AVG(amount), 2)                                        AS avg_transaction,
    SUM(fee)                                                     AS total_fees,
    SUM(tax)                                                     AS total_tax,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'Success') / COUNT(*), 2) AS success_rate_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'Failed')  / COUNT(*), 2) AS failure_rate_pct
FROM transactions
GROUP BY year
ORDER BY year;

-- ---------------------------------------------------------------------
-- v_yoy_growth: year-over-year growth with the LAG window function.
-- LAG(x) = the value of x in the previous row (here, the previous year).
-- Note: 2026 holds only Jan-Apr, so its growth vs a full year is not like-for-like.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_yoy_growth AS
SELECT
    year,
    total_amount,
    LAG(total_amount) OVER (ORDER BY year)                       AS prev_year_amount,
    ROUND(100.0 * (total_amount - LAG(total_amount) OVER (ORDER BY year))
                / LAG(total_amount) OVER (ORDER BY year), 2)     AS yoy_growth_pct
FROM v_kpi_by_year;

-- ---------------------------------------------------------------------
-- v_monthly_trend: one row per month for the trend chart.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_monthly_trend AS
SELECT
    month,
    SUM(amount) AS total_amount,
    COUNT(*)    AS total_transactions,
    SUM(fee)    AS total_fees,
    SUM(tax)    AS total_tax
FROM transactions
GROUP BY month
ORDER BY month;

-- ---------------------------------------------------------------------
-- v_channel_failure: which channel fails most often?
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_channel_failure AS
SELECT
    channel,
    COUNT(*)                                                     AS total_transactions,
    COUNT(*) FILTER (WHERE status = 'Failed')                    AS failed_transactions,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'Failed') / COUNT(*), 2) AS failure_rate_pct
FROM transactions
GROUP BY channel
ORDER BY failure_rate_pct DESC;

-- ---------------------------------------------------------------------
-- v_segment_share: value by customer segment and its share of the total.
-- SUM(...) OVER () is a window total across all segments.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_segment_share AS
SELECT
    c.customer_segment,
    SUM(t.amount)                                                AS total_amount,
    ROUND(100.0 * SUM(t.amount) / SUM(SUM(t.amount)) OVER (), 2) AS share_pct
FROM transactions t
JOIN customers c ON c.customer_id = t.customer_id
GROUP BY c.customer_segment
ORDER BY total_amount DESC;

-- ---------------------------------------------------------------------
-- v_state_ranking: states ranked by value with RANK().
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_state_ranking AS
SELECT
    c.state,
    SUM(t.amount)                                                AS total_amount,
    COUNT(*)                                                     AS total_transactions,
    RANK() OVER (ORDER BY SUM(t.amount) DESC)                    AS state_rank
FROM transactions t
JOIN customers c ON c.customer_id = t.customer_id
GROUP BY c.state
ORDER BY state_rank;

-- ---------------------------------------------------------------------
-- v_type_summary: transaction types sorted by fee income.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_type_summary AS
SELECT
    transaction_type,
    SUM(amount) AS total_amount,
    COUNT(*)    AS total_transactions,
    SUM(fee)    AS total_fees,
    SUM(tax)    AS total_tax
FROM transactions
GROUP BY transaction_type
ORDER BY total_fees DESC;
