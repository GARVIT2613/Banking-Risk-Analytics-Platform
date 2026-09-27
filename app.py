"""
Banking Risk Analytics Platform
Portfolio Securitisation & Credit Risk Monitoring Dashboard
Streamlit + Plotly replica of a Power BI banking risk analytics report.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

# --------------------------------------------------------------------------------------
# PAGE CONFIG & THEME
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Banking Risk Analytics Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY_DARK = "#0F1B2D"
PANEL = "#16223A"
ACCENT = "#3E8EDE"
GREEN = "#2ECC71"
AMBER = "#F5A623"
RED = "#E74C3C"
MUTED = "#8FA3BF"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {PRIMARY_DARK};
        color: #E6EDF7;
    }}
    div[data-testid="stMetric"] {{
        background-color: {PANEL};
        border: 1px solid #24314C;
        border-radius: 10px;
        padding: 14px 16px 10px 16px;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {MUTED};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {PANEL};
    }}
    .block-container {{
        padding-top: 1.4rem;
    }}
    h1, h2, h3 {{
        color: #E6EDF7;
    }}
    .card-note {{
        background-color: {PANEL};
        border: 1px solid #24314C;
        border-radius: 10px;
        padding: 10px 14px;
        color: {MUTED};
        font-size: 0.85rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

PLOTLY_TEMPLATE = "plotly_dark"

# --------------------------------------------------------------------------------------
# REGULATORY BASELINE FACTORS (used when explicit PD/LGD are not supplied)
# --------------------------------------------------------------------------------------
RISK_RATING_ORDER = ["AAA", "AA", "A", "BBB", "BB", "B", "Substandard"]

PD_BASELINE = {
    "AAA": 0.0005, "AA": 0.0015, "A": 0.004, "BBB": 0.012,
    "BB": 0.035, "B": 0.09, "Substandard": 0.25,
}
LGD_BASELINE = {
    "AAA": 0.20, "AA": 0.22, "A": 0.25, "BBB": 0.30,
    "BB": 0.35, "B": 0.45, "Substandard": 0.60,
}

DPD_BUCKET_ORDER = ["Current", "30-59 DPD", "60-89 DPD", "90+ DPD / Default", "Prepaid", "Closed"]


# --------------------------------------------------------------------------------------
# MOCK DATA GENERATOR
# --------------------------------------------------------------------------------------
def generate_mock_banking_data(n_loans: int = 1500, n_customers: int = 900, seed: int = 42):
    """Generates a realistic synthetic FactLoans + DimCustomers + DimCalendar dataset
    matching the schema of the target Power BI model, so the app runs standalone
    with zero external data dependencies."""
    rng = np.random.default_rng(seed)

    regions = ["North", "South", "East", "West", "Central"]
    segments = ["Retail", "HNI", "Corporate", "Micro-Enterprise"]
    loan_types = ["Auto Loan", "Mortgage", "Personal Loan", "SME Commercial"]
    tranches = ["Senior (AAA)", "Mezzanine (BBB)", "Junior / Equity", "Unassigned"]

    # ---- DimCustomers ----
    customer_ids = [f"CUST-{i:05d}" for i in range(1, n_customers + 1)]
    dim_customers = pd.DataFrame({
        "CustomerID": customer_ids,
        "CustomerSegment": rng.choice(segments, n_customers, p=[0.55, 0.15, 0.20, 0.10]),
        "Region": rng.choice(regions, n_customers),
        "CreditBureauScore": rng.integers(300, 851, n_customers),
    })

    # ---- DimCalendar ----
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2025, 12, 31)
    calendar_dates = pd.date_range(start_date, end_date, freq="D")
    dim_calendar = pd.DataFrame({"Date": calendar_dates})
    dim_calendar["Year"] = dim_calendar["Date"].dt.year
    dim_calendar["Quarter"] = dim_calendar["Date"].dt.quarter
    dim_calendar["Month"] = dim_calendar["Date"].dt.month
    dim_calendar["YearMonth"] = dim_calendar["Date"].dt.to_period("M").astype(str)

    # ---- FactLoans ----
    loan_ids = [f"LN-{i:06d}" for i in range(1, n_loans + 1)]
    cust_choice = rng.choice(customer_ids, n_loans)
    origination_offsets = rng.integers(0, (end_date - start_date).days - 30, n_loans)
    origination_dates = [start_date + timedelta(days=int(d)) for d in origination_offsets]

    loan_type_choice = rng.choice(loan_types, n_loans, p=[0.35, 0.25, 0.25, 0.15])

    disbursed_amount = np.where(
        loan_type_choice == "Mortgage", rng.uniform(80_000, 500_000, n_loans),
        np.where(loan_type_choice == "SME Commercial", rng.uniform(50_000, 400_000, n_loans),
                 np.where(loan_type_choice == "Auto Loan", rng.uniform(8_000, 60_000, n_loans),
                          rng.uniform(2_000, 30_000, n_loans)))
    )

    risk_rating = rng.choice(RISK_RATING_ORDER, n_loans, p=[0.05, 0.10, 0.20, 0.25, 0.20, 0.13, 0.07])

    # DPD skewed toward lower delinquency, correlated loosely with risk rating
    rating_dpd_skew = {"AAA": 0, "AA": 1, "A": 3, "BBB": 8, "BB": 20, "B": 45, "Substandard": 95}
    base_dpd = rng.exponential(scale=6.0, size=n_loans)
    skew = np.array([rating_dpd_skew[r] for r in risk_rating])
    dpd = np.clip((base_dpd + skew * rng.uniform(0.3, 1.2, n_loans)).astype(int), 0, 210)

    def dpd_to_status(d):
        if d == 0:
            return "Current"
        elif d < 30:
            return "Current"
        elif d < 60:
            return "30-59 DPD"
        elif d < 90:
            return "60-89 DPD"
        else:
            return "90+ DPD / Default"

    loan_status = np.array([dpd_to_status(d) for d in dpd])

    # Sprinkle in some Prepaid / Closed loans, independent of DPD economics
    lifecycle_roll = rng.random(n_loans)
    loan_status = np.where(lifecycle_roll < 0.06, "Prepaid",
                            np.where((lifecycle_roll >= 0.06) & (lifecycle_roll < 0.14), "Closed", loan_status))

    # Outstanding balance: amortized fraction of disbursed amount based on loan age, plus payoff at Closed/Prepaid
    months_on_book = np.array([
        max(1, (end_date.year - d.year) * 12 + (end_date.month - d.month)) for d in origination_dates
    ])
    amort_fraction = np.clip(1 - (months_on_book / rng.uniform(48, 84, n_loans)), 0.02, 0.98)
    outstanding_balance = disbursed_amount * amort_fraction
    outstanding_balance = np.where(np.isin(loan_status, ["Prepaid", "Closed"]),
                                    outstanding_balance * rng.uniform(0.0, 0.05, n_loans),
                                    outstanding_balance)

    interest_rate = np.where(
        loan_type_choice == "Mortgage", rng.uniform(6.5, 9.5, n_loans),
        np.where(loan_type_choice == "SME Commercial", rng.uniform(9.0, 14.0, n_loans),
                 np.where(loan_type_choice == "Auto Loan", rng.uniform(7.5, 12.5, n_loans),
                          rng.uniform(11.0, 18.0, n_loans)))
    )

    tranche_choice = rng.choice(tranches, n_loans, p=[0.45, 0.30, 0.15, 0.10])

    fact_loans = pd.DataFrame({
        "LoanID": loan_ids,
        "CustomerID": cust_choice,
        "DisbursedAmount": np.round(disbursed_amount, 2),
        "OutstandingBalance": np.round(outstanding_balance, 2),
        "InterestRate": np.round(interest_rate, 2),
        "DPD": dpd,
        "LoanStatus": loan_status,
        "RiskRating": risk_rating,
        "LoanType": loan_type_choice,
        "OriginationDate": origination_dates,
        "SecuritisationTranche": tranche_choice,
    })

    fact_loans["OriginationDate"] = pd.to_datetime(fact_loans["OriginationDate"])

    # Regulatory baseline PD / LGD by RiskRating -> Expected Loss
    fact_loans["PD"] = fact_loans["RiskRating"].map(PD_BASELINE)
    fact_loans["LGD"] = fact_loans["RiskRating"].map(LGD_BASELINE)
    fact_loans["ExpectedLoss"] = fact_loans["OutstandingBalance"] * fact_loans["PD"] * fact_loans["LGD"]

    return fact_loans, dim_customers, dim_calendar


@st.cache_data(show_spinner=False)
def load_data():
    fact_loans, dim_customers, dim_calendar = generate_mock_banking_data()
    df = fact_loans.merge(dim_customers, on="CustomerID", how="left")
    return df


# --------------------------------------------------------------------------------------
# METRIC CALCULATIONS
# --------------------------------------------------------------------------------------
def compute_kpis(df: pd.DataFrame) -> dict:
    total_balance = df["OutstandingBalance"].sum()
    total_disbursed = df["DisbursedAmount"].sum()
    gross_npl = df.loc[df["DPD"] >= 90, "OutstandingBalance"].sum()
    gross_npl_ratio = (gross_npl / total_balance * 100) if total_balance > 0 else 0.0

    wair_numerator = (df["OutstandingBalance"] * df["InterestRate"]).sum()
    wair = (wair_numerator / total_balance) if total_balance > 0 else 0.0

    avg_bureau_score = df["CreditBureauScore"].mean() if len(df) else 0.0
    total_expected_loss = df["ExpectedLoss"].sum()
    active_loans = df.loc[~df["LoanStatus"].isin(["Prepaid", "Closed"])].shape[0]

    return {
        "total_balance": total_balance,
        "total_disbursed": total_disbursed,
        "gross_npl": gross_npl,
        "gross_npl_ratio": gross_npl_ratio,
        "wair": wair,
        "avg_bureau_score": avg_bureau_score,
        "total_expected_loss": total_expected_loss,
        "active_loans": active_loans,
        "loan_count": df.shape[0],
    }


def npl_risk_color(ratio: float) -> str:
    if ratio < 2:
        return GREEN
    elif ratio <= 5:
        return AMBER
    else:
        return RED


def fmt_money(x: float) -> str:
    if abs(x) >= 1_000_000_000:
        return f"${x/1_000_000_000:,.2f}B"
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:,.2f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:,.1f}K"
    return f"${x:,.0f}"


# --------------------------------------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------------------------------------
raw_df = load_data()

# --------------------------------------------------------------------------------------
# SIDEBAR — SLICERS / FILTERS
# --------------------------------------------------------------------------------------
st.sidebar.markdown("## 🏦 Filters")
st.sidebar.caption("Portfolio Securitisation & Credit Risk Monitoring")

min_date = raw_df["OriginationDate"].min().date()
max_date = raw_df["OriginationDate"].max().date()

date_range = st.sidebar.slider(
    "Origination Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD",
)

region_options = sorted(raw_df["Region"].unique().tolist())
selected_regions = st.sidebar.multiselect("Region", options=region_options, default=region_options)

loan_type_options = sorted(raw_df["LoanType"].unique().tolist())
selected_loan_types = st.sidebar.multiselect("Loan Type", options=loan_type_options, default=loan_type_options)

tranche_options = sorted(raw_df["SecuritisationTranche"].unique().tolist())
selected_tranches = st.sidebar.multiselect(
    "Securitisation Tranche", options=tranche_options, default=tranche_options
)

risk_rating_options = ["All"] + [r for r in RISK_RATING_ORDER if r in raw_df["RiskRating"].unique()]
selected_risk_rating = st.sidebar.radio("Risk Rating Tier", options=risk_rating_options, index=0)

st.sidebar.divider()
st.sidebar.caption(f"Loans in mock dataset: **{raw_df.shape[0]:,}**")
st.sidebar.caption(f"Customers: **{raw_df['CustomerID'].nunique():,}**")

# --------------------------------------------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------------------------------------------
mask = (
    (raw_df["OriginationDate"].dt.date >= date_range[0])
    & (raw_df["OriginationDate"].dt.date <= date_range[1])
    & (raw_df["Region"].isin(selected_regions))
    & (raw_df["LoanType"].isin(selected_loan_types))
    & (raw_df["SecuritisationTranche"].isin(selected_tranches))
)
if selected_risk_rating != "All":
    mask &= raw_df["RiskRating"] == selected_risk_rating

df = raw_df.loc[mask].copy()

if df.empty:
    st.warning("No loans match the selected filters. Adjust the sidebar filters to see data.")
    st.stop()

# --------------------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------------------
st.title("🏦 Banking Risk Analytics Platform")
st.caption("Portfolio Securitisation & Credit Risk Monitoring — replicated from the Power BI report")

kpis = compute_kpis(df)

# --------------------------------------------------------------------------------------
# TOP ROW — KPI SCORECARDS
# --------------------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Outstanding Balance", fmt_money(kpis["total_balance"]))

with c2:
    ratio_color = npl_risk_color(kpis["gross_npl_ratio"])
    st.metric("Gross NPL Ratio", f"{kpis['gross_npl_ratio']:.2f}%")
    st.markdown(
        f"<div style='height:6px;border-radius:4px;background:{ratio_color};margin-top:-8px;'></div>",
        unsafe_allow_html=True,
    )

with c3:
    st.metric("Total Active Facilities", f"{kpis['active_loans']:,}", help=f"Total loans in dataset: {kpis['loan_count']:,}")

with c4:
    st.metric("Weighted Avg. Interest Rate", f"{kpis['wair']:.2f}%")

c5, c6, c7 = st.columns(3)
with c5:
    st.metric("Total Disbursed Capital", fmt_money(kpis["total_disbursed"]))
with c6:
    st.metric("Total Expected Loss (EL)", fmt_money(kpis["total_expected_loss"]))
with c7:
    st.metric("Average Bureau Score", f"{kpis['avg_bureau_score']:.0f}")

st.divider()

# --------------------------------------------------------------------------------------
# TABS
# --------------------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["📉 Credit Risk & Asset Quality", "🏛️ Securitisation & Tranche Analytics", "📋 Detailed Portfolio Records"]
)

# ============================ TAB 1 ============================
with tab1:
    col_a, col_b = st.columns(2)

    # ---- 1A: Portfolio Aging & Delinquency Breakdown ----
    with col_a:
        st.subheader("Portfolio Aging & Delinquency Breakdown")
        aging = (
            df.groupby(["LoanType", "LoanStatus"])["OutstandingBalance"]
            .sum()
            .reset_index()
        )
        present_statuses = [s for s in DPD_BUCKET_ORDER if s in aging["LoanStatus"].unique()]
        fig_1a = px.bar(
            aging,
            x="LoanType",
            y="OutstandingBalance",
            color="LoanStatus",
            category_orders={"LoanStatus": present_statuses},
            template=PLOTLY_TEMPLATE,
            color_discrete_map={
                "Current": GREEN,
                "30-59 DPD": AMBER,
                "60-89 DPD": "#E67E22",
                "90+ DPD / Default": RED,
                "Prepaid": "#5D6D7E",
                "Closed": "#34495E",
            },
            labels={"OutstandingBalance": "Outstanding Balance"},
        )
        fig_1a.update_layout(barmode="stack", legend_title_text="DPD Bucket", height=420)
        st.plotly_chart(fig_1a, use_container_width=True)

    # ---- 1C: Risk Rating vs Bureau Score ----
    with col_b:
        st.subheader("Risk Rating vs. Bureau Score Distribution")
        fig_1c = px.box(
            df,
            x="RiskRating",
            y="CreditBureauScore",
            category_orders={"RiskRating": [r for r in RISK_RATING_ORDER if r in df["RiskRating"].unique()]},
            color="RiskRating",
            template=PLOTLY_TEMPLATE,
            points="outliers",
        )
        fig_1c.update_layout(showlegend=False, height=420)
        st.plotly_chart(fig_1c, use_container_width=True)

    # ---- 1B: NPL Trend Over Time ----
    st.subheader("NPL Trend Over Time")
    df["YearMonth"] = df["OriginationDate"].dt.to_period("M").astype(str)
    monthly = df.groupby("YearMonth").apply(
        lambda g: pd.Series({
            "TotalBalance": g["OutstandingBalance"].sum(),
            "NPLBalance": g.loc[g["DPD"] >= 90, "OutstandingBalance"].sum(),
        })
    ).reset_index()
    monthly["NPLRatio"] = np.where(
        monthly["TotalBalance"] > 0, monthly["NPLBalance"] / monthly["TotalBalance"] * 100, 0
    )
    monthly = monthly.sort_values("YearMonth")

    fig_1b = go.Figure()
    fig_1b.add_trace(go.Bar(
        x=monthly["YearMonth"], y=monthly["TotalBalance"], name="Total Balance",
        marker_color=ACCENT, opacity=0.55, yaxis="y1",
    ))
    fig_1b.add_trace(go.Scatter(
        x=monthly["YearMonth"], y=monthly["NPLRatio"], name="NPL %",
        mode="lines+markers", line=dict(color=RED, width=3), yaxis="y2",
    ))
    fig_1b.update_layout(
        template=PLOTLY_TEMPLATE,
        height=420,
        yaxis=dict(title="Total Balance"),
        yaxis2=dict(title="NPL %", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Origination Month"),
    )
    st.plotly_chart(fig_1b, use_container_width=True)

# ============================ TAB 2 ============================
with tab2:
    col_c, col_d = st.columns(2)

    # ---- 2A: Outstanding Balance by Tranche ----
    with col_c:
        st.subheader("Outstanding Balance by Securitisation Tranche")
        tranche_bal = df.groupby("SecuritisationTranche")["OutstandingBalance"].sum().reset_index()
        fig_2a = px.pie(
            tranche_bal,
            names="SecuritisationTranche",
            values="OutstandingBalance",
            hole=0.5,
            template=PLOTLY_TEMPLATE,
            color="SecuritisationTranche",
            color_discrete_map={
                "Senior (AAA)": GREEN,
                "Mezzanine (BBB)": AMBER,
                "Junior / Equity": RED,
                "Unassigned": MUTED,
            },
        )
        fig_2a.update_traces(textinfo="percent+label")
        fig_2a.update_layout(height=440)
        st.plotly_chart(fig_2a, use_container_width=True)

    # ---- 2B: Loss Absorption & Risk Exposure across Segments ----
    with col_d:
        st.subheader("Loss Absorption & Risk Exposure by Customer Segment")
        seg = df.groupby(["CustomerSegment", "SecuritisationTranche"]).agg(
            ExpectedLoss=("ExpectedLoss", "sum"),
            OutstandingBalance=("OutstandingBalance", "sum"),
        ).reset_index()
        fig_2b = px.bar(
            seg,
            x="CustomerSegment",
            y="ExpectedLoss",
            color="SecuritisationTranche",
            barmode="group",
            template=PLOTLY_TEMPLATE,
            color_discrete_map={
                "Senior (AAA)": GREEN,
                "Mezzanine (BBB)": AMBER,
                "Junior / Equity": RED,
                "Unassigned": MUTED,
            },
            labels={"ExpectedLoss": "Expected Loss"},
        )
        fig_2b.update_layout(height=440, legend_title_text="Tranche")
        st.plotly_chart(fig_2b, use_container_width=True)

    st.markdown(
        f"<div class='card-note'>Expected Loss = Outstanding Balance × Probability of Default × LGD, "
        f"using regulatory baseline PD/LGD factors mapped from RiskRating (AAA → Substandard).</div>",
        unsafe_allow_html=True,
    )

# ============================ TAB 3 ============================
with tab3:
    st.subheader("Detailed Portfolio Records")

    search_term = st.text_input("Search (LoanID, CustomerID, Region, LoanType, RiskRating)", "")

    display_df = df.copy()
    if search_term:
        term = search_term.lower()
        search_cols = ["LoanID", "CustomerID", "Region", "LoanType", "RiskRating", "SecuritisationTranche", "LoanStatus"]
        combined = display_df[search_cols].astype(str).apply(lambda col: col.str.lower())
        row_mask = combined.apply(lambda row: row.str.contains(term).any(), axis=1)
        display_df = display_df[row_mask]

    st.caption(f"Showing {display_df.shape[0]:,} of {df.shape[0]:,} filtered loans")

    page_size = st.selectbox("Rows per page", options=[10, 25, 50, 100], index=1)
    total_pages = max(1, int(np.ceil(len(display_df) / page_size)))
    page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page_num - 1) * page_size
    end_idx = start_idx + page_size

    show_cols = [
        "LoanID", "CustomerID", "CustomerSegment", "Region", "LoanType", "RiskRating",
        "SecuritisationTranche", "OriginationDate", "DisbursedAmount", "OutstandingBalance",
        "InterestRate", "DPD", "LoanStatus", "CreditBureauScore", "ExpectedLoss",
    ]
    st.dataframe(
        display_df[show_cols].iloc[start_idx:end_idx].reset_index(drop=True),
        use_container_width=True,
        height=460,
    )

    csv_bytes = display_df[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Dataset as CSV",
        data=csv_bytes,
        file_name="banking_risk_filtered_portfolio.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Banking Risk Analytics Platform — Streamlit replica of the Power BI report. "
    "All data is synthetically generated for demonstration purposes."
)
