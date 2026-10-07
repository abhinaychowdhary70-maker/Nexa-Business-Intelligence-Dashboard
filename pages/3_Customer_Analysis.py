import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Customer Insights | Nexa Bussiness Intelligence",
    page_icon="👥",
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
c1, c2 = st.columns([5, 1])

with c1:

    st.title("Customer Insights")

    st.caption(
        "Understand customer behavior, purchasing patterns, "
        "revenue contribution and customer value."
    )

with c2:

    st.info("● LIVE ANALYTICS")

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.subheader("Customer Analysis Filters")

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

    regions_list = sorted(
        fact["Region"].dropna().unique()
    )

    selected_regions = st.multiselect(
        "Region",
        regions_list,
        default=regions_list
    )

with f3:

    channels_list = sorted(
        fact["SalesChannel"].dropna().unique()
    )

    selected_channels = st.multiselect(
        "Sales Channel",
        channels_list,
        default=channels_list
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

if selected_channels:

    df = df[
        df["SalesChannel"].isin(selected_channels)
    ]

# --------------------------------------------------
# CUSTOMER KPIs
# --------------------------------------------------
total_customers = df["CustomerID"].nunique()

total_revenue = df["SalesAmount"].sum()

total_profit = df["ProfitAmount"].sum()

total_orders = df["OrderID"].nunique()

avg_customer_value = (
    total_revenue / total_customers
    if total_customers
    else 0
)

orders_per_customer = (
    total_orders / total_customers
    if total_customers
    else 0
)

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("Customer Performance KPIs")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:

    st.metric(
        "👥 Total Customers",
        f"{total_customers:,}"
    )

with k2:

    st.metric(
        "💰 Customer Revenue",
        f"${total_revenue:,.0f}"
    )

with k3:

    st.metric(
        "🛒 Total Orders",
        f"{total_orders:,}"
    )

with k4:

    st.metric(
        "🎯 Avg. Customer Value",
        f"${avg_customer_value:,.0f}"
    )

with k5:

    st.metric(
        "🔄 Orders / Customer",
        f"{orders_per_customer:.1f}"
    )

# --------------------------------------------------
# CUSTOMER REVENUE ANALYSIS
# --------------------------------------------------
st.divider()

c1, c2 = st.columns([1.5, 1])

with c1:

    st.subheader("💰 Top Customers by Revenue")

    st.caption(
        "Highest-value customers based on total revenue"
    )

    customer_revenue = (
        df.groupby("CustomerID", as_index=False)
        .agg(
            Revenue=("SalesAmount", "sum"),
            Profit=("ProfitAmount", "sum"),
            Orders=("OrderID", "nunique")
        )
        .sort_values(
            "Revenue",
            ascending=False
        )
        .head(10)
    )

    if not customer_revenue.empty:

        customer_revenue["Customer"] = (
            "Customer "
            + customer_revenue["CustomerID"].astype(str)
        )

        plot_data = customer_revenue.sort_values(
            "Revenue",
            ascending=True
        )

        fig = px.bar(
            plot_data,
            x="Revenue",
            y="Customer",
            orientation="h",
            labels={
                "Revenue": "Revenue",
                "Customer": ""
            }
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
# CUSTOMER SEGMENT
# --------------------------------------------------
with c2:

    st.subheader("👥 Customer Value Mix")

    st.caption(
        "Customers grouped by revenue contribution"
    )

    customer_values = (
        df.groupby("CustomerID")["SalesAmount"]
        .sum()
    )

    if not customer_values.empty:

        segments = pd.cut(
            customer_values,
            bins=[
                -float("inf"),
                5000,
                15000,
                30000,
                float("inf")
            ],
            labels=[
                "Low Value",
                "Medium Value",
                "High Value",
                "Premium Value"
            ]
        )

        segment_counts = (
            segments.value_counts()
            .reset_index()
        )

        segment_counts.columns = [
            "Segment",
            "Customers"
        ]

        fig = px.pie(
            segment_counts,
            names="Segment",
            values="Customers",
            hole=0.60
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
# CUSTOMER ORDER BEHAVIOR
# --------------------------------------------------
st.divider()

b1, b2 = st.columns(2)

with b1:

    st.subheader("🛒 Orders per Customer")

    st.caption(
        "Distribution of customer purchasing frequency"
    )

    order_frequency = (
        df.groupby("CustomerID")["OrderID"]
        .nunique()
        .reset_index(
            name="Orders"
        )
    )

    if not order_frequency.empty:

        fig = px.histogram(
            order_frequency,
            x="Orders",
            nbins=15,
            labels={
                "Orders": "Orders per Customer"
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

with b2:

    st.subheader("🌍 Customer Revenue by Region")

    st.caption(
        "Customer revenue contribution across markets"
    )

    regional_customers = (
        df.groupby("Region", as_index=False)
        .agg(
            Revenue=("SalesAmount", "sum"),
            Customers=("CustomerID", "nunique")
        )
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    if not regional_customers.empty:

        fig = px.bar(
            regional_customers,
            x="Region",
            y="Revenue",
            labels={
                "Revenue": "Revenue",
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
# CUSTOMER TABLE
# --------------------------------------------------
st.divider()

st.subheader("📋 Customer Portfolio")

st.caption(
    "Detailed customer-level revenue and purchasing analysis"
)

customer_table = (
    df.groupby("CustomerID", as_index=False)
    .agg(
        Revenue=("SalesAmount", "sum"),
        Profit=("ProfitAmount", "sum"),
        Orders=("OrderID", "nunique"),
        Region=("Region", "first")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

if not customer_table.empty:

    customer_table.insert(
        0,
        "Rank",
        range(1, len(customer_table) + 1)
    )

    customer_table["Customer"] = (
        "Customer "
        + customer_table["CustomerID"].astype(str)
    )

    customer_table["Avg Order Value"] = (
        customer_table["Revenue"]
        / customer_table["Orders"]
    )

    customer_table["Revenue"] = (
        customer_table["Revenue"]
        .map(lambda x: f"${x:,.0f}")
    )

    customer_table["Profit"] = (
        customer_table["Profit"]
        .map(lambda x: f"${x:,.0f}")
    )

    customer_table["Avg Order Value"] = (
        customer_table["Avg Order Value"]
        .map(lambda x: f"${x:,.0f}")
    )

    st.dataframe(
        customer_table[
            [
                "Rank",
                "Customer",
                "Region",
                "Revenue",
                "Profit",
                "Orders",
                "Avg Order Value"
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=420
    )

# --------------------------------------------------
# AUTOMATED INSIGHTS
# --------------------------------------------------
st.divider()

st.subheader("💡 Automated Customer Insights")

if not df.empty:

    customer_revenue_series = (
        df.groupby("CustomerID")["SalesAmount"]
        .sum()
    )

    top_customer = (
        customer_revenue_series.idxmax()
    )

    top_customer_value = (
        customer_revenue_series.max()
    )

    most_active_customer = (
        df.groupby("CustomerID")["OrderID"]
        .nunique()
        .idxmax()
    )

    best_region = (
        df.groupby("Region")["SalesAmount"]
        .sum()
        .idxmax()
    )

    average_value = (
        customer_revenue_series.mean()
    )

    i1, i2, i3, i4 = st.columns(4)

    with i1:

        st.info(
            f"🏆 **Top Customer**\n\n"
            f"Customer {top_customer} generated "
            f"${top_customer_value:,.0f} in revenue."
        )

    with i2:

        st.info(
            f"🔄 **Most Active Customer**\n\n"
            f"Customer {most_active_customer} "
            f"has the highest order frequency."
        )

    with i3:

        st.info(
            f"🌍 **Leading Region**\n\n"
            f"{best_region} generates the most customer revenue."
        )

    with i4:

        st.info(
            f"🎯 **Average Customer Value**\n\n"
            f"${average_value:,.0f} average revenue per customer."
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "Nexa Bussiness Intelligence • Customer Insights Module • "
    "Python + Streamlit + Pandas + Plotly"
)