-- =====================================================================
-- 01_create_tables.sql   (PostgreSQL)
-- Creates the two clean tables in database finance_db.
-- Run by python/step03_load_to_sql.py, or open it in pgAdmin's Query Tool.
-- Re-running is safe: old tables (and the views built on them) are dropped first.
-- =====================================================================

DROP TABLE IF EXISTS transactions CASCADE;   -- CASCADE also drops views that use it
DROP TABLE IF EXISTS customers CASCADE;

-- One row per customer
CREATE TABLE customers (
    customer_id       VARCHAR(10) PRIMARY KEY,   -- e.g. C00001
    first_name        VARCHAR(50),
    last_name         VARCHAR(50),
    gender            VARCHAR(10),
    date_of_birth     DATE,
    age               INTEGER,
    city              VARCHAR(50),
    state             VARCHAR(50),
    occupation        VARCHAR(50),
    customer_segment  VARCHAR(20),               -- Retail, Premium, SME, Corporate, Wealth
    annual_income     NUMERIC(14, 2),
    join_date         DATE
);

-- One row per transaction
CREATE TABLE transactions (
    transaction_id       VARCHAR(12) PRIMARY KEY,  -- unique after cleaning
    transaction_date     DATE NOT NULL,
    year                 INTEGER,
    month                CHAR(7),                  -- 'YYYY-MM'
    account_id           VARCHAR(10),
    customer_id          VARCHAR(10) NOT NULL REFERENCES customers (customer_id),
    transaction_type     VARCHAR(30),
    channel              VARCHAR(30),
    merchant_category    VARCHAR(30),
    amount               NUMERIC(14, 2) CHECK (amount >= 0),   -- the database itself blocks negatives
    fee                  NUMERIC(12, 2),
    tax                  NUMERIC(12, 2),
    currency             CHAR(3),
    status               VARCHAR(10),              -- Success, Failed, Pending
    is_fraud             VARCHAR(3),               -- Yes / No
    risk_score           INTEGER,
    reference_no         VARCHAR(20),
    amount_was_negative  VARCHAR(3)                -- Yes = fixed during cleaning
);

-- Indexes make filters and joins on these columns fast
CREATE INDEX idx_tx_customer ON transactions (customer_id);
CREATE INDEX idx_tx_date     ON transactions (transaction_date);
