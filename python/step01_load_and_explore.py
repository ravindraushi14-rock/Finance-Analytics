"""
STEP 01 - LOAD AND EXPLORE
--------------------------
Goal: look at the raw data BEFORE changing anything, and list its problems.
A data analyst never cleans blind: first measure, then fix.

Run:  python python/step01_load_and_explore.py
"""

import pandas as pd
from config import RAW_TRANSACTIONS, RAW_CUSTOMERS


def load_raw():
    """Read both raw CSV files into pandas DataFrames (tables in memory)."""
    transactions = pd.read_csv(RAW_TRANSACTIONS)
    customers = pd.read_csv(RAW_CUSTOMERS)
    return transactions, customers


def profile(df, name):
    """Print a quick health check of one table."""
    print(f"\n========== {name} ==========")
    print(f"Rows: {len(df):,}   Columns: {df.shape[1]}")
    print("\nColumn names and types:")
    print(df.dtypes.to_string())

    # Missing values per column (only columns that have some)
    nulls = df.isna().sum()
    print("\nMissing values:", nulls[nulls > 0].to_dict() or "none")

    # Exact duplicate rows = the same row typed twice
    print("Exact duplicate rows:", df.duplicated().sum())


def find_problems(t):
    """Check the transactions table for the specific problems we expect."""
    print("\n========== PROBLEMS FOUND IN TRANSACTIONS ==========")

    # 1. Duplicate transaction IDs (an ID must be unique)
    print("1. Duplicate transaction IDs:", t["transaction_id"].duplicated().sum())

    # 2. Channel names: spelling and spaces
    print("2. Channel values as typed:")
    print(t["channel"].value_counts().to_string())

    # 3. Currency written in different cases
    print("3. Currency values:", t["currency"].value_counts().to_dict())

    # 4. Missing fees
    print("4. Blank fee_amount:", t["fee_amount"].isna().sum())

    # 5. Negative amounts (a transaction value cannot be below zero)
    print("5. Negative amounts:", (t["amount"] < 0).sum())

    # 6. Business rule check: tax should be 18% of fee
    has_fee = t["fee_amount"] > 0
    ratio = (t.loc[has_fee, "tax_amount"] / t.loc[has_fee, "fee_amount"]).round(2)
    print("6. tax / fee ratio (most common):", ratio.value_counts().head(3).to_dict())

    # 7. Dates are stored as text like '21-02-2025'
    print("7. Date column type:", t["transaction_date"].dtype, "e.g.", t["transaction_date"].iloc[0])


if __name__ == "__main__":
    transactions, customers = load_raw()
    profile(transactions, "TRANSACTIONS (raw)")
    profile(customers, "CUSTOMERS (raw)")
    find_problems(transactions)
    print("\nCustomer columns:", list(customers.columns), "<- note the typo 'fisrt_name'")
