# Power BI and Excel setup: connect to PostgreSQL

Run the pipeline first (`python python/run_pipeline.py`). This creates the database **finance_db** with its tables and views, which you can see in pgAdmin under *Databases → finance_db → Schemas → public → Views*.

## 1. Power BI Desktop (the free version works)

The dashboard is saved as a **Power BI project** (`FInance_analysis.pbip`). It is plain text, so GitHub can show every measure and visual. Sections 3, 4 and 6 below are already built into it. From section 5 only the **reset button** still needs to be added by hand.

1. Make sure PostgreSQL is running, then double-click `FInance_analysis.pbip` in the project folder.
2. The project holds no data yet, so the visuals start empty. Click **Home → Refresh**.
3. When asked for a login: choose **Database**, user `postgres`, and your pgAdmin password. Click **Connect**.
   (If Power BI asks about encryption, click **OK** to connect without it. That is normal for `localhost`.)
4. Check both pages, then **File → Save as → `FInance_analysis.pbix`** if you also want a single file to share.

What is inside:

| Part | Contents |
| --- | --- |
| Tables | `fact_transactions` (from the view `v_fact_transactions`), `Calendar` (marked as date table), `_Measures`, `Metric Selector` (field parameter) |
| Measures | Total Amount, Total Amount (Cr), Total Transactions, Avg Transaction, Total Fees, Total Tax, Success / Failure / Pending Rate %, Fraud Transactions, Avg Risk Score, Amount / Transactions / Fees YoY % (YTD) |
| Overview page | 5 slicers (Year, Segment, Channel, Age group, Trend metric), 6 KPI cards, monthly trend, status donut, segment, channel failure, states, gender |
| Details page | 5 slicers, transaction-type matrix, transaction-level table |

**YoY % (YTD)** compares the year to date with the same days of the previous year, so the 2026 figures (January–April only) are compared like-for-like with January–April 2025.

**Alternative (new report from scratch):** paste `power_query_postgresql.m` into *Get data → Blank query → Advanced editor*.

**Refresh routine:** edit `data/raw/*.csv` → `python python/run_pipeline.py` → Power BI **Home → Refresh**.

## 2. Excel Power Query (same data, for quick checks)

**Data → Get Data → From Database → From PostgreSQL Database** → `localhost` / `finance_db` → pick a view → **Load**.
Excel can refresh it too: **Data → Refresh All**.

## 3. Calendar table (Modeling → New table)

```DAX
Calendar =
ADDCOLUMNS(
    CALENDAR(DATE(2023,1,1), DATE(2026,4,30)),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date], "MMM yyyy"),
    "MonthNo", YEAR([Date]) * 100 + MONTH([Date])
)
```
Relate `Calendar[Date]` → `v_fact_transactions[transaction_date]`. Mark it as a date table and sort `Month` by `MonthNo`.

## 4. Measures (Modeling → New measure)

```DAX
Total Amount       = SUM(v_fact_transactions[amount])
Total Transactions = COUNTROWS(v_fact_transactions)
Avg Transaction    = DIVIDE([Total Amount], [Total Transactions])
Total Fees         = SUM(v_fact_transactions[fee])
Total Tax          = SUM(v_fact_transactions[tax])

Success Rate % =
DIVIDE(CALCULATE([Total Transactions], v_fact_transactions[status] = "Success"), [Total Transactions])

Failure Rate % =
DIVIDE(CALCULATE([Total Transactions], v_fact_transactions[status] = "Failed"), [Total Transactions])

Fraud Transactions =
CALCULATE([Total Transactions], v_fact_transactions[is_fraud] = "Yes")

Amount PY    = CALCULATE([Total Amount], SAMEPERIODLASTYEAR('Calendar'[Date]))
Amount YoY % = DIVIDE([Total Amount] - [Amount PY], [Amount PY])
```

Use the same YoY pattern for Transactions, Fees and Tax. Format the % measures as Percentage.

## 5. Interactivity checklist

- Slicers: Year, Segment, Occupation, Channel, Merchant category, **age_group** (new, built in the SQL view)
- Dynamic metric: your existing field parameter (Amount / Transactions / Fees / Tax)
- **Format → Edit interactions**: set every visual to *Filter*
- Reset button: Insert → Buttons → Reset, with its action set to a bookmark saved with no filters
- **View → Page view → Fit to page**, canvas 16:9

## 6. Theme colors

`#2A78D6` `#D77A29` `#2F9E8F` `#8A5CC7` `#C8507A`, failure red `#D0453A`, success green `#2E8B57`

## If something goes wrong

| Message | Fix |
| --- | --- |
| `password authentication failed` | Use the same password you use to open the server in pgAdmin |
| `could not connect to server` | Start PostgreSQL: Windows → Services → postgresql-x64-NN → Start |
| `ModuleNotFoundError: psycopg2` | Run `pip install -r requirements.txt` |
| Power BI cannot find a PostgreSQL provider | Update Power BI Desktop to the latest version, which includes the connector |
