"""
Banking Securitisation & Loan Risk Analytics Platform — Streamlit
9-page report with a dedicated, per-dashboard color-theming system and an
equal-width top navigation bar (replacing st.tabs).
"""
import inspect
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Banking Risk Analytics Platform", page_icon="🏦", layout="wide")

# ====================================================================================
# 1. THEME_CONFIG — one entry per dashboard: KPI colors, slicer accents, chart palette
# ====================================================================================
THEME_CONFIG = {
    "Executive Summary": {
        "label": "Executive Overview",
        "kpi_bg": "#0F2027", "kpi_text": "#F8FAFC", "accent": "#118DFF",
        "slicer_border": "#1A365D", "slicer_highlight": "#DBEAFE",
        "seq": ["#118DFF", "#93C5FD", "#475569", "#1A365D", "#0F2027"],
        "bar": "#118DFF", "line": "#118DFF", "area_fill": "rgba(147,197,253,0.45)", "secondary": "#475569",
    },
    "DPD & Roll Rate": {
        "label": "Credit Risk & Asset Quality",
        "kpi_bg": "#FFFFFF", "kpi_text": "#0F172A", "accent": "#F59E0B",
        "slicer_border": "#D97706", "slicer_highlight": "#FEF3C7",
        "seq": ["#22C55E", "#06B6D4", "#FBBF24", "#F97316", "#EF4444", "#DC2626", "#991B1B"],
        "bucket_colors": {
            "Current": "#22C55E", "1-29 DPD": "#06B6D4", "30-59 DPD": "#FBBF24",
            "60-89 DPD": "#F97316", "90-119 DPD": "#EF4444", "120+ DPD": "#DC2626",
            "Default": "#991B1B", "Repossessed": "#7F1D1D",
        },
        "bar": "#F59E0B", "line": "#DC2626", "area_fill": "rgba(251,191,36,0.4)", "secondary": "#475569",
        "kpi_low": "#16A34A", "kpi_med": "#F59E0B", "kpi_high": "#DC2626",
    },
    "Dynamic Loss": {
        "label": "NPL & Default Analytics",
        "kpi_bg": "#FFFFFF", "kpi_text": "#7F1D1D", "accent": "#991B1B",
        "slicer_border": "#B91C1C", "slicer_highlight": "#FEE2E2",
        "seq": ["#DC2626", "#16A34A", "#475569", "#7F1D1D", "#F87171"],
        "bar": "#7F1D1D", "line": "#DC2626", "area_fill": "rgba(220,38,38,0.35)", "secondary": "#16A34A",
    },
    "Waterfall": {
        "label": "Securitisation & Tranches",
        "kpi_bg": "#FFFFFF", "kpi_text": "#1E3A8A", "accent": "#D97706",
        "slicer_border": "#FCD34D", "slicer_highlight": "#FEF3C7",
        "seq": ["#1E3A8A", "#F59E0B", "#DC2626", "#10B981", "#1E40AF"],
        "bar": "#1E3A8A", "line": "#10B981", "area_fill": "rgba(245,158,11,0.35)", "secondary": "#B45309",
    },
    "Portfolio Overview": {
        "label": "Underwriting & Bureau Profile",
        "kpi_bg": "#FFFFFF", "kpi_text": "#0D9488", "accent": "#14B8A6",
        "slicer_border": "#0D9488", "slicer_highlight": "#CCFBF1",
        "seq": ["#059669", "#10B981", "#F59E0B", "#E11D48", "#0D9488"],
        "bucket_colors": {"750+": "#059669", "700-749": "#10B981", "600-699": "#F59E0B", "<600": "#E11D48"},
        "bar": "#0D9488", "line": "#0D9488", "area_fill": "rgba(20,184,166,0.35)", "secondary": "#E11D48",
    },
    "Investor Reporting": {
        "label": "Geographic & Exposure Analysis",
        "kpi_bg": "#FFFFFF", "kpi_text": "#0284C7", "accent": "#0369A1",
        "slicer_border": "#0369A1", "slicer_highlight": "#E0F2FE",
        "seq": ["#BAE6FD", "#38BDF8", "#0284C7", "#334155", "#EF4444"],
        "bar": "#0284C7", "line": "#0284C7", "area_fill": "rgba(56,189,248,0.35)", "secondary": "#334155",
    },
    "IFRS-9": {
        "label": "ECL & IFRS 9 Provisioning",
        "kpi_bg": "#FFFFFF", "kpi_text": "#0F172A", "accent": "#334155",
        "slicer_border": "#334155", "slicer_highlight": "#E2E8F0",
        "seq": ["#22C55E", "#F59E0B", "#DC2626", "#1E293B"],
        "bucket_colors": {"Stage 1": "#22C55E", "Stage 2": "#F59E0B", "Stage 3": "#DC2626"},
        "bar": "#334155", "line": "#1E293B", "area_fill": "rgba(51,65,85,0.3)", "secondary": "#1E293B",
    },
    "Vintage": {
        "label": "Vintage & Cohort Curves",
        "kpi_bg": "#FFFFFF", "kpi_text": "#4338CA", "accent": "#4F46E5",
        "slicer_border": "#4F46E5", "slicer_highlight": "#E0E7FF",
        "seq": ["#64748B", "#0284C7", "#2563EB", "#7C3AED", "#EA580C"],
        "bar": "#4F46E5", "line": "#2563EB", "area_fill": "rgba(124,58,237,0.3)", "secondary": "#EA580C",
    },
    "Stress Testing": {
        "label": "Stress Testing & Regulatory Capital",
        "kpi_bg": "#FFFFFF", "kpi_text": "#C2410C", "accent": "#C2410C",
        "slicer_border": "#C2410C", "slicer_highlight": "#FFEDD5",
        "seq": ["#94A3B8", "#EA580C", "#DC2626", "#FF0000", "#7C2D12"],
        "bar": "#EA580C", "line": "#DC2626", "area_fill": "rgba(234,88,12,0.3)", "secondary": "#94A3B8",
        "kpi_baseline": "#047857", "kpi_stressed": "#C2410C",
    },
}
PAGE_ORDER = list(THEME_CONFIG.keys())

