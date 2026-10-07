import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Product Intelligence | Nexa Business Intelligence",
    page_icon="📦",
    layout="wide"
)

# --------------------------------------------------
# PROJECT PATH
# --------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data_loader import load_data

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
fact, products, customers, regions, dates = load_data()

# --------------------------------------------------
# LOAD PROJECT CSS
# --------------------------------------------------
css_file = ROOT / "assets" / "style.css"

if css_file.exists():
    st.markdown(
        f"<style>{css_file.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:

    st.markdown("## NEXA BUSSINESS INTELLIGENCE")
    st.caption("Business Intelligence Suite")

    st.divider()

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

    st.caption("QUICK STATUS")

    st.success("Data pipeline connected")

    st.caption(
        f"{fact['OrderID'].nunique():,} transactions • "
        f"{fact['Region'].nunique()} regions"
    )

# --------------------------------------------------
# HEADER
# --------------------------------------------------
header_col, status_col = st.columns([5, 1])

with header_col:

    st.title("Product Intelligence")

    st.caption(
        "Understand product revenue, profitability, category performance "
        "and product-level business contribution."
    )

with status_col:

    st.info("● LIVE ANALYTICS")

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.subheader("Product Analysis Filters")

f1, f2, f3, f4 = st.columns(4)

with f1:

    date_range = st.date_input(
        "Analysis Period",
        value=(
            fact["OrderDate"].min().date(),
            fact["OrderDate"].max().date()
        )
    )

with f2:

    region_options = sorted(
        fact["Region"].dropna().unique()
    )

    selected_regions = st.multiselect(
        "Region",
        region_options,
        default=region_options
    )

with f3:

    category_options = sorted(
        fact["Category"].dropna().unique()
    )

    selected_categories = st.multiselect(
        "Category",
        category_options,
        default=category_options
    )

with f4:

    channel_options = sorted(
        fact["SalesChannel"].dropna().unique()
    )

    selected_channels = st.multiselect(
        "Sales Channel",
        channel_options,
        default=channel_options
    )

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------
df = fact.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:

    df = df[
        (df["OrderDate"].dt.date >= date_range[0])
        &
        (df["OrderDate"].dt.date <= date_range[1])
    ]

if selected_regions:
    df = df[
        df["Region"].isin(selected_regions)
    ]

if selected_categories:
    df = df[
        df["Category"].isin(selected_categories)
    ]

if selected_channels:
    df = df[
        df["SalesChannel"].isin(selected_channels)
    ]

# --------------------------------------------------
# PRODUCT METRICS
# --------------------------------------------------
total_products = df["ProductName"].nunique()

total_revenue = df["SalesAmount"].sum()

total_profit = df["ProfitAmount"].sum()

average_product_revenue = (
    total_revenue / total_products
    if total_products
    else 0
)

profit_margin = (
    total_profit / total_revenue
    if total_revenue
    else 0
)

# Best product
if not df.empty:

    product_sales = (
        df.groupby("ProductName")["SalesAmount"]
        .sum()
        .sort_values(ascending=False)
    )

    best_product = product_sales.index[0]

    best_product_revenue = product_sales.iloc[0]

else:

    best_product = "N/A"
    best_product_revenue = 0

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("Product Performance KPIs")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:

    st.metric(
        "📦 Total Products",
        f"{total_products:,}"
    )

with k2:

    st.metric(
        "💰 Product Revenue",
        f"${total_revenue:,.0f}"
    )

with k3:

    st.metric(
        "📈 Product Profit",
        f"${total_profit:,.0f}"
    )

with k4:

    st.metric(
        "🎯 Avg. Product Revenue",
        f"${average_product_revenue:,.0f}"
    )

with k5:

    st.metric(
        "🏆 Top Product",
        best_product
    )

# --------------------------------------------------
# PRODUCT REVENUE RANKING
# --------------------------------------------------
st.divider()

chart1, chart2 = st.columns([1.5, 1])

with chart1:

    st.subheader("🏆 Product Revenue Ranking")

    st.caption(
        "Top products ranked by revenue contribution"
    )

    product_revenue = (
        df.groupby(
            "ProductName",
            as_index=False
        )
        .agg(
            Revenue=("SalesAmount", "sum"),
            Profit=("ProfitAmount", "sum")
        )
        .sort_values(
            "Revenue",
            ascending=False
        )
        .head(10)
    )

    product_revenue_plot = product_revenue.sort_values(
        "Revenue",
        ascending=True
    )

    if not product_revenue_plot.empty:

        fig = px.bar(
            product_revenue_plot,
            x="Revenue",
            y="ProductName",
            orientation="h",
            labels={
                "Revenue": "Revenue",
                "ProductName": ""
            }
        )

        fig.update_traces(
            marker_color="#2F80ED"
        )

        fig.update_layout(
            height=430,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

# --------------------------------------------------
# CATEGORY MIX
# --------------------------------------------------
with chart2:

    st.subheader("📊 Category Revenue Mix")

    st.caption(
        "Revenue contribution by product category"
    )

    category_mix = (
        df.groupby(
            "Category",
            as_index=False
        )["SalesAmount"]
        .sum()
        .sort_values(
            "SalesAmount",
            ascending=False
        )
    )

    if not category_mix.empty:

        fig = px.pie(
            category_mix,
            names="Category",
            values="SalesAmount",
            hole=0.62
        )

        fig.update_traces(
            textinfo="percent"
        )

        fig.update_layout(
            height=430,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

# --------------------------------------------------
# PROFITABILITY ANALYSIS
# --------------------------------------------------
st.divider()

profit_col, category_col = st.columns(2)

# --------------------------------------------------
# PRODUCT PROFITABILITY
# --------------------------------------------------
with profit_col:

    st.subheader("💹 Product Profitability")

    st.caption(
        "Revenue compared with profit for leading products"
    )

    profitability = (
        df.groupby(
            "ProductName",
            as_index=False
        )
        .agg(
            Revenue=("SalesAmount", "sum"),
            Profit=("ProfitAmount", "sum")
        )
        .sort_values(
            "Revenue",
            ascending=False
        )
        .head(10)
    )

    if not profitability.empty:

        fig = px.scatter(
            profitability,
            x="Revenue",
            y="Profit",
            size="Revenue",
            hover_name="ProductName",
            labels={
                "Revenue": "Revenue",
                "Profit": "Profit"
            }
        )

        fig.update_layout(
            height=400,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

# --------------------------------------------------
# CATEGORY PROFITABILITY
# --------------------------------------------------
with category_col:

    st.subheader("📦 Category Performance")

    st.caption(
        "Revenue and profit contribution across categories"
    )

    category_performance = (
        df.groupby(
            "Category",
            as_index=False
        )
        .agg(
            Revenue=("SalesAmount", "sum"),
            Profit=("ProfitAmount", "sum")
        )
    )

    if not category_performance.empty:

        fig = px.bar(
            category_performance,
            x="Category",
            y=["Revenue", "Profit"],
            barmode="group",
            labels={
                "value": "Amount",
                "Category": "",
                "variable": ""
            }
        )

        fig.update_layout(
            height=400,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

# --------------------------------------------------
# PRODUCT TABLE
# --------------------------------------------------
st.divider()

st.subheader("📋 Product Portfolio")

st.caption(
    "Detailed product-level revenue and profitability analysis"
)

product_table = (
    df.groupby(
        "ProductName",
        as_index=False
    )
    .agg(
        Revenue=("SalesAmount", "sum"),
        Profit=("ProfitAmount", "sum"),
        Orders=("OrderID", "nunique")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

if not product_table.empty:

    product_table["Profit Margin"] = (
        product_table["Profit"]
        / product_table["Revenue"]
    )

    product_table.insert(
        0,
        "Rank",
        range(1, len(product_table) + 1)
    )

    product_table["Revenue"] = (
        product_table["Revenue"]
        .map(lambda x: f"${x:,.0f}")
    )

    product_table["Profit"] = (
        product_table["Profit"]
        .map(lambda x: f"${x:,.0f}")
    )

    product_table["Profit Margin"] = (
        product_table["Profit Margin"]
        .map(lambda x: f"{x:.1%}")
    )

    product_table = product_table.rename(
        columns={
            "ProductName": "Product"
        }
    )

    st.dataframe(
        product_table[
            [
                "Rank",
                "Product",
                "Revenue",
                "Profit",
                "Profit Margin",
                "Orders"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=430
    )

# --------------------------------------------------
# AUTOMATED PRODUCT INSIGHTS
# --------------------------------------------------
st.divider()

st.subheader("💡 Automated Product Insights")

if not df.empty:

    # Best revenue product
    best_product = (
        df.groupby("ProductName")["SalesAmount"]
        .sum()
        .idxmax()
    )

    # Most profitable product
    most_profitable = (
        df.groupby("ProductName")["ProfitAmount"]
        .sum()
        .idxmax()
    )

    # Best category
    best_category = (
        df.groupby("Category")["SalesAmount"]
        .sum()
        .idxmax()
    )

    # Highest margin product
    margin_data = (
        df.groupby("ProductName")
        .agg(
            Revenue=("SalesAmount", "sum"),
            Profit=("ProfitAmount", "sum")
        )
    )

    margin_data["Margin"] = (
        margin_data["Profit"]
        / margin_data["Revenue"]
    )

    highest_margin_product = (
        margin_data["Margin"]
        .idxmax()
    )

    i1, i2, i3, i4 = st.columns(4)

    with i1:

        st.info(
            f"🏆 **Revenue Leader**\n\n"
            f"{best_product} generates the highest revenue."
        )

    with i2:

        st.info(
            f"💰 **Profit Leader**\n\n"
            f"{most_profitable} generates the highest profit."
        )

    with i3:

        st.info(
            f"📦 **Category Leader**\n\n"
            f"{best_category} contributes the most revenue."
        )

    with i4:

        st.info(
            f"💹 **Margin Leader**\n\n"
            f"{highest_margin_product} has the highest profit margin."
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "Nexa Bussiness Intelligence • Product Intelligence Module • "
    "Python + Streamlit + Pandas + Plotly"
)