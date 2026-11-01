"""
STEP 03 - LOAD INTO POSTGRESQL
------------------------------
Goal: put the clean data into PostgreSQL (database finance_db, which you
can browse in pgAdmin) and create the KPI views that Power BI reads.

How the load works: PostgreSQL's COPY command reads a whole CSV file in one
go. It is the fastest way to load data, much faster than inserting row by row.

Run:  python python/step03_load_to_sql.py
"""

import csv
from config import (CLEAN_TRANSACTIONS, CLEAN_CUSTOMERS, SQL_DIR, PG_DATABASE,
                    connect, query_df, make_folders)


def create_database_if_missing():
    """Connect to the default 'postgres' database and create finance_db once."""
    conn = connect("postgres")
    conn.autocommit = True                     # CREATE DATABASE cannot run inside a transaction
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DATABASE,))
        if cur.fetchone():
            print(f"  database {PG_DATABASE} already exists")
        else:
            cur.execute(f"CREATE DATABASE {PG_DATABASE}")
            print(f"  created database {PG_DATABASE}")
    conn.close()


def run_sql_file(conn, file_name):
    """Run every statement in one .sql file."""
    sql_text = (SQL_DIR / file_name).read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql_text)
    print(f"  ran {file_name}")


def load_table(conn, csv_path, table_name):
    """COPY a clean CSV into its table, then count rows to confirm nothing was lost."""
    with open(csv_path, encoding="utf-8") as f:
        header = next(csv.reader(f))           # column names from the CSV's first row
    columns = ", ".join(header)
    with conn.cursor() as cur, open(csv_path, encoding="utf-8") as f:
        cur.copy_expert(f"COPY {table_name} ({columns}) FROM STDIN WITH (FORMAT csv, HEADER true)", f)
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
    csv_rows = sum(1 for _ in open(csv_path, encoding="utf-8")) - 1
    print(f"  {table_name}: {csv_rows:,} rows in CSV -> {count:,} rows in PostgreSQL")


if __name__ == "__main__":
    make_folders()
    print("Preparing database")
    create_database_if_missing()

    conn = connect()
    try:
        print("Creating tables")
        run_sql_file(conn, "01_create_tables.sql")

        print("Loading data")
        load_table(conn, CLEAN_CUSTOMERS, "customers")        # customers first: transactions refer to them
        load_table(conn, CLEAN_TRANSACTIONS, "transactions")

        print("Creating KPI views")
        run_sql_file(conn, "02_kpi_views.sql")
        conn.commit()                                          # save everything

        print("\nKPI by year (from view v_kpi_by_year):")
        print(query_df(conn, "SELECT * FROM v_kpi_by_year").to_string(index=False))
    except Exception:
        conn.rollback()                                        # undo a half-finished load
        raise
    finally:
        conn.close()
    print(f"\nDatabase ready: {PG_DATABASE}. Open pgAdmin -> Databases -> {PG_DATABASE} to browse it.")
