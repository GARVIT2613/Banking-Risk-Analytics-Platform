"""
Banking Securitisation & Loan Risk Analytics Platform
Streamlit replica of the 9-page Power BI report (auto loan securitisation pool).

Pages: Executive Summary | Portfolio Overview | IFRS-9 | DPD & Roll Rate | Vintage |
       Dynamic Loss | Waterfall | Investor Reporting | Stress Testing
"""
import inspect
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Banking Risk Analytics Platform", page_icon="🏦", layout="wide")

# ----------------------------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------------------------
BLUE, NAVY, ORANGE, PURPLE, PINK = "#118DFF", "#12239E", "#E66C37", "#6B007B", "#E044A7"
VIOLET, GOLD, RED, GREEN, STRESS_PINK = "#744EC2", "#D9B300", "#D64550", "#1AAB40", "#E88F99"

DPD_ORDER = ["Current", "1-29 DPD", "30-59 DPD", "60-89 DPD", "90-119 DPD", "120+ DPD", "Default", "Repossessed"]
STAGE_LABELS = {1: "Stage 1", 2: "Stage 2", 3: "Stage 3"}
STAGE_COLORS = {"Stage 1": BLUE, "Stage 2": NAVY, "Stage 3": ORANGE}
SERVICER_COLORS = {"HDFC Bank Auto Finance": BLUE, "Bajaj Finance Auto": NAVY, "ICICI Auto Loans": ORANGE}
REGION_COLORS = {"East": BLUE, "North": NAVY, "South": ORANGE, "Central": PURPLE, "West": PINK}

# Stress scenarios: (PD multiplier, LGD multiplier) applied to the base PD / LGD / ECL.
# Calibrated to reproduce the Power BI stress table (Stress ECL = Base ECL x PD mult x LGD mult).
STRESS_SCENARIOS = {
    "Base": (1.00, 1.00),
    "Mild Recession": (1.25, 1.10),
    "Severe Recession": (1.50, 1.30),
    "COVID Shock": (1.80, 1.20),
    "2008 Crisis": (2.00, 1.50),
}

# Fixed deal-waterfall deductions (as shown in the Power BI Waterfall page).
WATERFALL_DEDUCTIONS = {
    "Senior Fees": 500_000,
    "Class A Interest": 3_000_000,
    "Class A Principal": 10_000_000,
    "Class B Interest": 1_000_000,
    "Class B Principal": 3_000_000,
    "Residual Distribution": 1_500_000,
}

DATA_FILES = {
    "loans": "auto_loan_securitisation_data.csv",
    "snaps": "dpd_snapshot_history.csv",
    "loss": "dynamic_loss_monthly.csv",
    "vint": "static_pool_vintage_data.csv",
}

