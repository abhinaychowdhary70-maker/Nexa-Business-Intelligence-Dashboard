import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Sales Performance | Nexa Bussiness Intelligence",
    page_icon="📈",
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
# LOAD EXISTING DESIGN
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
title_col, status_col = st.columns([5, 1])

with title_col:

    st.title("Sales Performance")

    st.caption(
        "Analyze revenue, profitability, orders and sales-channel performance."
    )

with status_col:

    st.info("● LIVE ANALYTICS")

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.subheader("Analysis Filters")

filter1, filter2, filter3, filter4 = st.columns(4)

with filter1:

    date_range = st.date_input(
        "Analysis Period",
        value=(
            fact["OrderDate"].min().date(),
            fact["OrderDate"].max().date()
        )
    )

with filter2:

    region_options = sorted(
        fact["Region"].dropna().unique()
    )

    selected_regions = st.multiselect(
        "Region",
        region_options,
        default=region_options
    )

with filter3:

    category_options = sorted(
        fact["Category"].dropna().unique()
    )

    selected_categories = st.multiselect(
        "Category",
        category_options,
        default=category_options
    )

with filter4:

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
    df = df[df["Region"].isin(selected_regions)]

if selected_categories:
    df = df[df["Category"].isin(selected_categories)]

if selected_channels:
    df = df[df["SalesChannel"].isin(selected_channels)]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_sales = df["SalesAmount"].sum()

total_profit = df["ProfitAmount"].sum()

total_orders = df["OrderID"].nunique()

profit_margin = (
    total_profit / total_sales
    if total_sales
    else 0
)

average_order_value = (
    total_sales / total_orders
    if total_orders
    else 0
)

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("Sales Performance KPIs")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric(
        "💰 Total Revenue",
        f"${total_sales:,.0f}"
    )

with k2:
    st.metric(
        "📈 Net Profit",
        f"${total_profit:,.0f}"
    )

with k3:
    st.metric(
        "🧾 Total Orders",
        f"{total_orders:,}"
    )

with k4:
    st.metric(
        "💹 Profit Margin",
        f"{profit_margin:.1%}"
    )

with k5:
    st.metric(
        "🎯 Avg. Order Value",
        f"${average_order_value:,.2f}"
    )

