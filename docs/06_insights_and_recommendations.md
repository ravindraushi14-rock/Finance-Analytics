# 06 · Insights and Recommendations

All figures come from the cleaned data (50,000 transactions, Jan 2023 – Apr 2026).

## 1. Headline performance
| KPI | Value |
| --- | --- |
| Total value | **₹45.55 Cr** |
| Transactions | **50,000** |
| Average transaction | **₹9,111** |
| Fees · Tax (GST) | **₹7.26 L** · **₹1.31 L** |
| Success · Failed · Pending | **85.7%** · **10.2%** · **4.1%** |

**Year by year**
| Year | Value (₹ Cr) | Transactions | Success rate | Failure rate |
| --- | ---: | ---: | ---: | ---: |
| 2023 | 13.71 | 15,034 | 85.72% | 10.26% |
| 2024 | 13.56 | 15,029 | 85.47% | 10.33% |
| 2025 | 13.75 | 14,944 | 85.85% | 10.13% |
| 2026 (Jan–Apr) | 4.53 | 4,993 | 86.26% | 9.75% |

The business is **stable**: value moved −1.1% in 2024 and +1.4% in 2025. The failure rate is slowly improving (10.3% → 9.8%).

## 2. Failures cost real value
- Failed transactions represent **₹4.75 Cr** of value, and pending ones another **₹1.91 Cr**.
- **By channel:** ATM 10.86% · Auto Debit 10.80% · POS 10.23% · Branch 10.11% · Mobile App 9.90% · UPI 9.86% · Net Banking 9.59%.
- **Worst combinations:** Auto Debit × Salary (13.7%), ATM × Insurance (13.6%), POS × Rent (12.8%).
- **By merchant category:** Utilities (10.9%), Travel (10.8%) and Mutual Fund (10.6%) fail most.

## 3. Customers and regions
| Segment | Share of value |
| --- | ---: |
| Retail | 54.5% |
| Premium | 18.5% |
| SME | 15.8% |
| Corporate | 6.8% |
| Wealth | 4.5% |

- **Top states:** Maharashtra ₹6.83 Cr (15.0%), Karnataka ₹5.29 Cr (11.6%), Gujarat ₹5.01 Cr (11.0%).
- **Age:** the 40–59 group transacts the most (₹20.67 Cr), then 25–39 (₹14.72 Cr).
- **Gender:** balanced, with women at 51.7% and men at 48.3% of value.

## 4. Fee income is concentrated
Loan EMI (₹2.05 L, 28.2%) and Transfers (₹1.93 L, 26.6%) generate **over half of all fees**. Fee Charge transactions bring only ₹2,897.

## 5. The risk score works
| | Transactions | Avg risk score |
| --- | ---: | ---: |
| Fraud | 630 | **82.9** |
| Normal | 49,370 | **35.5** |

A threshold of **risk score ≥ 70** flags 1,212 transactions (2.4%) and catches **535 of 630 fraud cases (85%)**.

## Recommendations
| # | Action | Expected benefit | Owner |
| --- | --- | --- | --- |
| 1 | Investigate ATM and Auto Debit failures first, starting with the worst merchant combinations | Each 1-point drop in failure rate protects about ₹45 L of value | Operations |
| 2 | Turn on a risk-score alert at ≥ 70 | Review 2.4% of transactions and catch 85% of fraud | Risk |
| 3 | Run retention offers for Retail customers | Protects 54.5% of value | Marketing |
| 4 | Review Loan EMI and Transfer pricing | These two products drive 55% of fee income | Product |
| 5 | Follow up pending transactions within 48 hours | ₹1.91 Cr is waiting to be completed | Operations |

## Next steps
- Build a fraud prediction model in Python (logistic regression on risk score, channel, amount).
- Schedule the pipeline to run daily and publish the report to the Power BI Service.
