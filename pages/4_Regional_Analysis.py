import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Regional Performance | Nexa Bussiness Intelligence",
    page_icon="🌍",
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
header, status = st.columns([5, 1])

with header:

    st.title("Regional Performance")

    st.caption(
        "Analyze revenue, profitability, customers and sales "
        "performance across geographic markets."
    )

with status:

    st.info("● LIVE ANALYTICS")

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.subheader("Regional Analysis Filters")

f1, f2, f3 = st.columns(3)

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

# --------------------------------------------------
# REGIONAL KPIs
# --------------------------------------------------
total_revenue = df["SalesAmount"].sum()

total_profit = df["ProfitAmount"].sum()

total_orders = df["OrderID"].nunique()

total_customers = df["CustomerID"].nunique()

profit_margin = (
    total_profit / total_revenue
    if total_revenue
    else 0
)

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("Regional Performance KPIs")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:

    st.metric(
        "💰 Total Revenue",
        f"${total_revenue:,.0f}"
    )

with k2:

    st.metric(
        "📈 Total Profit",
        f"${total_profit:,.0f}"
    )

with k3:

    st.metric(
        "🛒 Total Orders",
        f"{total_orders:,}"
    )

with k4:

    st.metric(
        "👥 Customers",
        f"{total_customers:,}"
    )

with k5:

    st.metric(
        "🎯 Profit Margin",
        f"{profit_margin:.1%}"
    )

# --------------------------------------------------
# REGIONAL PERFORMANCE DATA
# --------------------------------------------------
regional = (
    df.groupby("Region", as_index=False)
    .agg(
        Revenue=("SalesAmount", "sum"),
        Profit=("ProfitAmount", "sum"),
        Orders=("OrderID", "nunique"),
        Customers=("CustomerID", "nunique")
    )
)

if not regional.empty:

    regional["Profit Margin"] = (
        regional["Profit"]
        / regional["Revenue"]
    )

    regional["Avg Order Value"] = (
        regional["Revenue"]
        / regional["Orders"]
    )

# --------------------------------------------------
# REGIONAL REVENUE
# --------------------------------------------------
st.divider()

c1, c2 = st.columns([1.5, 1])

with c1:

    st.subheader("🌍 Revenue by Region")

    st.caption(
        "Revenue contribution across geographic markets"
    )

    if not regional.empty:

        plot_data = regional.sort_values(
            "Revenue",
            ascending=True
        )

        fig = px.bar(
            plot_data,
            x="Revenue",
            y="Region",
            orientation="h",
            labels={
                "Revenue": "Revenue",
                "Region": ""
            },
            text="Revenue"
        )

        fig.update_traces(
            texttemplate="$%{text:,.0f}",
            textposition="outside"
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
# REGIONAL MIX
# --------------------------------------------------
with c2:

    st.subheader("🥧 Regional Revenue Mix")

    st.caption(
        "Percentage contribution by market"
    )

    if not regional.empty:

        fig = px.pie(
            regional,
            names="Region",
            values="Revenue",
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
# PROFITABILITY & CUSTOMERS
# --------------------------------------------------
st.divider()

c3, c4 = st.columns(2)

with c3:

    st.subheader("📈 Regional Profitability")

    st.caption(
        "Compare revenue and profit across regions"
    )

    if not regional.empty:

        fig = px.bar(
            regional,
            x="Region",
            y=["Revenue", "Profit"],
            barmode="group",
            labels={
                "value": "Amount",
                "Region": "",
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

with c4:

    st.subheader("👥 Customers by Region")

    st.caption(
        "Customer distribution across geographic markets"
    )

    if not regional.empty:

        customer_plot = regional.sort_values(
            "Customers",
            ascending=True
        )

        fig = px.bar(
            customer_plot,
            x="Customers",
            y="Region",
            orientation="h",
            labels={
                "Customers": "Customers",
                "Region": ""
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
# REGIONAL PERFORMANCE TABLE
# --------------------------------------------------
st.divider()

st.subheader("📋 Regional Performance Table")

st.caption(
    "Detailed performance metrics for each geographic market"
)

if not regional.empty:

    regional_table = regional.copy()

    regional_table.insert(
        0,
        "Rank",
        regional_table["Revenue"]
        .rank(
            ascending=False,
            method="first"
        )
        .astype(int)
    )

    regional_table = regional_table.sort_values(
        "Rank"
    )

    regional_table["Revenue"] = (
        regional_table["Revenue"]
        .map(lambda x: f"${x:,.0f}")
    )

    regional_table["Profit"] = (
        regional_table["Profit"]
        .map(lambda x: f"${x:,.0f}")
    )

    regional_table["Profit Margin"] = (
        regional_table["Profit Margin"]
        .map(lambda x: f"{x:.1%}")
    )

    regional_table["Avg Order Value"] = (
        regional_table["Avg Order Value"]
        .map(lambda x: f"${x:,.0f}")
    )

    st.dataframe(
        regional_table[
            [
                "Rank",
                "Region",
                "Revenue",
                "Profit",
                "Profit Margin",
                "Orders",
                "Customers",
                "Avg Order Value"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=300
    )

# --------------------------------------------------
# TOP REGION ANALYSIS
# --------------------------------------------------
st.divider()

st.subheader("🔎 Regional Business Analysis")

if not regional.empty:

    top_revenue_region = (
        regional.loc[
            regional["Revenue"].idxmax(),
            "Region"
        ]
    )

    top_profit_region = (
        regional.loc[
            regional["Profit"].idxmax(),
            "Region"
        ]
    )

    top_customer_region = (
        regional.loc[
            regional["Customers"].idxmax(),
            "Region"
        ]
    )

    highest_margin_region = (
        regional.loc[
            regional["Profit Margin"].idxmax(),
            "Region"
        ]
    )

    i1, i2, i3, i4 = st.columns(4)

    with i1:

        st.info(
            f"🌍 **Revenue Leader**\n\n"
            f"{top_revenue_region} generates the highest revenue."
        )

    with i2:

        st.info(
            f"💰 **Profit Leader**\n\n"
            f"{top_profit_region} generates the highest profit."
        )

    with i3:

        st.info(
            f"👥 **Customer Leader**\n\n"
            f"{top_customer_region} has the largest customer base."
        )

    with i4:

        st.info(
            f"🎯 **Margin Leader**\n\n"
            f"{highest_margin_region} has the highest profit margin."
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "Nexa Bussiness Intelligence • Regional Performance Module • "
    "Python + Streamlit + Pandas + Plotly"
)