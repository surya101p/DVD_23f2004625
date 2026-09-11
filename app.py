import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide"
)

PATH = "analysis_output"


# ============================================================
# LOAD DATA
# ============================================================

order_analysis = pd.read_csv(
    f"{PATH}/order_analysis.csv"
)

category = pd.read_csv(
    f"{PATH}/category_performance.csv"
)

strategy = pd.read_csv(
    f"{PATH}/category_strategy.csv"
)

delivered = pd.read_csv(
    f"{PATH}/delivered_orders.csv"
)

delivery = pd.read_csv(
    f"{PATH}/delivery_satisfaction.csv"
)

regional = pd.read_csv(
    f"{PATH}/regional_performance.csv"
)

seller = pd.read_csv(
    f"{PATH}/seller_performance.csv"
)


# ============================================================
# DATE
# ============================================================

order_analysis["order_purchase_timestamp"] = pd.to_datetime(
    order_analysis["order_purchase_timestamp"],
    errors="coerce"
)

order_analysis["month"] = (
    order_analysis["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Filters")

states = sorted(
    order_analysis["customer_state"]
    .dropna()
    .unique()
)

selected_states = st.sidebar.multiselect(
    "Customer State",
    states
)

if selected_states:
    df = order_analysis[
        order_analysis["customer_state"].isin(selected_states)
    ].copy()
else:
    df = order_analysis.copy()


# ============================================================
# TITLE
# ============================================================

st.title("E-Commerce Analytics Dashboard")

st.caption(
    "Sales • Customers • Categories • Delivery • Satisfaction • Sellers"
)


# ============================================================
# KPI
# ============================================================

total_orders = df["order_id"].nunique()

delivered_orders = df[
    df["order_status"] == "delivered"
]["order_id"].nunique()

revenue = df["order_value"].sum()

customers = df["customer_unique_id"].nunique()

rating = df["review_score"].mean()

late_rate = df["is_late"].mean() * 100

negative_rate = df["is_negative_review"].mean() * 100

aov = df["order_value"].mean()


c1, c2, c3, c4 = st.columns(4)

c1.metric("Orders", f"{total_orders:,}")
c2.metric("Revenue", f"R$ {revenue:,.0f}")
c3.metric("Customers", f"{customers:,}")
c4.metric("Avg Rating", f"{rating:.2f}")


c1, c2, c3, c4 = st.columns(4)

c1.metric("Late Delivery", f"{late_rate:.1f}%")
c2.metric("Negative Reviews", f"{negative_rate:.1f}%")
c3.metric("Avg Order Value", f"R$ {aov:,.0f}")
c4.metric("Delivered", f"{delivered_orders:,}")


# ============================================================
# TABS
# ============================================================

overview, category_tab, delivery_tab, regional_tab, seller_tab = st.tabs(
    [
        "Overview",
        "Category Strategy",
        "Delivery & Satisfaction",
        "Regional",
        "Seller Performance"
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

with overview:

    st.subheader("Monthly Sales")

    monthly = (
        df.groupby("month", as_index=False)
        .agg(
            revenue=("order_value", "sum"),
            orders=("order_id", "nunique")
        )
    )

    fig = px.line(
        monthly,
        x="month",
        y="revenue",
        markers=True
    )

    fig.update_layout(
        height=380,
        xaxis_title="",
        yaxis_title="Revenue (R$)"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Top Categories")

        top = (
            category
            .nlargest(10, "revenue")
            .sort_values("revenue")
        )

        fig = px.bar(
            top,
            x="revenue",
            y="product_category_name_english",
            orientation="h"
        )

        fig.update_layout(
            height=400,
            xaxis_title="Revenue (R$)",
            yaxis_title=""
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        st.subheader("Revenue by State")

        states_revenue = (
            regional
            .nlargest(15, "revenue")
            .sort_values("revenue")
        )

        fig = px.bar(
            states_revenue,
            x="revenue",
            y="customer_state",
            orientation="h"
        )

        fig.update_layout(
            height=400,
            xaxis_title="Revenue (R$)",
            yaxis_title=""
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )


# ============================================================
# CATEGORY STRATEGY
# ============================================================

with category_tab:

    st.subheader("Category Strategy")

    st.caption(
        "Strategy is based on revenue and customer satisfaction."
    )

    counts = strategy["strategy"].value_counts()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Invest", int(counts.get("Invest", 0)))
    c2.metric("Intervene", int(counts.get("Intervene", 0)))
    c3.metric("Maintain", int(counts.get("Maintain", 0)))
    c4.metric("Review", int(counts.get("Review", 0)))

    fig = px.scatter(
        strategy,
        x="revenue",
        y="average_rating",
        size="orders_sales",
        color="strategy",
        hover_name="product_category_name_english"
    )

    fig.update_layout(
        height=480,
        xaxis_title="Revenue (R$)",
        yaxis_title="Average Rating"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.subheader("Strategic Categories")

    display = strategy[
        [
            "product_category_name_english",
            "orders_sales",
            "revenue",
            "average_rating",
            "negative_rate",
            "strategy"
        ]
    ].sort_values(
        "revenue",
        ascending=False
    )

    display["revenue"] = display["revenue"].round(2)
    display["average_rating"] = display["average_rating"].round(2)
    display["negative_rate"] = display["negative_rate"].round(2)

    st.dataframe(
        display,
        width="stretch",
        hide_index=True
    )


# ============================================================
# DELIVERY
# ============================================================

with delivery_tab:

    st.subheader("Delivery & Customer Satisfaction")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            delivery,
            x="delivery_status",
            y="average_rating",
            text="average_rating"
        )

        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig.update_layout(
            height=380,
            xaxis_title="",
            yaxis_title="Average Rating"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        score_delivery = (
            df.groupby("review_score", as_index=False)
            .agg(
                average_delay=(
                    "delivery_delay_days",
                    "mean"
                )
            )
        )

        fig = px.bar(
            score_delivery,
            x="review_score",
            y="average_delay",
            text="average_delay"
        )

        fig.update_layout(
            height=380,
            xaxis_title="Review Score",
            yaxis_title="Average Delay (Days)"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    col1, col2 = st.columns(2)

    with col1:

        performance = (
            delivered["delivery_performance"]
            .value_counts()
            .reset_index()
        )

        performance.columns = [
            "delivery_performance",
            "orders"
        ]

        fig = px.bar(
            performance,
            x="delivery_performance",
            y="orders"
        )

        fig.update_layout(
            height=350,
            xaxis_title="",
            yaxis_title="Orders"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        fig = px.histogram(
            delivered,
            x="delivery_days",
            nbins=40
        )

        fig.update_layout(
            height=350,
            xaxis_title="Delivery Days",
            yaxis_title="Orders"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )


# ============================================================
# REGIONAL
# ============================================================

with regional_tab:

    st.subheader("Regional Performance")

    regional_df = regional.copy()

    if selected_states:
        regional_df = regional_df[
            regional_df["customer_state"].isin(
                selected_states
            )
        ]

    col1, col2 = st.columns(2)

    with col1:

        top_states = (
            regional_df
            .nlargest(15, "revenue")
            .sort_values("revenue")
        )

        fig = px.bar(
            top_states,
            x="revenue",
            y="customer_state",
            orientation="h"
        )

        fig.update_layout(
            height=450,
            xaxis_title="Revenue (R$)",
            yaxis_title=""
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        fig = px.scatter(
            regional_df,
            x="late_rate",
            y="average_rating",
            size="orders",
            hover_name="customer_state"
        )

        fig.update_layout(
            height=450,
            xaxis_title="Late Delivery Rate (%)",
            yaxis_title="Average Rating"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    best_state = regional_df.loc[
        regional_df["revenue"].idxmax()
    ]

    worst_delivery = regional_df.loc[
        regional_df["late_rate"].idxmax()
    ]

    best_rating = regional_df.loc[
        regional_df["average_rating"].idxmax()
    ]

    c1, c2, c3 = st.columns(3)

    c1.success(
        f"Highest Revenue\n\n"
        f"**{best_state['customer_state']}**\n\n"
        f"R$ {best_state['revenue']:,.0f}"
    )

    c2.warning(
        f"Highest Late Rate\n\n"
        f"**{worst_delivery['customer_state']}**\n\n"
        f"{worst_delivery['late_rate']:.1f}%"
    )

    c3.info(
        f"Highest Rating\n\n"
        f"**{best_rating['customer_state']}**\n\n"
        f"{best_rating['average_rating']:.2f}"
    )


# ============================================================
# SELLER
# ============================================================

with seller_tab:

    st.subheader("Seller Performance")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.scatter(
            seller,
            x="late_rate",
            y="average_rating",
            size="orders",
            hover_name="seller_id"
        )

        fig.add_vline(
            x=20,
            line_dash="dash"
        )

        fig.add_hline(
            y=3.5,
            line_dash="dash"
        )

        fig.update_layout(
            height=450,
            xaxis_title="Late Delivery Rate (%)",
            yaxis_title="Average Rating"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        high_risk = seller[
            (seller["orders"] >= 100) &
            (seller["average_rating"] < 3.5) &
            (seller["late_rate"] > 20)
        ]

        st.subheader("High-Risk Sellers")

        st.caption(
            "100+ orders • Rating < 3.5 • Late rate > 20%"
        )

        st.dataframe(
            high_risk[
                [
                    "seller_id",
                    "orders",
                    "average_rating",
                    "negative_rate",
                    "late_rate",
                    "avg_delay_days"
                ]
            ].sort_values(
                "late_rate",
                ascending=False
            ),
            width="stretch",
            hide_index=True
        )


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "E-Commerce Analytics Dashboard | Brazilian E-Commerce Dataset"
)