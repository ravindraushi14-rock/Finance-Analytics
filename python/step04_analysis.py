"""
STEP 04 - ANALYSIS AND EXPORT FOR POWER BI
------------------------------------------
Goal:
  a) read the KPI views from PostgreSQL, print the insights, save simple charts
  b) save CSV copies of the views in outputs/exports (handy for Excel and as a backup;
     Power BI itself connects to PostgreSQL directly)

Run:  python python/step04_analysis.py
"""

import matplotlib
matplotlib.use("Agg")            # draw charts to files, no window needed
import matplotlib.pyplot as plt
from config import CHART_DIR, EXPORT_DIR, connect, query_df, make_folders

# Views to copy out as CSV (view name -> file name)
EXPORTS = {
    "v_fact_transactions": "fact_transactions.csv",
    "v_kpi_by_year": "kpi_by_year.csv",
    "v_monthly_trend": "monthly_trend.csv",
    "v_channel_failure": "channel_failure.csv",
    "v_segment_share": "segment_share.csv",
    "v_state_ranking": "state_ranking.csv",
    "v_type_summary": "type_summary.csv",
}


def read_view(conn, view):
    return query_df(conn, f"SELECT * FROM {view}")


def save_bar(df, x, y, title, file_name, horizontal=True, divide_by=1):
    """One simple bar chart saved as PNG (for the README and quick checks).
    divide_by=1e7 shows rupees in crore (1 crore = 1,00,00,000)."""
    df = df.assign(**{y: df[y] / divide_by})
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if horizontal:
        ax.barh(df[x], df[y], color="#2A78D6")
        ax.invert_yaxis()                 # biggest at the top
    else:
        ax.bar(df[x], df[y], color="#2A78D6")
        ax.tick_params(axis="x", rotation=90, labelsize=7)
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(CHART_DIR / file_name, dpi=120)
    plt.close(fig)


def print_insights(conn):
    kpi = query_df(conn, """SELECT COUNT(*) AS n, SUM(amount) AS amt, AVG(amount) AS avg_amt,
                                   SUM(fee) AS fee, SUM(tax) AS tax,
                                   100.0 * COUNT(*) FILTER (WHERE status = 'Success') / COUNT(*) AS success_pct,
                                   100.0 * COUNT(*) FILTER (WHERE status = 'Failed')  / COUNT(*) AS failed_pct
                            FROM transactions""").iloc[0]
    print("\nKEY FIGURES (after cleaning)")
    print(f"  Transactions:     {kpi.n:,.0f}")
    print(f"  Total value:      Rs {kpi.amt / 1e7:,.2f} Cr")
    print(f"  Avg transaction:  Rs {kpi.avg_amt:,.0f}")
    print(f"  Fees / Tax:       Rs {kpi.fee / 1e5:,.2f} L / Rs {kpi.tax / 1e5:,.2f} L")
    print(f"  Success / Failed: {kpi.success_pct:.1f}% / {kpi.failed_pct:.1f}%")

    ch = read_view(conn, "v_channel_failure").iloc[0]
    seg = read_view(conn, "v_segment_share").iloc[0]
    states = read_view(conn, "v_state_ranking").sort_values("state_rank").head(3)["state"].tolist()
    types = read_view(conn, "v_type_summary").head(2)["transaction_type"].tolist()
    print("\nINSIGHTS")
    print(f"  Worst channel: {ch.channel} fails {ch.failure_rate_pct}% of the time")
    print(f"  Top segment:   {seg.customer_segment} = {seg.share_pct}% of value")
    print(f"  Top states:    {', '.join(states)}")
    print(f"  Top fee types: {' and '.join(types)}")


if __name__ == "__main__":
    make_folders()
    conn = connect()
    try:
        # a) charts
        save_bar(read_view(conn, "v_channel_failure"), "channel", "failure_rate_pct",
                 "Failure rate by channel (%)", "channel_failure.png")
        save_bar(read_view(conn, "v_segment_share"), "customer_segment", "share_pct",
                 "Share of value by customer segment (%)", "segment_share.png")
        save_bar(read_view(conn, "v_state_ranking").head(10), "state", "total_amount",
                 "Top 10 states by value (Rs Crore)", "top_states.png", divide_by=1e7)
        save_bar(read_view(conn, "v_monthly_trend"), "month", "total_amount",
                 "Monthly transaction value (Rs Crore)", "monthly_trend.png",
                 horizontal=False, divide_by=1e7)
        print(f"Charts saved in {CHART_DIR}")

        # b) CSV copies of the views
        for view, file_name in EXPORTS.items():
            df = read_view(conn, view)
            df.to_csv(EXPORT_DIR / file_name, index=False)
            print(f"  exported {view:22} -> outputs/exports/{file_name} ({len(df):,} rows)")

        print_insights(conn)
    finally:
        conn.close()
