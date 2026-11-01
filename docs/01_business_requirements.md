# 01 · Business Requirements

## 1. Background
A financial services company processes card payments, transfers, loan EMIs, deposits and other transactions across seven channels (Branch, ATM, POS, UPI, Net Banking, Mobile App, Auto Debit). Reporting was spread across spreadsheets, and the numbers did not always agree, because the source data held duplicates and entry errors.

## 2. Objectives
| # | Objective | Success measure |
| --- | --- | --- |
| O1 | One trusted source of transaction data | Clean, validated tables in PostgreSQL. Every fix logged |
| O2 | Monitor business performance | KPI cards for value, volume, average ticket, fees, tax and success rate, each with a YoY comparison |
| O3 | Find where transactions fail | Failure rate by channel and merchant category |
| O4 | Understand customers and regions | Value by segment, state, gender and age group |
| O5 | Check the fraud signal | Risk score compared between fraud and normal transactions |
| O6 | Refresh without manual work | One command rebuilds the data, and one click refreshes the dashboard |

## 3. Stakeholders
| Stakeholder | Needs |
| --- | --- |
| Senior management | Headline KPIs and trends at a glance |
| Operations / channel heads | Failure rates by channel, to target fixes |
| Product and pricing | Fee income by transaction type |
| Risk and compliance | Fraud volume and risk-score reliability |
| MIS / analytics team | A repeatable, documented, auditable pipeline |

## 4. KPI definitions
| KPI | Definition | Where calculated |
| --- | --- | --- |
| Total Amount | Sum of `amount` | SQL view `v_kpi_by_year`, DAX `[Total Amount]` |
| Total Transactions | Count of transactions | `COUNT(*)`, DAX `COUNTROWS` |
| Avg Transaction | Total Amount ÷ Total Transactions | SQL and DAX |
| Total Fees / Total Tax | Sum of `fee` / `tax`. Tax = 18% GST on the fee | SQL and DAX |
| Success Rate % | Successful ÷ all transactions | `COUNT(*) FILTER (WHERE status='Success')` |
| Failure Rate % | Failed ÷ all transactions | Same pattern |
| YoY % (YTD) | Year to date vs the **same days** of the previous year | DAX (see [Power BI model](05_power_bi_model.md)) |
| Avg Risk Score | Mean `risk_score` (1–100) | SQL and DAX |

## 5. Scope
**In scope:** transactions from Jan 2023 to Apr 2026; customer attributes (segment, state, city, gender, age, occupation); data cleaning, database, KPIs and dashboard.
**Out of scope:** real-time streaming, individual customer credit decisions, predictive fraud modelling (proposed as a next step).

## 6. Assumptions
- A negative `amount` is a sign-entry error, because its fee and tax are positive.
- A blank fee can be rebuilt as `tax ÷ 0.18`, a rule confirmed on 29,000+ rows where both were present.
- Customer age is measured at the last data date, 30 Apr 2026.