# ----------------------------------------------------------------------------------
# STYLE
# ----------------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {padding-top: 1rem; max-width: 1500px;}
    .page-title {font-family: Georgia, 'Times New Roman', serif; font-size: 2.6rem; text-align: center;
                 letter-spacing: 1px; margin: 0 0 .8rem 0; text-transform: uppercase; color: #252423;}
    .kpi {text-align: center; padding: .3rem 0 .6rem 0;}
    .kpi-v {font-size: 2.7rem; font-weight: 500; color: #252423; line-height: 1.1; font-family: 'Segoe UI', Arial, sans-serif;}
    .kpi-l {font-size: .95rem; color: #605E5C;}
    .note {font-size: .8rem; color: #797775;}
    </style>
    """,
    unsafe_allow_html=True,
)

_PLOTLY_WIDTH = "width" in inspect.signature(st.plotly_chart).parameters
_DF_WIDTH = "width" in inspect.signature(st.dataframe).parameters


def show(fig, key=None):
    """Render a plotly figure at container width (works across Streamlit versions)."""
    if _PLOTLY_WIDTH:
        st.plotly_chart(fig, width="stretch", key=key)
    else:
        st.plotly_chart(fig, use_container_width=True, key=key)


def show_df(df, **kw):
    if _DF_WIDTH:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True, **kw)


def style(fig, height=340, legend=True):
    fig.update_layout(
        template="plotly_white", height=height, margin=dict(l=10, r=10, t=48, b=10),
        title_font_size=15, showlegend=legend, paper_bgcolor="white", plot_bgcolor="white",
    )
    return fig


def page_title(text):
    st.markdown(f"<div class='page-title'>{text}</div>", unsafe_allow_html=True)


def kpi_row(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.markdown(
            f"<div class='kpi'><div class='kpi-v'>{value}</div><div class='kpi-l'>{label}</div></div>",
            unsafe_allow_html=True,
        )


# ----------------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------------
def _find(name):
    here = Path(__file__).parent
    for base in (here / "data", here, Path("data"), Path(".")):
        p = base / name
        if p.exists():
            return p
    return None


@st.cache_data(show_spinner="Loading portfolio data...")
def load_data():
    paths = {k: _find(v) for k, v in DATA_FILES.items()}
    missing = [DATA_FILES[k] for k, p in paths.items() if p is None]
    if missing:
        return None, missing

    loans = pd.read_csv(paths["loans"])
    snaps = pd.read_csv(paths["snaps"])
    loss = pd.read_csv(paths["loss"])
    vint = pd.read_csv(paths["vint"])

    for c in ["OriginationDate", "CutoffDate", "MaturityDate"]:
        loans[c] = pd.to_datetime(loans[c], errors="coerce")
    loans["StageLabel"] = loans["IFRS9_Stage"].map(STAGE_LABELS)

    snaps["SnapshotDate"] = pd.to_datetime(snaps["SnapshotDate"], format="%m/%d/%Y", errors="coerce")
    loss["ReportingDate"] = pd.to_datetime(loss["ReportingDate"], errors="coerce")
    vint["VintageStartDate"] = pd.to_datetime(vint["VintageStartDate"], errors="coerce")
    return dict(loans=loans, snaps=snaps, loss=loss, vint=vint), []


data, missing = load_data()
if data is None:
    st.error(
        "Data files not found: " + ", ".join(missing) +
        ". Place the four CSV files in a `data/` folder next to `app.py`."
    )
    st.stop()

loans_raw, snaps_raw, loss_raw, vint = data["loans"], data["snaps"], data["loss"], data["vint"]

# ----------------------------------------------------------------------------------
# SIDEBAR SLICERS (empty selection = All, as in Power BI)
# ----------------------------------------------------------------------------------
st.sidebar.markdown("### Slicers")
d_min, d_max = loss_raw["ReportingDate"].min().date(), loss_raw["ReportingDate"].max().date()
date_range = st.sidebar.slider("ReportingDate", min_value=d_min, max_value=d_max, value=(d_min, d_max), format="MM/DD/YYYY")
sel_stage = st.sidebar.multiselect("IFRS9_Stage", list(STAGE_LABELS.values()), placeholder="All")
sel_status = st.sidebar.multiselect(
    "DelinquencyStatus", [b for b in DPD_ORDER if b in set(loans_raw["DelinquencyStatus"])], placeholder="All")
sel_servicer = st.sidebar.multiselect("ServicerName", sorted(loans_raw["ServicerName"].unique()), placeholder="All")
c_min, c_max = int(loans_raw["CIBIL_Score_Current"].min()), int(loans_raw["CIBIL_Score_Current"].max())
sel_cibil = st.sidebar.slider("CIBIL_Score_Current", c_min, c_max, (c_min, c_max))
fmt_mode = st.sidebar.radio("Number format", ["₹ Cr / Lakh", "Power BI style (M / K / bn)"])
st.sidebar.markdown(
    "<div class='note'>Loan slicers filter the loan and DPD-snapshot tables. "
    "Vintage and Dynamic Loss are pool-level tables, so only the date slicer applies to Dynamic Loss.</div>",
    unsafe_allow_html=True,
)


def money(x):
    x = float(x)
    if fmt_mode.startswith("₹"):
        if abs(x) >= 1e7:
            return f"₹{x / 1e7:,.2f} Cr"
        if abs(x) >= 1e5:
            return f"₹{x / 1e5:,.2f} L"
        return f"₹{x:,.0f}"
    if abs(x) >= 1e9:
        return f"{x / 1e9:,.2f}bn"
    if abs(x) >= 1e6:
        return f"{x / 1e6:,.2f}M"
    if abs(x) >= 1e3:
        return f"{x / 1e3:,.2f}K"
    return f"{x:,.2f}"


loans = loans_raw[loans_raw["CIBIL_Score_Current"].between(*sel_cibil)]
if sel_stage:
    loans = loans[loans["StageLabel"].isin(sel_stage)]
if sel_status:
    loans = loans[loans["DelinquencyStatus"].isin(sel_status)]
if sel_servicer:
    loans = loans[loans["ServicerName"].isin(sel_servicer)]

d0, d1 = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
snaps = snaps_raw[snaps_raw["SnapshotDate"].between(d0, d1) & snaps_raw["LoanID"].isin(loans["LoanID"])]
loss = loss_raw[loss_raw["ReportingDate"].between(d0, d1)]

if loans.empty:
    st.warning("No loans match the selected slicers.")
    st.stop()

# ----------------------------------------------------------------------------------
# REUSABLE BUILDERS
# ----------------------------------------------------------------------------------
def line_by(df, x, y, title, color=BLUE, area=False, height=320):
    g = df.groupby(x, as_index=False)[y].sum().sort_values(x)
    fig = px.area(g, x=x, y=y, title=title) if area else px.line(g, x=x, y=y, title=title)
    fig.update_traces(line_color=color, **({"fillcolor": "rgba(17,141,255,0.35)"} if area else {}))
    return style(fig, height, legend=False)


def pie_of(df, names, values, title, colors=None, hole=0.0, height=330):
    fig = px.pie(df, names=names, values=values, title=title, hole=hole, color=names, color_discrete_map=colors,
                 color_discrete_sequence=[BLUE, NAVY, ORANGE, PURPLE, PINK, VIOLET, GOLD, RED])
    fig.update_traces(textinfo="percent", hovertemplate="%{label}: %{value:,.2f} (%{percent})<extra></extra>")
    return style(fig, height)


def waterfall_frame(loss_df):
    rows = [
        ("Interest Collections", loss_df["CollectionsTotal"].sum()),
        ("Principal Collections", loss_df["ScheduledAmort"].sum()),
        ("Recoveries", loss_df["Recoveries_ThisMonth"].sum()),
    ] + [(k, -v) for k, v in WATERFALL_DEDUCTIONS.items()]
    return pd.DataFrame(rows, columns=["Flow", "Cash Flow Amount"])


def waterfall_fig(wf, height=380):
    fig = go.Figure(go.Waterfall(
        x=list(wf["Flow"]) + ["Total"], y=list(wf["Cash Flow Amount"]) + [wf["Cash Flow Amount"].sum()],
        measure=["relative"] * len(wf) + ["total"],
        increasing=dict(marker=dict(color=GREEN)), decreasing=dict(marker=dict(color=RED)),
        totals=dict(marker=dict(color=BLUE)), connector=dict(line=dict(color="#C8C6C4")),
    ))
    fig.update_layout(title="Cash Flow Amount by Flow", yaxis_title="Cash Flow Amount", yaxis_tickformat=".2s")
    return style(fig, height, legend=False)


def vintage_lines(y, title, height=340):
    fig = px.line(vint, x="MonthsOnBook", y=y, color="VintageID", title=title,
                  color_discrete_sequence=px.colors.qualitative.Dark24)
    return style(fig, height)


def stage_kpi(stage):
    return loans.loc[loans["StageLabel"] == stage, "EAD"].sum()


# ----------------------------------------------------------------------------------
# PAGES
# ----------------------------------------------------------------------------------
tabs = st.tabs(["Executive Summary", "Portfolio Overview", "IFRS-9", "DPD & Roll Rate", "Vintage",
                "Dynamic Loss", "Waterfall", "Investor Reporting", "Stress Testing"])

# ---------------- 1. EXECUTIVE SUMMARY ----------------
with tabs[0]:
    page_title("Executive Summary Dashboard")
    kpi_row([
        ("Portfolio Balance", money(loans["CurrentBalance"].sum())),
        ("Total ECL", money(loans["ECL_Provision"].sum())),
        ("Net Loss", money(loans["NetLoss"].sum())),
        ("Collection Efficiency (avg)", f"{loss['CollectionEfficiency'].mean():.2f}" if len(loss) else "–"),
    ])
    c1, c2 = st.columns(2)
    with c1:
        g = loss.groupby("ReportingDate", as_index=False)["EOP_Balance"].sum()
        fig = px.bar(g, x="ReportingDate", y="EOP_Balance", title="EOP Balance by ReportingDate")
        fig.update_traces(marker_color=BLUE)
        fig.update_layout(yaxis_tickformat=".2s")
        show(style(fig, legend=False), "ex1")
    with c2:
        g = loans.groupby("StageLabel", as_index=False)["CurrentBalance"].sum()
        show(pie_of(g, "StageLabel", "CurrentBalance", "Current Balance by IFRS9 Stage", STAGE_COLORS, hole=0.6), "ex2")
    c3, c4 = st.columns(2)
    with c3:
        show(line_by(loss, "ReportingDate", "MonthlyDefaultRate", "Monthly Default Rate by ReportingDate"), "ex3")
    with c4:
        g = loans.groupby("ServicerName", as_index=False)["InterestRate"].mean()
        show(pie_of(g, "ServicerName", "InterestRate", "Avg Interest Rate by ServicerName", SERVICER_COLORS), "ex4")

# ---------------- 2. PORTFOLIO OVERVIEW ----------------
with tabs[1]:
    page_title("Portfolio Overview Dashboard")
    kpi_row([
        ("IFRS9 ECL", money(loans["ECL_Provision"].sum())),
        ("Current Balance", money(loans["CurrentBalance"].sum())),
        ("Origination Balance", money(loans["OriginalLoanAmount"].sum())),
        ("Total Payments Made", f"{loans['TotalPaymentsMade'].sum():,.0f}"),
    ])
    c1, c2 = st.columns(2)
    with c1:
        g = loans.groupby("CIBIL_Score_Current", as_index=False).size().rename(columns={"size": "Loan Count"})
        fig = px.bar(g, x="CIBIL_Score_Current", y="Loan Count", title="Loan Count by CIBIL Score (Current)")
        fig.update_traces(marker_color=BLUE)
        show(style(fig, legend=False), "po1")
    with c2:
        fig = px.histogram(loans, x="LTV_Current", y="CurrentBalance", histfunc="sum", nbins=80,
                           title="Current Balance by LTV (Current)")
        fig.update_traces(marker_color=BLUE)
        fig.update_layout(yaxis_title="Sum of CurrentBalance", yaxis_tickformat=".2s")
        show(style(fig, legend=False), "po2")
    c3, c4 = st.columns(2)
    with c3:
        fig = px.scatter(loans, x="AnnualIncome_INR", y="CurrentBalance", size="EAD", size_max=20,
                         title="Current Balance and EAD by Annual Income (INR)",
                         hover_data=["LoanID", "Region"])
        fig.update_traces(marker=dict(color=BLUE, opacity=0.7, line=dict(width=0)))
        fig.update_layout(xaxis_tickformat=".2s", yaxis_tickformat=".2s")
        show(style(fig, legend=False), "po3")
    with c4:
        g = loans.groupby("Region", as_index=False)["BorrowerAge"].min()
        show(pie_of(g, "Region", "BorrowerAge", "Min of Borrower Age by Region", REGION_COLORS), "po4")

# ---------------- 3. IFRS-9 ----------------
with tabs[2]:
    page_title("IFRS-9 Dashboard")
    kpi_row([
        ("Stage 1 Exposure", money(stage_kpi("Stage 1"))),
        ("Stage 2 Exposure", money(stage_kpi("Stage 2"))),
        ("Stage 3 Exposure", money(stage_kpi("Stage 3"))),
        ("IFRS9 ECL", money(loans["ECL_Provision"].sum())),
    ])
    c1, c2 = st.columns(2)
    with c1:
        g = loans.groupby("StageLabel", as_index=False)["CurrentBalance"].sum()
        show(pie_of(g, "StageLabel", "CurrentBalance", "Current Balance by IFRS9 Stage", STAGE_COLORS, hole=0.6), "if1")
    with c2:
        g = loans.groupby("BorrowerAge", as_index=False)["IFRS9_Stage"].sum()
        fig = px.line(g, x="BorrowerAge", y="IFRS9_Stage", title="Sum of IFRS9_Stage by Borrower Age")
        fig.update_traces(line_color=BLUE)
        show(style(fig, legend=False), "if2")
    c3, c4 = st.columns(2)
    with c3:
        g = loans.groupby("StageLabel", as_index=False)["ECL_Provision"].sum()
        fig = px.bar(g, x="StageLabel", y="ECL_Provision", title="ECL Provision by IFRS9 Stage")
        fig.update_traces(marker_color=BLUE)
        fig.update_layout(yaxis_tickformat=".2s")
        show(style(fig, legend=False), "if3")
    with c4:
        g = loans.groupby("StageLabel", as_index=False)["InterestRate"].mean()
        show(pie_of(g, "StageLabel", "InterestRate", "WAC by IFRS9 Stage", STAGE_COLORS), "if4")

# ---------------- 4. DPD & ROLL RATE ----------------
with tabs[3]:
    page_title("DPD & Roll Rate Dashboard")
    bal = lambda t: loans.loc[loans["DelinquencyDays"] >= t, "CurrentBalance"].sum()
    kpi_row([("30+ DPD Exposure", money(bal(30))), ("60+ DPD Exposure", money(bal(60))), ("90+ DPD Exposure", money(bal(90)))])

    st.markdown("**Roll Rate Matrix** – share of loans moving from the prior bucket (rows) to the current bucket (columns)")
    if len(snaps):
        ct = pd.crosstab(snaps["DPD_Bucket_Prior"], snaps["DPD_Bucket"], normalize="index")
        rows = [b for b in DPD_ORDER if b in ct.index]
        cols = [b for b in DPD_ORDER if b in ct.columns]
        ct = ct.reindex(index=rows, columns=cols).fillna(0)
        text = np.where(ct.values > 0, np.round(ct.values, 2).astype(str), "")
        fig = go.Figure(go.Heatmap(
            z=ct.values, x=cols, y=rows, text=text, texttemplate="%{text}", zmin=0, zmax=1, showscale=False,
            colorscale=[[0, "#FFFFFF"], [0.15, "#FFF2CC"], [0.5, "#FFD966"], [1, "#D64550"]], xgap=2, ygap=2))
        fig.update_yaxes(autorange="reversed", title="DPD_Bucket_Prior")
        fig.update_xaxes(title="DPD_Bucket", side="top")
        show(style(fig, 420, legend=False), "dpd_m")
    else:
        st.info("No snapshots in the selected range.")

    c1, c2 = st.columns(2)
    with c1:
        show(line_by(snaps, "SnapshotDate", "ConsecutiveMonthsDelinquent",
                     "Sum of Consecutive Months Delinquent by SnapshotDate"), "dpd1")
    with c2:
        g = loans["DelinquencyStatus"].value_counts().reset_index()
        g.columns = ["DPD_Bucket", "Loan Count"]
        fig = px.line(g, x="DPD_Bucket", y="Loan Count", markers=True, title="Loan Count by DPD Bucket")
        fig.update_traces(line_color=BLUE)
        show(style(fig, 320, legend=False), "dpd2")

# ---------------- 5. VINTAGE ----------------
with tabs[4]:
    page_title("Vintage Dashboard")
    kpi_row([
        ("Sum of PoolFactor", f"{vint['PoolFactor'].sum():,.2f}"),
        ("Sum of CumulativeDefaults_Balance", money(vint["CumulativeDefaults_Balance"].sum())),
        ("Sum of CurrentDelinq30Plus", f"{vint['CurrentDelinq30Plus'].sum():,.2f}"),
    ])
    c1, c2 = st.columns(2)
    with c1:
        show(vintage_lines("CumulativeNetLossRate", "Cumulative Net Loss Rate by Months on Book and Vintage"), "vi1")
    with c2:
        g = vint.groupby("VintageID", as_index=False)["CumulativeRecoveries"].sum()
        show(pie_of(g, "VintageID", "CumulativeRecoveries", "Cumulative Recoveries by Vintage"), "vi2")
    c3, c4 = st.columns(2)
    with c3:
        g = vint.groupby("MonthsOnBook", as_index=False)["RemainingPoolBalance"].sum()
        fig = px.line(g, x="MonthsOnBook", y="RemainingPoolBalance", title="Remaining Pool Balance by Months on Book")
        fig.update_traces(line_color=BLUE)
        fig.update_layout(yaxis_tickformat=".2s")
        show(style(fig, legend=False), "vi3")
    with c4:
        fig = px.scatter(vint, x="PoolFactor", y="RemainingPoolBalance", hover_data=["VintageID", "MonthsOnBook"],
                         title="Pool Factor vs Remaining Pool Balance")
        fig.update_traces(marker=dict(color=BLUE, size=8, opacity=0.8))
        fig.update_layout(yaxis_tickformat=".2s")
        show(style(fig, legend=False), "vi4")

# ---------------- 6. DYNAMIC LOSS ----------------
with tabs[5]:
    page_title("Dynamic Loss Dashboard")
    kpi_row([
        ("Sum of GrossLoss_ThisMonth", money(loss["GrossLoss_ThisMonth"].sum())),
        ("Sum of ExcessSpread_Monthly", money(loss["ExcessSpread_Monthly"].sum())),
        ("Sum of Recoveries_ThisMonth", money(loss["Recoveries_ThisMonth"].sum())),
        ("Sum of NetLoss_ThisMonth", money(loss["NetLoss_ThisMonth"].sum())),
    ])
    c1, c2 = st.columns(2)
    with c1:
        show(line_by(loss, "ReportingDate", "NetLoss_ThisMonth", "Net Loss This Month by ReportingDate"), "dl1")
    with c2:
        show(line_by(loss, "ReportingDate", "CPR_Annualised", "CPR Annualised by ReportingDate", area=True), "dl2")
    c3, c4 = st.columns(2)
    with c3:
        g = loss.groupby("ReportingDate", as_index=False)["CollectionEfficiency"].sum()
        g["Label"] = g["ReportingDate"].dt.strftime("%A, %B %d, %Y")
        fig = px.treemap(g, path=["Label"], values="CollectionEfficiency", title="Collection Efficiency by ReportingDate",
                         color_discrete_sequence=[BLUE, NAVY, ORANGE, PURPLE, PINK, VIOLET, GOLD, RED])
        show(style(fig, 360, legend=False), "dl3")
    with c4:
        bop = float(loss["BOP_Balance"].sum())
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=bop / 1e9, number=dict(suffix="bn", valueformat=".2f"),
            title=dict(text="Sum of BOP_Balance"),
            gauge=dict(axis=dict(range=[0, max(bop * 2 / 1e9, 0.01)]), bar=dict(color=BLUE), bgcolor="#F2F2F2")))
        show(style(fig, 360, legend=False), "dl4")

# ---------------- 7. WATERFALL ----------------
with tabs[6]:
    page_title("Waterfall Dashboard")
    kpi_row([
        ("CollectionsTotal", money(loss["CollectionsTotal"].sum())),
        ("Recoveries_ThisMonth", money(loss["Recoveries_ThisMonth"].sum())),
        ("ScheduledAmort", money(loss["ScheduledAmort"].sum())),
        ("NetLoss_ThisMonth", money(loss["NetLoss_ThisMonth"].sum())),
    ])
    wf = waterfall_frame(loss)
    c1, c2 = st.columns([3, 2])
    with c1:
        show(waterfall_fig(wf), "wf1")
    with c2:
        t = wf.copy()
        t.loc[len(t)] = ["Total", t["Cash Flow Amount"].sum()]
        show_df(t.style.format({"Cash Flow Amount": "{:,.2f}"}), height=390)
    c3, c4 = st.columns(2)
    with c3:
        g = loss.groupby("ReportingDate", as_index=False)[["Recoveries_ThisMonth", "CollectionsTotal"]].sum()
        fig = go.Figure()
        fig.add_scatter(x=g["ReportingDate"], y=g["Recoveries_ThisMonth"], name="Recoveries_ThisMonth", line=dict(color=BLUE))
        fig.add_scatter(x=g["ReportingDate"], y=g["CollectionsTotal"], name="CollectionsTotal", line=dict(color=NAVY))
        fig.update_layout(title="Recoveries and Collections Total by ReportingDate", yaxis_tickformat=".2s")
        show(style(fig, 320), "wf2")
    with c4:
        show(line_by(loss, "ReportingDate", "ExcessSpread_Monthly", "Excess Spread Monthly by ReportingDate", area=True), "wf3")

# ---------------- 8. INVESTOR REPORTING ----------------
with tabs[7]:
    page_title("Investor Reporting Dashboard")
    kpi_row([
        ("Portfolio Balance", money(loans["CurrentBalance"].sum())),
        ("Expected Credit Loss", money(loans["ECL_Provision"].sum())),
        ("Net Loss", money(loss["NetLoss_ThisMonth"].sum())),
        ("Collection Efficiency (avg)", f"{loss['CollectionEfficiency'].mean():.2f}" if len(loss) else "–"),
    ])
    c1, c2 = st.columns(2)
    with c1:
        show(line_by(loss, "ReportingDate", "EOP_Balance", "Portfolio Balance Trend by ReportingDate"), "ir1")
    with c2:
        s30 = snaps[snaps["DPD_Days"] >= 30]
        show(line_by(s30, "SnapshotDate", "CurrentBalance", "30+ DPD Exposure by Snapshot Date"), "ir2")
    c3, c4 = st.columns(2)
    with c3:
        show(vintage_lines("CumulativeNetLoss", "Cumulative Net Loss by Months on Book and Vintage", 380), "ir3")
    with c4:
        show(waterfall_fig(wf, 380), "ir4")

# ---------------- 9. STRESS TESTING ----------------
with tabs[8]:
    page_title("Stress Testing Dashboard")
    chosen = st.multiselect("Scenario", list(STRESS_SCENARIOS), default=list(STRESS_SCENARIOS), placeholder="All")
    chosen = chosen or list(STRESS_SCENARIOS)

    base_ecl = loans["ECL_Provision"].sum()
    base_pd, base_lgd = loans["PD_Estimate"].mean(), loans["LGD_Estimate"].mean()
    rows = []
    for name in chosen:
        pm, lm = STRESS_SCENARIOS[name]
        stress = base_ecl * pm * lm
        rows.append(dict(Scenario=name, **{"Base ECL": base_ecl, "Stress ECL": stress, "ECL Increase": stress - base_ecl,
                                           "ECL Increase %": (stress / base_ecl - 1) if base_ecl else 0,
                                           "Stress PD": base_pd * pm, "Stress LGD": base_lgd * lm}))
    st_df = pd.DataFrame(rows)
    worst = st_df.loc[st_df["Stress ECL"].idxmax()]
    kpi_row([
        ("Base ECL", money(base_ecl)),
        (f"Stress ECL ({worst['Scenario']})", money(worst["Stress ECL"])),
        ("ECL Increase", money(worst["ECL Increase"])),
        ("ECL Increase %", f"{worst['ECL Increase %'] * 100:,.0f}%"),
    ])

    c1, c2 = st.columns([1, 1.15])
    with c1:
        g = st_df.sort_values("Stress ECL", ascending=False)
        fig = px.bar(g, x="Scenario", y="Stress ECL", text=g["Stress ECL"].map(money), title="Stress ECL by Scenario")
        fig.update_traces(marker_color=STRESS_PINK, textposition="outside")
        fig.update_layout(yaxis_tickformat=".2s")
        show(style(fig, 380, legend=False), "st1")
    with c2:
        lo, hi = st_df["Stress ECL"].min(), st_df["Stress ECL"].max()

        def heat(v):
            t = 0 if hi == lo else (v - lo) / (hi - lo)
            return f"background-color: rgb(255,{int(255 * (1 - t))},0)"

        disp = st_df[["Scenario", "Base ECL", "Stress ECL", "ECL Increase", "ECL Increase %"]].sort_values("Scenario")
        styled = (disp.style.map(heat, subset=["Stress ECL"])
                  .format({"Base ECL": "{:,.2f}", "Stress ECL": "{:,.2f}", "ECL Increase": "{:,.2f}", "ECL Increase %": "{:.0%}"}))
        show_df(styled, height=250)
        st.markdown(
            "<div class='note'>Stress ECL = Base ECL × PD multiplier × LGD multiplier. "
            "Multipliers per scenario: " + ", ".join(f"{k} (PD ×{a}, LGD ×{b})" for k, (a, b) in STRESS_SCENARIOS.items()) + ".</div>",
            unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        g = st_df.sort_values("Stress PD")
        fig = px.bar(g, x="Stress PD", y="Scenario", orientation="h", title="PD Impact Analysis")
        fig.update_traces(marker_color=STRESS_PINK)
        show(style(fig, 340, legend=False), "st2")
    with c4:
        g = st_df.sort_values("Stress LGD")
        fig = px.bar(g, x="Stress LGD", y="Scenario", orientation="h", title="LGD Impact Analysis")
        fig.update_traces(marker_color=STRESS_PINK)
        show(style(fig, 340, legend=False), "st3")