# --------------------------------------------------
# MONTHLY DATA
# --------------------------------------------------
monthly = (
    df.assign(
        Month=df["OrderDate"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    .groupby("Month", as_index=False)
    .agg(
        Sales=("SalesAmount", "sum"),
        Profit=("ProfitAmount", "sum")
    )
)

# --------------------------------------------------
# ROW 1
# --------------------------------------------------
st.divider()

chart1, chart2 = st.columns([1.55, 1])

# --------------------------------------------------
# REVENUE / PROFIT TREND
# --------------------------------------------------
with chart1:

    st.subheader("📈 Revenue & Profit Trend")

    st.caption(
        "Monthly sales and profitability performance"
    )

    if not monthly.empty:

        fig = px.bar(
            monthly,
            x="Month",
            y="Sales",
            labels={
                "Sales": "Revenue",
                "Month": ""
            }
        )

        fig.update_traces(
            marker_color="#75B8F5",
            name="Revenue"
        )

        profit_fig = px.line(
            monthly,
            x="Month",
            y="Profit"
        )

        for trace in profit_fig.data:

            trace.update(
                line=dict(
                    color="#20B486",
                    width=3
                ),
                name="Profit"
            )

            fig.add_trace(trace)

        fig.update_layout(
            height=380,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

# --------------------------------------------------
# CHANNEL MIX
# --------------------------------------------------
with chart2:

    st.subheader("🛒 Sales Channel Mix")

    st.caption(
        "Revenue contribution by sales channel"
    )

    channel_data = (
        df.groupby(
            "SalesChannel",
            as_index=False
        )["SalesAmount"]
        .sum()
        .sort_values(
            "SalesAmount",
            ascending=False
        )
    )

    if not channel_data.empty:

        fig = px.pie(
            channel_data,
            names="SalesChannel",
            values="SalesAmount",
            hole=0.65
        )

        fig.update_traces(
            textinfo="percent"
        )

        fig.update_layout(
            height=380,
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
# ROW 2
# --------------------------------------------------
st.divider()

region_col, category_col = st.columns(2)

# --------------------------------------------------
# REGIONAL PERFORMANCE
# --------------------------------------------------
with region_col:

    st.subheader("🌍 Regional Sales Performance")

    st.caption(
        "Revenue generated across geographic markets"
    )

    regional = (
        df.groupby(
            "Region",
            as_index=False
        )
        .agg(
            Sales=("SalesAmount", "sum"),
            Profit=("ProfitAmount", "sum")
        )
        .sort_values(
            "Sales",
            ascending=True
        )
    )

    if not regional.empty:

        fig = px.bar(
            regional,
            x="Sales",
            y="Region",
            orientation="h",
            labels={
                "Sales": "Revenue",
                "Region": ""
            }
        )

        fig.update_traces(
            marker_color="#2F80ED"
        )

        fig.update_layout(
            height=360,
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
# CATEGORY PERFORMANCE
# --------------------------------------------------
with category_col:

    st.subheader("📦 Category Revenue")

    st.caption(
        "Revenue contribution across product categories"
    )

    category_data = (
        df.groupby(
            "Category",
            as_index=False
        )
        .agg(
            Sales=("SalesAmount", "sum"),
            Profit=("ProfitAmount", "sum")
        )
        .sort_values(
            "Sales",
            ascending=True
        )
    )

    if not category_data.empty:

        fig = px.bar(
            category_data,
            x="Sales",
            y="Category",
            orientation="h",
            labels={
                "Sales": "Revenue",
                "Category": ""
            }
        )

        fig.update_traces(
            marker_color="#5CA9F8"
        )

        fig.update_layout(
            height=360,
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
# TOP PRODUCTS
# --------------------------------------------------
st.divider()

st.subheader("🏆 Top 10 Products")

st.caption(
    "Highest revenue-generating products in the selected period"
)

top_products = (
    df.groupby(
        "ProductName",
        as_index=False
    )
    .agg(
        Sales=("SalesAmount", "sum"),
        Profit=("ProfitAmount", "sum")
    )
    .sort_values(
        "Sales",
        ascending=False
    )
    .head(10)
)

if not top_products.empty:

    top_products["Profit Margin"] = (
        top_products["Profit"]
        / top_products["Sales"]
    )

    display_products = top_products.copy()

    display_products.insert(
        0,
        "Rank",
        range(1, len(display_products) + 1)
    )

    display_products["Sales"] = (
        display_products["Sales"]
        .map(lambda x: f"${x:,.0f}")
    )

    display_products["Profit"] = (
        display_products["Profit"]
        .map(lambda x: f"${x:,.0f}")
    )

    display_products["Profit Margin"] = (
        display_products["Profit Margin"]
        .map(lambda x: f"{x:.1%}")
    )

    display_products = display_products.rename(
        columns={
            "ProductName": "Product",
            "Sales": "Revenue"
        }
    )

    st.dataframe(
        display_products[
            [
                "Rank",
                "Product",
                "Revenue",
                "Profit",
                "Profit Margin"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=390
    )

# --------------------------------------------------
# AUTOMATED INSIGHTS
# --------------------------------------------------
st.divider()

st.subheader("💡 Automated Sales Insights")

if not df.empty:

    best_region = (
        df.groupby("Region")["SalesAmount"]
        .sum()
        .idxmax()
    )

    best_category = (
        df.groupby("Category")["SalesAmount"]
        .sum()
        .idxmax()
    )

    best_channel = (
        df.groupby("SalesChannel")["SalesAmount"]
        .sum()
        .idxmax()
    )

    best_product = (
        df.groupby("ProductName")["SalesAmount"]
        .sum()
        .idxmax()
    )

    online_share = (
        df.loc[
            df["SalesChannel"] == "Online",
            "SalesAmount"
        ].sum()
        / total_sales
        if total_sales
        else 0
    )

    i1, i2, i3, i4 = st.columns(4)

    with i1:
        st.info(
            f"🌍 **Regional Leader**\n\n"
            f"{best_region} generates the highest revenue."
        )

    with i2:
        st.info(
            f"📦 **Category Leader**\n\n"
            f"{best_category} is the strongest category."
        )

    with i3:
        st.info(
            f"🛒 **Channel Leader**\n\n"
            f"{best_channel} contributes the most revenue."
        )

    with i4:
        st.info(
            f"🏆 **Product Leader**\n\n"
            f"{best_product} is the top product by revenue."
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "Nexa Bussiness Intelligence • Sales Performance Module • "
    "Python + Streamlit + Pandas + Plotly"
)