BASE_BG, BASE_TEXT, BASE_BORDER = "#F8FAFC", "#0F172A", "#E2E8F0"
DPD_ORDER = ["Current", "1-29 DPD", "30-59 DPD", "60-89 DPD", "90-119 DPD", "120+ DPD", "Default", "Repossessed"]
STAGE_LABELS = {1: "Stage 1", 2: "Stage 2", 3: "Stage 3"}

STRESS_SCENARIOS = {
    "Base": (1.00, 1.00), "Mild Recession": (1.25, 1.10), "Severe Recession": (1.50, 1.30),
    "COVID Shock": (1.80, 1.20), "2008 Crisis": (2.00, 1.50),
}
WATERFALL_DEDUCTIONS = {
    "Senior Fees": 500_000, "Class A Interest": 3_000_000, "Class A Principal": 10_000_000,
    "Class B Interest": 1_000_000, "Class B Principal": 3_000_000, "Residual Distribution": 1_500_000,
}
DATA_FILES = {
    "loans": "auto_loan_securitisation_data.csv", "snaps": "dpd_snapshot_history.csv",
    "loss": "dynamic_loss_monthly.csv", "vint": "static_pool_vintage_data.csv",
}

# ====================================================================================
# 2. GLOBAL BASE STYLE + apply_dashboard_theme()
# ====================================================================================
st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; }}
    .block-container {{ padding-top: .6rem; max-width: 1500px; }}
    .page-title {{ font-family: Georgia, 'Times New Roman', serif; font-size: 2.3rem; text-align: center;
                 letter-spacing: 1px; margin: .2rem 0 1rem 0; text-transform: uppercase; color: {BASE_TEXT}; }}
    .note {{ font-size: .8rem; color: #797775; }}
    div[data-testid="stMetric"] {{ background: #FFFFFF; border: 1px solid {BASE_BORDER}; border-radius: 12px;
        padding: 14px 16px 10px 16px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def apply_dashboard_theme(dashboard_name: str) -> dict:
    """Inject page-specific CSS (KPI cards, sidebar accents, nav bar) and return the theme dict."""
    t = THEME_CONFIG[dashboard_name]
    css = f"""
    <style>
    div[data-testid="stMetric"] {{
        border: 1px solid {t['slicer_border']}33 !important;
        border-top: 4px solid {t['accent']} !important;
        box-shadow: 0 1px 3px rgba(15,23,42,0.06);
    }}
    div[data-testid="stMetricValue"] {{ color: {BASE_TEXT} !important; }}
    div[data-testid="stMetricLabel"] {{ color: {BASE_TEXT}99 !important; }}

    section[data-testid="stSidebar"] {{ background-color: #FFFFFF; border-right: 1px solid {BASE_BORDER}; }}
    section[data-testid="stSidebar"] h3 {{ color: {t['accent']}; }}
    section[data-testid="stSidebar"] [data-baseweb="tag"] {{
        background-color: {t['slicer_highlight']} !important; border: 1px solid {t['slicer_border']} !important;
        color: {BASE_TEXT} !important;
    }}
    section[data-testid="stSidebar"] [role="slider"] {{ background-color: {t['slicer_border']} !important; }}
    section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {{
        border-color: {t['slicer_border']} !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="radio"] label div:first-child {{
        border-color: {t['slicer_border']} !important;
    }}

    .theme-banner {{ background: linear-gradient(90deg, {t['accent']}22, transparent);
        border-left: 5px solid {t['accent']}; padding: 6px 14px; border-radius: 6px; margin-bottom: .6rem;
        font-size: .82rem; color: {BASE_TEXT}; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    return t


def render_nav(active: str):
    """Equal-width, evenly-spread top navigation bar — an alternative to st.tabs."""
    st.markdown(
        """
        <style>
        div[data-testid="stHorizontalBlock"].nav-row div.stButton > button {
            width: 100%; border-radius: 8px 8px 0 0; border: 1px solid #E2E8F0; border-bottom: none;
            font-size: .78rem; padding: .5rem .2rem; white-space: normal; line-height: 1.15;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(len(PAGE_ORDER), gap="small")
    for col, name in zip(cols, PAGE_ORDER):
        t = THEME_CONFIG[name]
        is_active = name == active
        with col:
            if st.button(t["label"], key=f"nav_{name}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state["page"] = name
                st.rerun()
    st.markdown(
        f"<div style='height:3px;background:{THEME_CONFIG[active]['accent']};margin-top:-14px;"
        f"border-radius:2px;'></div>", unsafe_allow_html=True,
    )


_PLOTLY_WIDTH = "width" in inspect.signature(st.plotly_chart).parameters
_DF_WIDTH = "width" in inspect.signature(st.dataframe).parameters


def show(fig, key=None):
    if _PLOTLY_WIDTH:
        st.plotly_chart(fig, width="stretch", key=key)
    else:
        st.plotly_chart(fig, use_container_width=True, key=key)


def show_df(df, **kw):
    if _DF_WIDTH:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True, **kw)


def style(fig, theme, height=340, legend=True):
    fig.update_layout(
        template="plotly_white", height=height, margin=dict(l=10, r=10, t=48, b=10),
        title_font_size=15, showlegend=legend, paper_bgcolor="white", plot_bgcolor="white",
        colorway=theme["seq"], font=dict(color=BASE_TEXT),
    )
    return fig


def page_title(text):
    st.markdown(f"<div class='page-title'>{text}</div>", unsafe_allow_html=True)


def kpi_row(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


# ====================================================================================
# 3. DATA LOADING
# ====================================================================================
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
    st.error("Data files not found: " + ", ".join(missing) + ". Place the four CSVs in a `data/` folder next to `app.py`.")
    st.stop()
loans_raw, snaps_raw, loss_raw, vint = data["loans"], data["snaps"], data["loss"], data["vint"]

# ====================================================================================
# 4. NAVIGATION (equal-width bar, alternative to st.tabs) + ACTIVE THEME
# ====================================================================================
if "page" not in st.session_state:
    st.session_state["page"] = PAGE_ORDER[0]
active_page = st.session_state["page"]

render_nav(active_page)
theme = apply_dashboard_theme(active_page)
st.markdown(
    f"<div class='theme-banner'>Theme: <b>{theme['label']}</b> — KPI accents, slicers and chart palette "
    f"on this page follow the {theme['label']} color system.</div>", unsafe_allow_html=True,
)

# ====================================================================================
# 5. SIDEBAR SLICERS
# ====================================================================================
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

def money(x):
    x = float(x)
    if fmt_mode.startswith("₹"):
        if abs(x) >= 1e7: return f"₹{x/1e7:,.2f} Cr"
        if abs(x) >= 1e5: return f"₹{x/1e5:,.2f} L"
        return f"₹{x:,.0f}"
    if abs(x) >= 1e9: return f"{x/1e9:,.2f}bn"
    if abs(x) >= 1e6: return f"{x/1e6:,.2f}M"
    if abs(x) >= 1e3: return f"{x/1e3:,.2f}K"
    return f"{x:,.2f}"

loans = loans_raw[loans_raw["CIBIL_Score_Current"].between(*sel_cibil)]
if sel_stage: loans = loans[loans["StageLabel"].isin(sel_stage)]
if sel_status: loans = loans[loans["DelinquencyStatus"].isin(sel_status)]
if sel_servicer: loans = loans[loans["ServicerName"].isin(sel_servicer)]
d0, d1 = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
snaps = snaps_raw[snaps_raw["SnapshotDate"].between(d0, d1) & snaps_raw["LoanID"].isin(loans["LoanID"])]
loss = loss_raw[loss_raw["ReportingDate"].between(d0, d1)]
if loans.empty:
    st.warning("No loans match the selected slicers.")
    st.stop()

# ====================================================================================
# 6. CHART HELPERS (theme-aware)
# ====================================================================================
def line_by(df, x, y, title, theme, area=False, height=320, color=None):
    g = df.groupby(x, as_index=False)[y].sum().sort_values(x)
    fig = px.area(g, x=x, y=y, title=title) if area else px.line(g, x=x, y=y, title=title)
    fig.update_traces(line_color=color or theme["line"], **({"fillcolor": theme["area_fill"]} if area else {}))
    return style(fig, theme, height, legend=False)


def pie_of(df, names, values, title, theme, colors=None, hole=0.0, height=330):
    fig = px.pie(df, names=names, values=values, title=title, hole=hole, color=names,
                 color_discrete_map=colors, color_discrete_sequence=theme["seq"])
    fig.update_traces(textinfo="percent", hovertemplate="%{label}: %{value:,.2f} (%{percent})<extra></extra>")
    return style(fig, theme, height)


def waterfall_frame(loss_df):
    rows = [("Interest Collections", loss_df["CollectionsTotal"].sum()),
            ("Principal Collections", loss_df["ScheduledAmort"].sum()),
            ("Recoveries", loss_df["Recoveries_ThisMonth"].sum())] + \
           [(k, -v) for k, v in WATERFALL_DEDUCTIONS.items()]
    return pd.DataFrame(rows, columns=["Flow", "Cash Flow Amount"])


def waterfall_fig(wf, theme, height=380):
    fig = go.Figure(go.Waterfall(
        x=list(wf["Flow"]) + ["Total"], y=list(wf["Cash Flow Amount"]) + [wf["Cash Flow Amount"].sum()],
        measure=["relative"] * len(wf) + ["total"],
        increasing=dict(marker=dict(color="#10B981")), decreasing=dict(marker=dict(color=theme["seq"][2])),
        totals=dict(marker=dict(color=theme["accent"])), connector=dict(line=dict(color="#C8C6C4")),
    ))
    fig.update_layout(title="Cash Flow Amount by Flow", yaxis_title="Cash Flow Amount", yaxis_tickformat=".2s")
    return style(fig, theme, height, legend=False)


def vintage_lines(y, title, theme, height=340):
    fig = px.line(vint, x="MonthsOnBook", y=y, color="VintageID", title=title, color_discrete_sequence=theme["seq"])
    return style(fig, theme, height)


def stage_kpi(stage):
    return loans.loc[loans["StageLabel"] == stage, "EAD"].sum()

# ====================================================================================
# 7. PAGE RENDERERS
# ====================================================================================
def page_executive(theme):
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
        fig.update_traces(marker_color=theme["bar"])
        fig.update_layout(yaxis_tickformat=".2s")
        show(style(fig, theme, legend=False), "ex1")
    with c2:
        g = loans.groupby("StageLabel", as_index=False)["CurrentBalance"].sum()
        show(pie_of(g, "StageLabel", "CurrentBalance", "Current Balance by IFRS9 Stage", theme, hole=0.6), "ex2")
    c3, c4 = st.columns(2)
    with c3:
        show(line_by(loss, "ReportingDate", "MonthlyDefaultRate", "Monthly Default Rate by ReportingDate", theme), "ex3")
    with c4:
        g = loans.groupby("ServicerName", as_index=False)["InterestRate"].mean()
        show(pie_of(g, "ServicerName", "InterestRate", "Avg Interest Rate by ServicerName", theme), "ex4")


def page_portfolio(theme):
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
        fig.update_traces(marker_color=theme["bar"])
        show(style(fig, theme, legend=False), "po1")
    with c2:
        fig = px.histogram(loans, x="LTV_Current", y="CurrentBalance", histfunc="sum", nbins=80,
                            title="Current Balance by LTV (Current)")
        fig.update_traces(marker_color=theme["bar"])
        fig.update_layout(yaxis_title="Sum of CurrentBalance", yaxis_tickformat=".2s")
        show(style(fig, theme, legend=False), "po2")
    c3, c4 = st.columns(2)
    with c3:
        fig = px.scatter(loans, x="AnnualIncome_INR", y="CurrentBalance", size="EAD", size_max=20,
                          title="Current Balance and EAD by Annual Income (INR)", hover_data=["LoanID", "Region"])
        fig.update_traces(marker=dict(color=theme["accent"], opacity=0.7, line=dict(width=0)))
        fig.update_layout(xaxis_tickformat=".2s", yaxis_tickformat=".2s")
        show(style(fig, theme, legend=False), "po3")
    with c4:
        g = loans.groupby("Region", as_index=False)["BorrowerAge"].min()
        show(pie_of(g, "Region", "BorrowerAge", "Min of Borrower Age by Region", theme), "po4")


def page_ifrs9(theme):
    page_title("IFRS-9 Dashboard")
    kpi_row([
        ("Stage 1 Exposure", money(stage_kpi("Stage 1"))),
        ("Stage 2 Exposure", money(stage_kpi("Stage 2"))),
        ("Stage 3 Exposure", money(stage_kpi("Stage 3"))),
        ("IFRS9 ECL", money(loans["ECL_Provision"].sum())),
    ])
    bc = theme.get("bucket_colors")
    c1, c2 = st.columns(2)
    with c1:
        g = loans.groupby("StageLabel", as_index=False)["CurrentBalance"].sum()
        show(pie_of(g, "StageLabel", "CurrentBalance", "Current Balance by IFRS9 Stage", theme, colors=bc, hole=0.6), "if1")
    with c2:
        g = loans.groupby("BorrowerAge", as_index=False)["IFRS9_Stage"].sum()
        fig = px.line(g, x="BorrowerAge", y="IFRS9_Stage", title="Sum of IFRS9_Stage by Borrower Age")
        fig.update_traces(line_color=theme["line"])
        show(style(fig, theme, legend=False), "if2")
    c3, c4 = st.columns(2)
    with c3:
        g = loans.groupby("StageLabel", as_index=False)["ECL_Provision"].sum()
        fig = px.bar(g, x="StageLabel", y="ECL_Provision", title="ECL Provision by IFRS9 Stage",
                     color="StageLabel", color_discrete_map=bc)
        fig.update_layout(yaxis_tickformat=".2s")
        show(style(fig, theme, legend=False), "if3")
    with c4:
        g = loans.groupby("StageLabel", as_index=False)["InterestRate"].mean()
        show(pie_of(g, "StageLabel", "InterestRate", "WAC by IFRS9 Stage", theme, colors=bc), "if4")


def page_dpd(theme):
    page_title("DPD & Roll Rate Dashboard")
    bal = lambda t: loans.loc[loans["DelinquencyDays"] >= t, "CurrentBalance"].sum()
    b30, b60, b90 = bal(30), bal(60), bal(90)
    c1, c2, c3 = st.columns(3)
    c1.metric("30+ DPD Exposure (Low watch)", money(b30))
    c2.metric("60+ DPD Exposure (Med risk)", money(b60))
    c3.metric("90+ DPD Exposure (High risk)", money(b90))
    st.markdown(
        f"<div style='display:flex;gap:6px;margin:-8px 0 12px 0;'>"
        f"<div style='flex:1;height:5px;background:{theme['kpi_low']};border-radius:3px'></div>"
        f"<div style='flex:1;height:5px;background:{theme['kpi_med']};border-radius:3px'></div>"
        f"<div style='flex:1;height:5px;background:{theme['kpi_high']};border-radius:3px'></div></div>",
        unsafe_allow_html=True)

    st.markdown("**Roll Rate Matrix** — share of loans moving from the prior bucket (rows) to the current bucket (columns)")
    if len(snaps):
        ct = pd.crosstab(snaps["DPD_Bucket_Prior"], snaps["DPD_Bucket"], normalize="index")
        rows = [b for b in DPD_ORDER if b in ct.index]
        cols = [b for b in DPD_ORDER if b in ct.columns]
        ct = ct.reindex(index=rows, columns=cols).fillna(0)
        text = np.where(ct.values > 0, np.round(ct.values, 2).astype(str), "")
        fig = go.Figure(go.Heatmap(
            z=ct.values, x=cols, y=rows, text=text, texttemplate="%{text}", zmin=0, zmax=1, showscale=False,
            colorscale=[[0, "#FFFFFF"], [0.15, theme["bucket_colors"]["Current"] + "33"],
                        [0.5, theme["bucket_colors"]["60-89 DPD"]], [1, theme["bucket_colors"]["Default"]]],
            xgap=2, ygap=2))
        fig.update_yaxes(autorange="reversed", title="DPD_Bucket_Prior")
        fig.update_xaxes(title="DPD_Bucket", side="top")
        show(style(fig, theme, 420, legend=False), "dpd_m")
    else:
        st.info("No snapshots in the selected range.")

    c1, c2 = st.columns(2)
    with c1:
        show(line_by(snaps, "SnapshotDate", "ConsecutiveMonthsDelinquent",
                      "Sum of Consecutive Months Delinquent by SnapshotDate", theme), "dpd1")
    with c2:
        g = loans["DelinquencyStatus"].value_counts().reset_index()
        g.columns = ["DPD_Bucket", "Loan Count"]
        fig = px.line(g, x="DPD_Bucket", y="Loan Count", markers=True, title="Loan Count by DPD Bucket")
        fig.update_traces(line_color=theme["line"], marker_color=theme["accent"])
        show(style(fig, theme, 320, legend=False), "dpd2")


def page_vintage(theme):
    page_title("Vintage Dashboard")
    kpi_row([
        ("Sum of PoolFactor", f"{vint['PoolFactor'].sum():,.2f}"),
        ("Sum of CumulativeDefaults_Balance", money(vint["CumulativeDefaults_Balance"].sum())),
        ("Sum of CurrentDelinq30Plus", f"{vint['CurrentDelinq30Plus'].sum():,.2f}"),
    ])
    c1, c2 = st.columns(2)
    with c1:
        show(vintage_lines("CumulativeNetLossRate", "Cumulative Net Loss Rate by Months on Book and Vintage", theme), "vi1")
    with c2:
        g = vint.groupby("VintageID", as_index=False)["CumulativeRecoveries"].sum()
        show(pie_of(g, "VintageID", "CumulativeRecoveries", "Cumulative Recoveries by Vintage", theme), "vi2")
    c3, c4 = st.columns(2)
    with c3:
        g = vint.groupby("MonthsOnBook", as_index=False)["RemainingPoolBalance"].sum()
        fig = px.line(g, x="MonthsOnBook", y="RemainingPoolBalance", title="Remaining Pool Balance by Months on Book")
        fig.update_traces(line_color=theme["line"])
        fig.update_layout(yaxis_tickformat=".2s")
        show(style(fig, theme, legend=False), "vi3")
    with c4:
        fig = px.scatter(vint, x="PoolFactor", y="RemainingPoolBalance", hover_data=["VintageID", "MonthsOnBook"],
                          title="Pool Factor vs Remaining Pool Balance")
        fig.update_traces(marker=dict(color=theme["accent"], size=8, opacity=0.8))
        fig.update_layout(yaxis_tickformat=".2s")
        show(style(fig, theme, legend=False), "vi4")


def page_dynamic_loss(theme):
    page_title("Dynamic Loss Dashboard")
    kpi_row([
        ("Sum of GrossLoss_ThisMonth", money(loss["GrossLoss_ThisMonth"].sum())),
        ("Sum of ExcessSpread_Monthly", money(loss["ExcessSpread_Monthly"].sum())),
        ("Sum of Recoveries_ThisMonth", money(loss["Recoveries_ThisMonth"].sum())),
        ("Sum of NetLoss_ThisMonth", money(loss["NetLoss_ThisMonth"].sum())),
    ])
    c1, c2 = st.columns(2)
    with c1:
        show(line_by(loss, "ReportingDate", "NetLoss_ThisMonth", "Net Loss This Month by ReportingDate", theme), "dl1")
    with c2:
        show(line_by(loss, "ReportingDate", "CPR_Annualised", "CPR Annualised by ReportingDate", theme, area=True), "dl2")
    c3, c4 = st.columns(2)
    with c3:
        g = loss.groupby("ReportingDate", as_index=False)["CollectionEfficiency"].sum()
        g["Label"] = g["ReportingDate"].dt.strftime("%A, %B %d, %Y")
        fig = px.treemap(g, path=["Label"], values="CollectionEfficiency", title="Collection Efficiency by ReportingDate",
                          color_discrete_sequence=theme["seq"])
        show(style(fig, theme, 360, legend=False), "dl3")
    with c4:
        bop = float(loss["BOP_Balance"].sum())
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=bop / 1e9, number=dict(suffix="bn", valueformat=".2f"),
            title=dict(text="Sum of BOP_Balance"),
            gauge=dict(axis=dict(range=[0, max(bop * 2 / 1e9, 0.01)]), bar=dict(color=theme["accent"]), bgcolor="#F2F2F2")))
        show(style(fig, theme, 360, legend=False), "dl4")


def page_waterfall(theme):
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
        show(waterfall_fig(wf, theme), "wf1")
    with c2:
        t = wf.copy()
        t.loc[len(t)] = ["Total", t["Cash Flow Amount"].sum()]
        show_df(t.style.format({"Cash Flow Amount": "{:,.2f}"}), height=390)
    c3, c4 = st.columns(2)
    with c3:
        g = loss.groupby("ReportingDate", as_index=False)[["Recoveries_ThisMonth", "CollectionsTotal"]].sum()
        fig = go.Figure()
        fig.add_scatter(x=g["ReportingDate"], y=g["Recoveries_ThisMonth"], name="Recoveries_ThisMonth", line=dict(color=theme["seq"][0]))
        fig.add_scatter(x=g["ReportingDate"], y=g["CollectionsTotal"], name="CollectionsTotal", line=dict(color=theme["seq"][1]))
        fig.update_layout(title="Recoveries and Collections Total by ReportingDate", yaxis_tickformat=".2s")
        show(style(fig, theme, 320), "wf2")
    with c4:
        show(line_by(loss, "ReportingDate", "ExcessSpread_Monthly", "Excess Spread Monthly by ReportingDate", theme, area=True), "wf3")


def page_investor(theme):
    page_title("Investor Reporting Dashboard")
    kpi_row([
        ("Portfolio Balance", money(loans["CurrentBalance"].sum())),
        ("Expected Credit Loss", money(loans["ECL_Provision"].sum())),
        ("Net Loss", money(loss["NetLoss_ThisMonth"].sum())),
        ("Collection Efficiency (avg)", f"{loss['CollectionEfficiency'].mean():.2f}" if len(loss) else "–"),
    ])
    c1, c2 = st.columns(2)
    with c1:
        show(line_by(loss, "ReportingDate", "EOP_Balance", "Portfolio Balance Trend by ReportingDate", theme), "ir1")
    with c2:
        s30 = snaps[snaps["DPD_Days"] >= 30]
        show(line_by(s30, "SnapshotDate", "CurrentBalance", "30+ DPD Exposure by Snapshot Date", theme), "ir2")
    c3, c4 = st.columns(2)
    with c3:
        show(vintage_lines("CumulativeNetLoss", "Cumulative Net Loss by Months on Book and Vintage", theme, 380), "ir3")
    with c4:
        show(waterfall_fig(waterfall_frame(loss), theme, 380), "ir4")


def page_stress(theme):
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
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Baseline ECL", money(base_ecl))
    c2.metric(f"Stressed ECL ({worst['Scenario']})", money(worst["Stress ECL"]))
    c3.metric("ECL Increase", money(worst["ECL Increase"]))
    c4.metric("ECL Increase %", f"{worst['ECL Increase %'] * 100:,.0f}%")

    c1, c2 = st.columns([1, 1.15])
    with c1:
        g = st_df.sort_values("Stress ECL", ascending=False)
        fig = px.bar(g, x="Scenario", y="Stress ECL", text=g["Stress ECL"].map(money), title="Stress ECL by Scenario")
        fig.update_traces(marker_color=theme["bar"], textposition="outside")
        fig.update_layout(yaxis_tickformat=".2s")
        show(style(fig, theme, 380, legend=False), "st1")
    with c2:
        lo, hi = st_df["Stress ECL"].min(), st_df["Stress ECL"].max()

        def heat(v):
            tt = 0 if hi == lo else (v - lo) / (hi - lo)
            return f"background-color: rgb(255,{int(255 * (1 - tt))},0)"

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
        fig.update_traces(marker_color=theme["seq"][2])
        show(style(fig, theme, 340, legend=False), "st2")
    with c4:
        g = st_df.sort_values("Stress LGD")
        fig = px.bar(g, x="Stress LGD", y="Scenario", orientation="h", title="LGD Impact Analysis")
        fig.update_traces(marker_color=theme["seq"][1])
        show(style(fig, theme, 340, legend=False), "st3")


PAGE_RENDERERS = {
    "Executive Summary": page_executive, "Portfolio Overview": page_portfolio, "IFRS-9": page_ifrs9,
    "DPD & Roll Rate": page_dpd, "Vintage": page_vintage, "Dynamic Loss": page_dynamic_loss,
    "Waterfall": page_waterfall, "Investor Reporting": page_investor, "Stress Testing": page_stress,
}

PAGE_RENDERERS[active_page](theme)
