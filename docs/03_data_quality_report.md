# 03 · Data Quality Report

## Approach
1. **Profile before changing anything** (`step01_load_and_explore.py`): row counts, types, nulls, duplicates, value lists and business-rule checks.
2. **Fix one problem per function** (`step02_clean.py`), printing before and after counts.
3. **Log every fix** to `data/clean/cleaning_log.csv`.
4. **Validate** with automatic checks; the pipeline stops if any fails.
5. **Enforce in the database**: primary keys, a foreign key and `CHECK (amount >= 0)` block bad data at load time as well.

## Profiling summary
| Check | Transactions | Customers |
| --- | --- | --- |
| Rows | 50,069 | 5,000 |
| Exact duplicate rows | **68** | 0 |
| Duplicate IDs | **69** | 0 |
| Missing values | **24** in fee_amount | 0 |
| Dirty categories | **770** channel, **605** currency | – |
| Invalid values | **9** negative amounts (8 after de-duplication) | – |
| Orphan customer IDs | 0 | – |

**Business rule discovered:** `tax ÷ fee = 0.18` on 29,206 rows, which is GST at 18%. This allowed blank fees to be rebuilt rather than dropped.

## Fixes applied
| Step | Problem | Rows | Action | Why |
| --- | --- | ---: | --- | --- |
| T1 | Exact duplicate rows | 68 | Removed | Duplicates inflated value by ₹7.46 L |
| T2 | Same ID, different rows | 1 | Kept the copy with the fee filled | Keep the most complete record |
| T3 | Dirty channel names | 770 | Trimmed, `M@bile` → `Mobile` | Mobile App appeared under 4 different labels |
| T4 | Currency case | 605 | Upper-cased | `inr` = `INR` |
| T5 | Blank fee | 23 | `fee = tax ÷ 0.18` | Uses the confirmed GST rule; no rows lost |
| T6 | Negative amount | 8 | Absolute value, flagged | Fees and tax were never negative, so the sign was an entry error |
| T7 | Text dates | 50,000 | Converted; year and month added | Enables time analysis |
| C1 | Column typo `fisrt_name` | 5,000 | Renamed | Clean schema |
| C2 | Text dates (customers) | 5,000 | Converted; age added | Enables age-group analysis |

## Impact
| Metric | Raw | Clean | Change |
| --- | ---: | ---: | ---: |
| Rows | 50,069 | 50,000 | −69 |
| Total amount | ₹45,61,41,514 | ₹45,55,34,250 | −₹6.07 L (net) |
| Distinct channels | 13 labels | 7 | Correct grouping |
| Blank fees | 24 | 0 | |

The net change of −₹6.07 L = duplicates removed (−₹7.46 L in T1, −₹0.04 L in T2) + negative amounts corrected to positive (+₹1.43 L in T6).

## Validation checks (automated)
- `transaction_id` is unique
- `fee` has no blanks
- `amount` ≥ 0
- every `customer_id` exists in customers
- row counts match after loading into PostgreSQL (CSV rows = table rows)
