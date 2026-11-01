# 04 · SQL Guide (PostgreSQL)

All SQL lives in [`/sql`](../sql). Each file runs on its own in pgAdmin's Query Tool, and the Python pipeline also runs them in order.

## 1. Schema design: `01_create_tables.sql`
| Design choice | Reason |
| --- | --- |
| `transaction_id` **PRIMARY KEY** | Duplicates can never be loaded again |
| `customer_id` **FOREIGN KEY** → customers | No transaction without a known customer |
| `amount NUMERIC(14,2) CHECK (amount >= 0)` | Exact money arithmetic; the database itself rejects negatives |
| `DATE` columns | Real date logic instead of text |
| Indexes on `customer_id`, `transaction_date` | Fast joins and date filters |
| `DROP TABLE … CASCADE` | Safe to re-run; dependent views are rebuilt |

**Loading:** `step03_load_to_sql.py` uses PostgreSQL **`COPY`** to bulk-load each CSV in one statement, which is far faster than row-by-row inserts. It then compares CSV rows with table rows.

## 2. KPI views: `02_kpi_views.sql`
Views store no data. They recalculate on every read, so Power BI always gets current numbers.

| View | Key SQL technique |
| --- | --- |
| `v_fact_transactions` | `JOIN` transactions ↔ customers; `CASE` builds `age_group` |
| `v_kpi_by_year` | Aggregates + `COUNT(*) FILTER (WHERE status = 'Success')` |
| `v_yoy_growth` | Window function **`LAG()`** reads the previous year |
| `v_monthly_trend` | `GROUP BY month` |
| `v_channel_failure` | Conditional counts with `FILTER` |
| `v_segment_share` | **`SUM(SUM(amount)) OVER ()`**: a window total for share % |
| `v_state_ranking` | **`RANK() OVER (ORDER BY SUM(amount) DESC)`** |
| `v_type_summary` | Fee income by type |

Example:
```sql
SELECT year,
       SUM(amount) AS total_amount,
       ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'Failed') / COUNT(*), 2) AS failure_rate_pct
FROM transactions
GROUP BY year;
```

## 3. Business questions: `03_analysis_queries.sql`
| # | Question | Techniques | Answer (clean data) |
| --- | --- | --- | --- |
| Q1 | How big is the business? | Aggregates | 50,000 transactions, ₹45.55 Cr, avg ₹9,111 |
| Q2 | Status mix? | Window `SUM(COUNT(*)) OVER ()` | 85.74% success / 10.19% failed / 4.07% pending |
| Q3 | Top 5 customers by value | `JOIN`, `GROUP BY`, `LIMIT` | Top customer ₹6.01 L |
| Q4 | Worst channel × merchant combos | `HAVING COUNT(*) >= 300` | Auto Debit × Salary 13.7%, ATM × Insurance 13.6% |
| Q5 | Fraud by channel | `FILTER`, `COALESCE` | ATM has the most fraud cases (101) |
| Q6 | Does the risk score work? | `GROUP BY is_fraud` | Fraud avg 82.9 vs normal 35.5 |
| Q7 | Who transacts most by age? | `CASE` groups | 40–59 age group: ₹20.67 Cr |
| Q8 | Peak month each year | Sub-query + `RANK() OVER (PARTITION BY year …)` | May 2023, May 2024, Jul 2025, Mar 2026 |
| Q9 | What did cleaning correct? | Filter on audit flag | 8 sign-corrected transactions |

## 4. Run it yourself
pgAdmin → right-click **finance_db** → **Query Tool** → open a `.sql` file → select one query → **F5**.
