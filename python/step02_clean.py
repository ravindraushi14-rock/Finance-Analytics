"""
STEP 02 - CLEAN AND FIX
-----------------------
Goal: fix every problem found in step 01, one small function per problem.
Each fix prints a BEFORE -> AFTER count and is written to cleaning_log.csv,
so you can always prove what was changed and why.

Run:  python python/step02_clean.py
"""

import numpy as np
import pandas as pd
from config import (CLEAN_TRANSACTIONS, CLEAN_CUSTOMERS, CLEANING_LOG,
                    GST_RATE, make_folders)
from step01_load_and_explore import load_raw

log = []  # every fix adds one line here


def record(step, problem, rows_affected, action):
    """Print a fix and keep it for the cleaning log."""
    print(f"  [{step}] {problem}: {rows_affected:,} rows -> {action}")
    log.append({"step": step, "problem": problem,
                "rows_affected": int(rows_affected), "action": action})


# ---------------- TRANSACTIONS ----------------

def fix_exact_duplicates(t):
    """Fix 1: the same row typed twice inflates totals. Keep one copy."""
    before = len(t)
    t = t.drop_duplicates()
    record("T1", "Exact duplicate rows", before - len(t), "removed, kept first copy")
    return t


def fix_duplicate_ids(t):
    """Fix 2: same transaction_id twice but not identical (one copy has a blank fee).
    Keep the most complete copy: sort so rows WITH a fee come first, then keep first."""
    before = len(t)
    t = (t.assign(_fee_missing=t["fee_amount"].isna())
           .sort_values(["transaction_id", "_fee_missing"])
           .drop_duplicates(subset="transaction_id", keep="first")
           .drop(columns="_fee_missing"))
    record("T2", "Same ID, different rows", before - len(t), "kept the copy with the fee filled")
    return t


def fix_channel_names(t):
    """Fix 3: 'M@bile App' and names with extra spaces split one channel into many bars."""
    before = t["channel"].copy()
    t["channel"] = (t["channel"].str.strip()                       # remove spaces at both ends
                                .str.replace("M@bile", "Mobile", regex=False))
    record("T3", "Dirty channel names", (before != t["channel"]).sum(),
           "trimmed spaces, 'M@bile App' -> 'Mobile App'")
    return t


def fix_currency_case(t):
    """Fix 4: 'inr', 'inR' and 'INR' are the same currency."""
    before = t["currency"].copy()
    t["currency"] = t["currency"].str.upper()
    record("T4", "Currency in mixed case", (before != t["currency"]).sum(), "made upper case")
    return t


def fix_blank_fees(t):
    """Fix 5: fee is blank but tax is known. Rule from the data: tax = 18% GST of fee,
    so fee = tax / 0.18. If tax is 0, the fee was 0."""
    blank = t["fee_amount"].isna()
    t.loc[blank, "fee_amount"] = (t.loc[blank, "tax_amount"] / GST_RATE).round(2)
    record("T5", "Blank fee_amount", blank.sum(), "rebuilt as tax / 18% GST")
    return t


def fix_negative_amounts(t):
    """Fix 6: a negative amount is a sign-entry error (its fee and tax are positive).
    Make it positive, and keep a flag column so the fix stays visible."""
    negative = t["amount"] < 0
    t["amount_was_negative"] = np.where(negative, "Yes", "No")
    t.loc[negative, "amount"] = t.loc[negative, "amount"].abs()
    record("T6", "Negative amounts", negative.sum(), "made positive, flagged in amount_was_negative")
    return t


def fix_dates(t):
    """Fix 7: text '21-02-2025' -> real date, plus year and month columns for reports."""
    t["transaction_date"] = pd.to_datetime(t["transaction_date"], format="%d-%m-%Y")
    t["year"] = t["transaction_date"].dt.year
    t["month"] = t["transaction_date"].dt.strftime("%Y-%m")
    record("T7", "Dates stored as text", len(t), "converted to dates, added year and month")
    return t


def clean_transactions(t):
    print("\nCleaning TRANSACTIONS")
    print(f"  Start: {len(t):,} rows, total amount Rs {t['amount'].sum():,.2f}")
    t = fix_exact_duplicates(t)
    t = fix_duplicate_ids(t)
    t = fix_channel_names(t)
    t = fix_currency_case(t)
    t = fix_blank_fees(t)
    t = fix_negative_amounts(t)
    t = fix_dates(t)
    t = t.rename(columns={"fee_amount": "fee", "tax_amount": "tax",
                          "transaction_status": "status"})
    print(f"  End:   {len(t):,} rows, total amount Rs {t['amount'].sum():,.2f}")
    return t


# ---------------- CUSTOMERS ----------------

def clean_customers(c):
    print("\nCleaning CUSTOMERS")
    # Fix C1: typo in the column name
    c = c.rename(columns={"fisrt_name": "first_name", "second_name": "last_name"})
    record("C1", "Column name typo 'fisrt_name'", len(c), "renamed to first_name / last_name")

    # Fix C2: text dates -> real dates, then age (useful for age-group analysis)
    c["date_of_birth"] = pd.to_datetime(c["date_of_birth"], format="%d-%m-%Y")
    c["join_date"] = pd.to_datetime(c["join_date"], format="%d-%m-%Y")
    c["age"] = ((pd.Timestamp("2026-04-30") - c["date_of_birth"]).dt.days // 365).astype(int)
    record("C2", "Dates stored as text", len(c), "converted; age calculated at 30-Apr-2026")
    return c


def check_result(t, c):
    """Final checks: if any of these fail, the pipeline stops with a clear message."""
    assert t["transaction_id"].is_unique, "transaction_id still has duplicates"
    assert t["fee"].notna().all(), "fee still has blanks"
    assert (t["amount"] >= 0).all(), "negative amounts remain"
    assert t["customer_id"].isin(c["customer_id"]).all(), "unknown customer_id found"
    print("\nAll checks passed.")


if __name__ == "__main__":
    make_folders()
    transactions, customers = load_raw()
    transactions = clean_transactions(transactions)
    customers = clean_customers(customers)
    check_result(transactions, customers)

    transactions.to_csv(CLEAN_TRANSACTIONS, index=False)
    customers.to_csv(CLEAN_CUSTOMERS, index=False)
    pd.DataFrame(log).to_csv(CLEANING_LOG, index=False)
    print(f"Saved: {CLEAN_TRANSACTIONS.name}, {CLEAN_CUSTOMERS.name}, {CLEANING_LOG.name}")
