"""
config.py - All folder paths and database settings in ONE place.

Every step script imports from here, so if you move the project to
another folder or laptop, or change your PostgreSQL login, only this
file changes.
"""

import os
from getpass import getpass
from pathlib import Path

# The project folder = one level above this "python" folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Input: raw files exactly as received (never edited by code)
RAW_DIR = PROJECT_DIR / "data" / "raw"
RAW_TRANSACTIONS = RAW_DIR / "finance_transactions.csv"
RAW_CUSTOMERS = RAW_DIR / "customers.csv"

# Output of step 02: cleaned files
CLEAN_DIR = PROJECT_DIR / "data" / "clean"
CLEAN_TRANSACTIONS = CLEAN_DIR / "transactions_clean.csv"
CLEAN_CUSTOMERS = CLEAN_DIR / "customers_clean.csv"
CLEANING_LOG = CLEAN_DIR / "cleaning_log.csv"

# SQL scripts (you can also open and run them in pgAdmin)
SQL_DIR = PROJECT_DIR / "sql"

# Output of step 04: charts, and CSV copies of the views (backup for Excel)
CHART_DIR = PROJECT_DIR / "outputs" / "charts"
EXPORT_DIR = PROJECT_DIR / "outputs" / "exports"

# Business rule found in the data: tax = 18% GST on the fee
GST_RATE = 0.18

# ---------------- PostgreSQL (the same server you open in pgAdmin) ----------------
PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "finance_db"        # created automatically by step 03 if missing
PG_USER = "postgres"


def pg_password():
    """The password is never written in code (so it never reaches GitHub).
    It is read from the PG_PASSWORD environment variable, or asked once."""
    if "PG_PASSWORD" not in os.environ:
        os.environ["PG_PASSWORD"] = getpass(f"PostgreSQL password for user '{PG_USER}': ")
    return os.environ["PG_PASSWORD"]


def connect(database=PG_DATABASE):
    """Open a connection to PostgreSQL."""
    import psycopg2                        # the PostgreSQL driver for Python
    return psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=database,
                            user=PG_USER, password=pg_password())


def query_df(conn, sql):
    """Run a SELECT and return a pandas DataFrame.
    PostgreSQL NUMERIC values arrive as Decimal; we turn them into normal numbers."""
    import pandas as pd
    with conn.cursor() as cur:
        cur.execute(sql)
        columns = [col[0] for col in cur.description]
        df = pd.DataFrame(cur.fetchall(), columns=columns)
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass                            # text columns stay text
    return df


def make_folders():
    """Create output folders if they do not exist yet."""
    for folder in [CLEAN_DIR, CHART_DIR, EXPORT_DIR]:
        folder.mkdir(parents=True, exist_ok=True)
