-- =====================================================================
-- 03_analysis_queries.sql   (PostgreSQL)
-- Business questions answered with SQL. In pgAdmin, open the Query Tool on
-- finance_db, select ONE query and press F5 to run just that query.
-- Good interview practice: read the question, write your own query,
-- then compare it with the one below.
-- =====================================================================

-- Q1. What is the overall size of the business?
SELECT COUNT(*)                    AS transactions,
       ROUND(SUM(amount) / 1e7, 2) AS amount_crore,
       ROUND(AVG(amount), 0)       AS avg_transaction
FROM transactions;

-- Q2. What share of transactions succeed, fail or stay pending?
SELECT status,
       COUNT(*) AS transactions,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct
FROM transactions
GROUP BY status
ORDER BY transactions DESC;

-- Q3. Top 5 customers by transaction value (with their segment)
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer_name,
       c.customer_segment,
       SUM(t.amount) AS total_amount
FROM transactions t
JOIN customers c ON c.customer_id = t.customer_id
GROUP BY c.customer_id
ORDER BY total_amount DESC
LIMIT 5;

-- Q4. Which channel + merchant category combinations fail most?
--     HAVING filters groups after GROUP BY, keeping only combos with enough volume.
SELECT channel, merchant_category,
       COUNT(*) AS transactions,
       ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'Failed') / COUNT(*), 2) AS failure_rate_pct
FROM transactions
GROUP BY channel, merchant_category
HAVING COUNT(*) >= 300
ORDER BY failure_rate_pct DESC
LIMIT 10;

-- Q5. Fraud: how many flagged transactions, and how much value, by channel?
SELECT channel,
       COUNT(*) FILTER (WHERE is_fraud = 'Yes')              AS fraud_transactions,
       COALESCE(SUM(amount) FILTER (WHERE is_fraud = 'Yes'), 0) AS fraud_amount
FROM transactions
GROUP BY channel
ORDER BY fraud_transactions DESC;

-- Q6. Is risk_score higher for fraud? (checks whether the risk model works)
SELECT is_fraud,
       ROUND(AVG(risk_score), 1) AS avg_risk_score,
       COUNT(*)                  AS transactions
FROM transactions
GROUP BY is_fraud;

-- Q7. Age groups: who transacts the most? (CASE builds the groups)
SELECT CASE WHEN c.age < 25 THEN '1. Under 25'
            WHEN c.age < 40 THEN '2. 25-39'
            WHEN c.age < 60 THEN '3. 40-59'
            ELSE                 '4. 60+' END AS age_group,
       COUNT(*)                        AS transactions,
       ROUND(SUM(t.amount) / 1e7, 2)   AS amount_crore
FROM transactions t
JOIN customers c ON c.customer_id = t.customer_id
GROUP BY age_group
ORDER BY age_group;

-- Q8. Month with the highest value in each year
--     (window function in a sub-query, then filter on its result)
SELECT year, month, total_amount
FROM (
    SELECT year, month, SUM(amount) AS total_amount,
           RANK() OVER (PARTITION BY year ORDER BY SUM(amount) DESC) AS rnk
    FROM transactions
    GROUP BY year, month
) AS monthly
WHERE rnk = 1
ORDER BY year;

-- Q9. What did cleaning fix? Transactions whose negative amount was corrected
SELECT transaction_id, transaction_date, amount, fee
FROM transactions
WHERE amount_was_negative = 'Yes'
ORDER BY transaction_id;
