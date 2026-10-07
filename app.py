import sys
import random
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PROJECT PATH
# =========================================================

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from src.data_loader import load_data


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Nexa Bussiness Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# LOAD GLOBAL CSS
# =========================================================

css_file = ROOT / "assets" / "style.css"

if css_file.exists():
    st.html(
        f"<style>{css_file.read_text()}</style>",

    )


# =========================================================
# CACHED DATA LOADER
# =========================================================

@st.cache_data(show_spinner=False)
def get_dashboard_data():
    return load_data()


fact, products, customers, regions, dates = get_dashboard_data()


# =========================================================
# SESSION STATE
# =========================================================

if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = None

if "uploader_version" not in st.session_state:
    st.session_state["uploader_version"] = 0


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # -----------------------------------------------------
    # BRAND
    # -----------------------------------------------------

    st.html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">NEXA BUSSINESS INTELLIGENCE</div>
            <div class="sidebar-brand-subtitle">
                Business Intelligence Suite
            </div>
        </div>
        """,

    )

    st.divider()

    # -----------------------------------------------------
    # NAVIGATION
    # -----------------------------------------------------

    st.page_link(
        "app.py",
        label="Executive Overview",
        icon="🏠"
    )

    st.page_link(
        "pages/1_Sales_Analysis.py",
        label="Sales Performance",
        icon="📈"
    )

    st.page_link(
        "pages/2_Product_Analysis.py",
        label="Product Intelligence",
        icon="📦"
    )

    st.page_link(
        "pages/3_Customer_Analysis.py",
        label="Customer Insights",
        icon="👥"
    )

    st.page_link(
        "pages/4_Regional_Analysis.py",
        label="Regional Performance",
        icon="🌍"
    )

    st.divider()

    # -----------------------------------------------------
    # QUICK STATUS
    # -----------------------------------------------------

    st.html(
        '<div class="sidebar-section-title">QUICK STATUS</div>',

    )

    st.success("Data pipeline connected")

    default_rows = len(fact)
    default_regions = fact["Region"].nunique()

    if st.session_state["uploaded_data"] is not None:
        active_rows = len(st.session_state["uploaded_data"])
        active_regions = (
            st.session_state["uploaded_data"]["Region"].nunique()
            if "Region" in st.session_state["uploaded_data"].columns
            else 0
        )
    else:
        active_rows = default_rows
        active_regions = default_regions

    st.caption(
        f"{active_rows:,} transactions • {active_regions} regions"
    )

    st.divider()

    # -----------------------------------------------------
    # DATA CENTER
    # -----------------------------------------------------

    st.html(
        '<div class="sidebar-section-title">📂 DATA CENTER</div>',

    )

    uploaded_file = st.file_uploader(
        "Upload Sales CSV",
        type=["csv"],
        help="Upload a CSV containing your sales transaction data.",
        key=f"csv_uploader_{st.session_state['uploader_version']}"
    )

    # -----------------------------------------------------
    # PROCESS NEW FILE
    # -----------------------------------------------------

    if uploaded_file is not None:

        try:

            uploaded_data = pd.read_csv(uploaded_file)

            required_columns = {
                "OrderDate",
                "SalesAmount",
                "ProfitAmount",
                "OrderID",
                "CustomerID",
                "Region",
                "Category",
                "SalesChannel",
                "ProductName"
            }

            missing_columns = (
                required_columns
                - set(uploaded_data.columns)
            )

            if missing_columns:

                st.error(
                    "Invalid CSV. Missing columns: "
                    + ", ".join(sorted(missing_columns))
                )

            else:

                uploaded_data["OrderDate"] = pd.to_datetime(
                    uploaded_data["OrderDate"],
                    errors="coerce"
                )

                uploaded_data["SalesAmount"] = pd.to_numeric(
                    uploaded_data["SalesAmount"],
                    errors="coerce"
                )

                uploaded_data["ProfitAmount"] = pd.to_numeric(
                    uploaded_data["ProfitAmount"],
                    errors="coerce"
                )

                uploaded_data = uploaded_data.dropna(
                    subset=[
                        "OrderDate",
                        "SalesAmount",
                        "ProfitAmount"
                    ]
                )

                st.session_state["uploaded_data"] = uploaded_data

                st.success(
                    f"✓ {len(uploaded_data):,} rows loaded"
                )

        except Exception as error:

            st.error(
                f"Unable to read CSV: {error}"
            )

    # -----------------------------------------------------
    # SHOW ACTIVE UPLOAD
    # -----------------------------------------------------

    # -----------------------------------------------------
    # ACTIVE DATASET STATUS
    # -----------------------------------------------------

    if st.session_state["uploaded_data"] is not None:

        active_upload = st.session_state["uploaded_data"]

        st.caption(
            f"Dataset: {active_upload.shape[0]:,} rows × "
            f"{active_upload.shape[1]:,} columns"
        )

        st.success("✓ Uploaded CSV is active")

        with st.expander("🔍 Preview uploaded data"):

            st.dataframe(
                active_upload.head(5),
                use_container_width=True,
                hide_index=True
            )

    else:

        st.caption(
            "Using the default connected dataset."
        )

    # -----------------------------------------------------
    # RESET BUTTON - ALWAYS VISIBLE
    # -----------------------------------------------------

    if st.button(
            "🔄 Reset to Default Data",
            use_container_width=True,
            key="reset_default_data"
    ):
        st.session_state["uploaded_data"] = None
        st.session_state["uploader_version"] += 1

        st.rerun()


# =========================================================
# SELECT ACTIVE DATASET
# =========================================================

if st.session_state["uploaded_data"] is not None:

    df = st.session_state["uploaded_data"].copy()

else:

    df = fact.copy()


# =========================================================
# DATA TYPE SAFETY
# =========================================================

df["OrderDate"] = pd.to_datetime(
    df["OrderDate"],
    errors="coerce"
)

df["SalesAmount"] = pd.to_numeric(
    df["SalesAmount"],
    errors="coerce"
)

df["ProfitAmount"] = pd.to_numeric(
    df["ProfitAmount"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "OrderDate",
        "SalesAmount",
        "ProfitAmount"
    ]
)


# =========================================================
# PAGE HEADER
# =========================================================

header_left, header_right = st.columns(
    [5, 1]
)

with header_left:

    st.html(
        '<div class="hero-title">Executive Sales Overview</div>',

    )

    st.html(
        """
        <div class="hero-subtitle">
            A real-time view of revenue, profitability,
            customers and regional performance.
        </div>
        """,

    )

with header_right:

    st.html(
        '<div class="live-badge">● LIVE ANALYTICS</div>',

    )


# =========================================================
# FILTERS
# =========================================================

st.html(
    '<div class="section-title">Analysis Filters</div>',

)

filter_1, filter_2, filter_3, filter_4 = st.columns(
    [1.7, 1, 1, 1]
)


with filter_1:

    min_date = df["OrderDate"].min().date()
    max_date = df["OrderDate"].max().date()

    date_range = st.date_input(
        "Analysis period",
        value=(min_date, max_date)
    )


with filter_2:

    region_options = sorted(
        df["Region"].dropna().unique()
    )

    selected_regions = st.multiselect(
        "Region",
        region_options,
        default=region_options
    )


with filter_3:

    category_options = sorted(
        df["Category"].dropna().unique()
    )

    selected_categories = st.multiselect(
        "Category",
        category_options,
        default=category_options
    )


with filter_4:

    channel_options = sorted(
        df["SalesChannel"].dropna().unique()
    )

    selected_channels = st.multiselect(
        "Channel",
        channel_options,
        default=channel_options
    )


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()


if isinstance(date_range, tuple) and len(date_range) == 2:

    filtered_df = filtered_df[
        (
            filtered_df["OrderDate"].dt.date
            >= date_range[0]
        )
        &
        (
            filtered_df["OrderDate"].dt.date
            <= date_range[1]
        )
    ]


if selected_regions:

    filtered_df = filtered_df[
        filtered_df["Region"].isin(selected_regions)
    ]


if selected_categories:

    filtered_df = filtered_df[
        filtered_df["Category"].isin(selected_categories)
    ]


if selected_channels:

    filtered_df = filtered_df[
        filtered_df["SalesChannel"].isin(selected_channels)
    ]


# =========================================================
# KPI CALCULATIONS
# =========================================================

sales = filtered_df["SalesAmount"].sum()

profit = filtered_df["ProfitAmount"].sum()

orders = filtered_df["OrderID"].nunique()

customers_count = filtered_df["CustomerID"].nunique()

margin = (
    profit / sales
    if sales
    else 0
)

aov = (
    sales / orders
    if orders
    else 0
)


# =========================================================
# KPI HEADER
# =========================================================

st.html(
    '<div class="section-title">Performance KPIs</div>',

)


kpi_1, kpi_2, kpi_3, kpi_4, kpi_5 = st.columns(5)


def render_kpi(
    container,
    icon,
    label,
    value,
    footer
):
    with container:
        st.html(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    {icon} {label}
                </div>

                <div class="kpi-value">
                    {value}
                </div>

                <div class="kpi-footer">
                    {footer}
                </div>

            </div>
            """
        )

