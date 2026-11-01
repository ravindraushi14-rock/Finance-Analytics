# 02 · Data Dictionary

## Source files (`data/raw/`)

### `finance_transactions.csv` (50,069 rows × 15 columns)
| Column | Type | Description | Notes |
| --- | --- | --- | --- |
| transaction_id | text | Transaction identifier (`T00000001`) | 68 exact duplicates, 1 conflicting duplicate |
| transaction_date | text | Date as `dd-mm-yyyy` | Converted to a date |
| account_id | text | Account identifier | |
| customer_id | text | Links to `customers.csv` | All IDs match a customer |
| transaction_type | text | Loan EMI, Transfer, Card Payment, Deposit, Bill Payment, Withdrawal, Interest Credit, Fee Charge, Investment, Refund | 10 values |
| channel | text | Branch, ATM, POS, UPI, Net Banking, Mobile App, Auto Debit | 770 dirty values (`M@bile App`, extra spaces) |
| merchant_category | text | Rent, Salary, Groceries, Insurance, Travel, … | 14 values |
| amount | number | Transaction value (₹) | 8 negative values |
| fee_amount | number | Fee charged (₹), 0 to 0.5% of the amount | 24 blanks |
| tax_amount | number | GST on the fee (₹) = 18% × fee | |
| currency | text | `INR` | 605 in lower or mixed case |
| transaction_status | text | Success, Failed, Pending | |
| is_fraud | text | Yes / No | 632 Yes |
| risk_score | integer | Risk score from 1 to 100 | |
| reference_no | text | Bank reference number | |

### `customers.csv` (5,000 rows × 11 columns)
| Column | Type | Description | Notes |
| --- | --- | --- | --- |
| customer_id | text | Customer identifier (`C00001`) | Unique |
| fisrt_name | text | First name | Typo in the column name, renamed `first_name` |
| second_name | text | Last name | Renamed `last_name` |
| gender | text | Female / Male | |
| date_of_birth | text | `dd-mm-yyyy` | Converted, with age derived |
| city / state | text | 20 cities, 13 states | |
| occupation | text | Salaried, Self Employed, Business Owner, Freelancer, Student, Retired | |
| customer_segment | text | Retail, Premium, SME, Corporate, Wealth | |
| annual_income | number | Annual income (₹) | |
| join_date | text | `dd-mm-yyyy` | Converted |

## Database tables (`finance_db`, schema `public`)

### `transactions` (50,000 rows)
Same fields as the source, cleaned and typed, plus three columns:

| Column | Type | Description |
| --- | --- | --- |
| transaction_id | VARCHAR(12) **PK** | Unique after cleaning |
| transaction_date | DATE | |
| year / month | INTEGER / CHAR(7) | Added for reporting (`2025`, `2025-02`) |
| customer_id | VARCHAR(10) **FK** → customers | |
| amount | NUMERIC(14,2) `CHECK (amount >= 0)` | |
| fee, tax | NUMERIC(12,2) | Renamed from fee_amount / tax_amount |
| status | VARCHAR(10) | Renamed from transaction_status |
| amount_was_negative | VARCHAR(3) | `Yes` if the sign was corrected |

### `customers` (5,000 rows)
`customer_id` (**PK**), first_name, last_name, gender, date_of_birth, **age**, city, state, occupation, customer_segment, annual_income, join_date.

## Reporting view: `v_fact_transactions`
One row per transaction, joined to customer attributes. **Power BI loads this view.**

transaction_id, transaction_date, year, month, transaction_type, channel, merchant_category, amount, fee, tax, status, is_fraud, risk_score, customer_id, gender, age, **age_group** (Under 25 / 25-39 / 40-59 / 60+), state, city, occupation, customer_segment.

## KPI views
| View | Grain | Used for |
| --- | --- | --- |
| v_kpi_by_year | Year | KPI cards |
| v_yoy_growth | Year | Year-over-year growth (`LAG`) |
| v_monthly_trend | Month | Trend chart |
| v_channel_failure | Channel | Failure rate ranking |
| v_segment_share | Segment | Share of value (window total) |
| v_state_ranking | State | Ranked by value (`RANK`) |
| v_type_summary | Transaction type | Fee income |
