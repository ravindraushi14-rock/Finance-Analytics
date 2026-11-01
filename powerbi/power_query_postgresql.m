// =====================================================================
// Power Query (M): read the clean fact view straight from PostgreSQL
// Works in Power BI Desktop AND in Excel (Data -> Get Data -> Blank Query).
// ---------------------------------------------------------------------
// HOW TO USE
// 1. Home -> Get data -> Blank query -> Advanced editor -> paste -> Done
// 2. Rename the query: fact_transactions
// 3. First time only: Power BI asks for a login -> choose "Database",
//    user: postgres, password: your pgAdmin password
//
// After you re-run the Python pipeline, just click Home -> Refresh.
// =====================================================================
let
    // Connect to the same server you open in pgAdmin
    Source = PostgreSQL.Database("localhost", "finance_db"),

    // Pick the view (schema "public", view name)
    Fact = Source{[Schema = "public", Item = "v_fact_transactions"]}[Data],

    // PostgreSQL already sends the right data types (date, numbers, text),
    // so only one small Power Query step is needed: a Year-Month label for visuals
    AddMonthName = Table.AddColumn(Fact, "month_name",
        each Date.ToText([transaction_date], "MMM yyyy"), type text)
in
    AddMonthName