render_kpi(
    kpi_1,
    "💰",
    "Total Revenue",
    f"${sales:,.0f}",
    "Current selection"
)

render_kpi(
    kpi_2,
    "📈",
    "Net Profit",
    f"${profit:,.0f}",
    f"{margin:.1%} margin"
)

render_kpi(
    kpi_3,
    "🧾",
    "Orders",
    f"{orders:,}",
    "Unique transactions"
)

render_kpi(
    kpi_4,
    "👥",
    "Customers",
    f"{customers_count:,}",
    "Active customers"
)

render_kpi(
    kpi_5,
    "🎯",
    "Avg. Order Value",
    f"${aov:,.2f}",
    "Revenue / order"
)


# =========================================================
# CHART DATA
# =========================================================

monthly = (
    filtered_df
    .assign(
        Month=filtered_df["OrderDate"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    .groupby("Month", as_index=False)
    .agg(
        Revenue=("SalesAmount", "sum"),
        Profit=("ProfitAmount", "sum")
    )
)


regional = (
    filtered_df
    .groupby("Region", as_index=False)
    .agg(
        Revenue=("SalesAmount", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)


top_products = (
    filtered_df
    .groupby("ProductName", as_index=False)
    .agg(
        Revenue=("SalesAmount", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
    .head(7)
)


category_data = (
    filtered_df
    .groupby("Category", as_index=False)
    .agg(
        Revenue=("SalesAmount", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)


# =========================================================
# REVENUE & PROFIT TREND
# =========================================================

chart_left, chart_right = st.columns(
    [1.55, 1]
)


with chart_left:

    st.html(
        """
        <div class="panel">

            <div class="panel-title">
                Revenue & Profit Trend
            </div>

            <div class="panel-subtitle">
                Monthly performance across the selected period
            </div>

        </div>
        """,
    )

    fig = px.bar(
        monthly,
        x="Month",
        y="Revenue"
    )

    fig.update_traces(
        marker_color="#1674D1"
    )

    fig.add_scatter(
        x=monthly["Month"],
        y=monthly["Profit"],
        mode="lines+markers",
        name="Profit",
        line=dict(
            color="#28B67A",
            width=3
        ),
        marker=dict(
            size=6
        )
    )

    fig.update_layout(
        height=350,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_title="",
        yaxis_title="Revenue",
        font=dict(
            color="#24496F"
        ),
        xaxis=dict(
            gridcolor="#EDF1F5"
        ),
        yaxis=dict(
            gridcolor="#EDF1F5"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# =========================================================
# REGIONAL REVENUE MIX
# =========================================================

with chart_right:

    st.html(
        """
        <div class="panel">

            <div class="panel-title">
                Regional Revenue Mix
            </div>

            <div class="panel-subtitle">
                Contribution by market region
            </div>

        </div>
        """,
    )

    fig_region = px.pie(
        regional,
        names="Region",
        values="Revenue",
        hole=0.62
    )

    fig_region.update_traces(
        textinfo="percent",
        textposition="outside"
    )

    fig_region.update_layout(
        height=350,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        font=dict(
            color="#24496F"
        )
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# =========================================================
# TOP PRODUCTS
# =========================================================

product_left, category_right = st.columns(
    2
)


with product_left:

    st.html(
        """
        <div class="panel">

            <div class="panel-title">
                Top Products
            </div>

            <div class="panel-subtitle">
                Highest revenue-generating products
            </div>

        </div>
        """,
    )

    fig_product = px.bar(
        top_products,
        x="Revenue",
        y="ProductName",
        orientation="h"
    )

    fig_product.update_traces(
        marker_color="#2F80ED"
    )

    fig_product.update_layout(
        height=330,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="Revenue",
        yaxis_title="",
        font=dict(
            color="#24496F"
        ),
        xaxis=dict(
            gridcolor="#EDF1F5"
        ),
        yaxis=dict(
            categoryorder="total ascending"
        )
    )

    st.plotly_chart(
        fig_product,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# =========================================================
# CATEGORY PERFORMANCE
# =========================================================

with category_right:

    st.html(
        """
        <div class="panel">

            <div class="panel-title">
                Category Performance
            </div>

            <div class="panel-subtitle">
                Revenue contribution by category
            </div>

        </div>
        """,
    )

    fig_category = px.bar(
        category_data,
        x="Category",
        y="Revenue"
    )

    fig_category.update_traces(
        marker_color="#28B67A"
    )

    fig_category.update_layout(
        height=330,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="",
        yaxis_title="Revenue",
        font=dict(
            color="#24496F"
        ),
        xaxis=dict(
            gridcolor="#EDF1F5"
        ),
        yaxis=dict(
            gridcolor="#EDF1F5"
        )
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# =========================================================
# AUTOMATED BUSINESS INSIGHTS
# =========================================================

st.html(
    '<div class="section-title">Automated Business Insights</div>',

)


if len(filtered_df) > 0:

    best_region = (
        filtered_df
        .groupby("Region")["SalesAmount"]
        .sum()
        .idxmax()
    )

    best_category = (
        filtered_df
        .groupby("Category")["SalesAmount"]
        .sum()
        .idxmax()
    )

    best_product = (
        filtered_df
        .groupby("ProductName")["SalesAmount"]
        .sum()
        .idxmax()
    )

    online_revenue = filtered_df.loc[
        filtered_df["SalesChannel"].eq("Online"),
        "SalesAmount"
    ].sum()

    online_share = (
        online_revenue / sales
        if sales
        else 0
    )

else:

    best_region = "N/A"
    best_category = "N/A"
    best_product = "N/A"
    online_share = 0


insight_1, insight_2, insight_3, insight_4 = st.columns(4)


def render_insight(
    container,
    title,
    text
):

    with container:

        st.html(
            f"""
            <div class="insight-card">

                <div class="insight-title">
                    {title}
                </div>

                <div class="insight-text">
                    {text}
                </div>

            </div>
            """,

        )


render_insight(
    insight_1,
    "Market Leader",
    f"{best_region} is the largest revenue market in this selection."
)

render_insight(
    insight_2,
    "Category Leader",
    f"{best_category} generates the highest category revenue."
)

render_insight(
    insight_3,
    "Product Leader",
    f"{best_product} is the strongest product by revenue."
)

render_insight(
    insight_4,
    "Digital Share",
    f"Online sales represent {online_share:.1%} of selected revenue."
)


# =========================================================
# FOOTER
# =========================================================

st.html(
    """
    <div class="dashboard-footer">
        Nexa Bussiness Intelligence • Final Year Data Analytics Project
        • Python + Streamlit + Pandas + Plotly
    </div>
    """,

)