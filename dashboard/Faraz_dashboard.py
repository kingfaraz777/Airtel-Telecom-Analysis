
# ============================================================
# AIRTEL CUSTOMER SERVICE DASHBOARD
# ============================================================

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from pathlib import Path


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Customer Service Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# 2. DATABASE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "raw" / "airtel.db"

# Airtel Logo
LOGO_URL = (
    "https://thumb.wikimedia.org/wikipedia/commons/"
    "thumb/f/fb/Bharti_Airtel_Logo.svg/"
    "960px-Bharti_Airtel_Logo.svg.png"
)


# ============================================================
# 3. CSS DESIGN
# ============================================================

st.markdown("""
<style>

    .stApp {
        background-color: #F4F7FB;
    }

    .main .block-container {
        padding: 1.5rem 2rem;
        max-width: 1600px;
    }

    /* MAIN HEADING */

    .stApp h1 {
        color: #E4002B !important;
        font-size: 38px !important;
        font-weight: 850 !important;
        text-align: center;
        padding: 18px 10px;
        margin-bottom: 20px;
        background: #FFFFFF;
        border-bottom: 5px solid #E4002B;
        border-radius: 10px;
    }

    /* SECTION HEADINGS */

    .stApp h2,
    .stApp h3,
    .stApp h4 {
        color: #000000 !important;
        font-weight: 750 !important;
    }

    .stApp p,
    .stApp label {
        color: #172B4D;
    }

    /* KPI METRICS */

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #E4002B;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 7px rgba(0,0,0,0.05);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #172B4D !important;
        font-weight: 800 !important;
    }

    /* FILTER PANEL */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label {
        color: #172B4D !important;
        font-weight: 650 !important;
    }

    /* TABS */

    div[data-testid="stTabs"] button {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #E4002B !important;
        border-bottom: 3px solid #E4002B !important;
    }

    /* BUTTON */

    div.stButton > button {
        background-color: #E4002B;
        color: #FFFFFF !important;
        border-radius: 8px;
        border: none;
        font-weight: 650;
        min-height: 40px;
    }

    div.stButton > button:hover {
        background-color: #B00020;
        color: #FFFFFF !important;
    }

    /* DOWNLOAD BUTTON */

    div.stDownloadButton > button {
        background-color: #E4002B;
        color: #FFFFFF !important;
        border-radius: 8px;
        font-weight: 650;
    }

    /* DATAFRAME */

    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }

    /* FOOTER */

    .footer {
        text-align: center;
        color: #64748B;
        padding: 18px;
        font-size: 13px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# 4. PLOTLY CHART STYLE
# ============================================================

def apply_chart_style(fig):

    fig.update_layout(

        height=300,

        margin=dict(
            l=45,
            r=25,
            t=25,
            b=45
        ),

        font=dict(
            family="Arial",
            size=12,
            color="#000000"
        ),

        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",

        legend=dict(
            font=dict(
                color="#000000",
                size=11
            )
        ),

        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#000000",
            font=dict(
                color="#000000"
            )
        )
    )

    fig.update_xaxes(
        title_font=dict(color="#000000"),
        tickfont=dict(color="#000000"),
        color="#000000",
        gridcolor="#E5E7EB"
    )

    fig.update_yaxes(
        title_font=dict(color="#000000"),
        tickfont=dict(color="#000000"),
        color="#000000",
        gridcolor="#E5E7EB"
    )

    return fig


# ============================================================
# 5. DATABASE LOADING
# ============================================================

@st.cache_data
def load_data(database_path, modified_time):

    conn = sqlite3.connect(str(database_path))

    try:

        complaints = pd.read_sql_query(
            "SELECT * FROM complaints",
            conn
        )

        customers = pd.read_sql_query(
            "SELECT * FROM customer_features",
            conn
        )

    finally:

        conn.close()

    if "customer_id" not in complaints.columns:

        raise ValueError(
            "The complaints table does not contain customer_id."
        )

    if "customer_id" not in customers.columns:

        raise ValueError(
            "The customer_features table does not contain customer_id."
        )

    data = complaints.merge(
        customers,
        on="customer_id",
        how="left",
        suffixes=("", "_customer")
    )

    return data


# ============================================================
# 6. CHECK DATABASE
# ============================================================

if not DB_PATH.is_file():

    st.error("Database file not found.")

    st.info(
        f"Expected database location: {DB_PATH}"
    )

    st.stop()


try:

    df = load_data(
        str(DB_PATH),
        DB_PATH.stat().st_mtime
    )

except Exception as error:

    st.error(f"Database loading error: {error}")

    st.info(
        "Please check the complaints and customer_features tables."
    )

    st.stop()


# ============================================================
# 7. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "complaint_id",
    "customer_id",
    "complaint_date",
    "category",
    "channel",
    "is_resolved",
    "resolution_days"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )

    st.stop()


# ============================================================
# 8. DATA CLEANING
# ============================================================

df["complaint_date"] = pd.to_datetime(
    df["complaint_date"],
    errors="coerce"
)

df["resolution_days"] = pd.to_numeric(
    df["resolution_days"],
    errors="coerce"
)

df["is_resolved"] = (
    df["is_resolved"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(["1", "true", "yes", "resolved"])
)

if "is_churned" in df.columns:

    df["is_churned"] = (
        df["is_churned"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["1", "true", "yes"])
    )

else:

    df["is_churned"] = False


optional_columns = [
    "region",
    "circle_name",
    "connection_type",
    "plan_name",
    "plan_type",
    "age_band",
    "gender",
    "device_type",
    "os",
    "acquisition_channel"
]

for column in optional_columns:

    if column not in df.columns:

        df[column] = "Unknown"

    df[column] = (
        df[column]
        .fillna("Unknown")
        .astype(str)
    )


df["category"] = (
    df["category"].fillna("Unknown").astype(str)
)

df["channel"] = (
    df["channel"].fillna("Unknown").astype(str)
)


# ============================================================
# 9. MAIN HEADING WITH AIRTEL LOGO
# ============================================================

logo_col, heading_col = st.columns(
    [1, 8],
    vertical_alignment="center"
)

with logo_col:

    st.image(
        LOGO_URL,
        width=90
    )

with heading_col:

    st.title("Customer Service Dashboard")


# ============================================================
# 10. FILTER OPTIONS
# ============================================================

def filter_options(column):

    values = sorted(
        df[column].dropna().astype(str).unique().tolist()
    )

    return ["All"] + values


valid_dates = df["complaint_date"].dropna()

if not valid_dates.empty:

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

else:

    min_date = None
    max_date = None


# ============================================================
# 11. RESET FILTER FUNCTION
# ============================================================

def reset_filters():

    st.session_state["filter_category"] = "All"
    st.session_state["filter_channel"] = "All"
    st.session_state["filter_region"] = "All"
    st.session_state["filter_circle"] = "All"
    st.session_state["filter_connection"] = "All"

    if min_date is not None:

        st.session_state["filter_dates"] = (
            min_date,
            max_date
        )


# ============================================================
# 12. HORIZONTAL FILTER PANEL
# ============================================================

with st.container(border=True):

    st.markdown("### 🔎 Dashboard Filters")

    f1, f2, f3, f4, f5 = st.columns(5)

    with f1:

        selected_category = st.selectbox(
            "Complaint Category",
            filter_options("category"),
            key="filter_category"
        )

    with f2:

        selected_channel = st.selectbox(
            "Complaint Channel",
            filter_options("channel"),
            key="filter_channel"
        )

    with f3:

        selected_region = st.selectbox(
            "Region",
            filter_options("region"),
            key="filter_region"
        )

    with f4:

        selected_circle = st.selectbox(
            "Circle",
            filter_options("circle_name"),
            key="filter_circle"
        )

    with f5:

        selected_connection = st.selectbox(
            "Connection Type",
            filter_options("connection_type"),
            key="filter_connection"
        )

    st.write("")

    date_col, reset_col = st.columns([4, 1])

    with date_col:

        if min_date is not None:

            date_range = st.date_input(
                "Complaint Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="filter_dates"
            )

        else:

            date_range = None

    with reset_col:

        st.write("")

        st.button(
            "↻ Reset Filters",
            use_container_width=True,
            on_click=reset_filters
        )


# ============================================================
# 13. APPLY FILTERS
# ============================================================

filtered = df.copy()

if selected_category != "All":

    filtered = filtered[
        filtered["category"] == selected_category
    ]

if selected_channel != "All":

    filtered = filtered[
        filtered["channel"] == selected_channel
    ]

if selected_region != "All":

    filtered = filtered[
        filtered["region"] == selected_region
    ]

if selected_circle != "All":

    filtered = filtered[
        filtered["circle_name"] == selected_circle
    ]

if selected_connection != "All":

    filtered = filtered[
        filtered["connection_type"] == selected_connection
    ]

if (
    date_range is not None
    and isinstance(date_range, (tuple, list))
    and len(date_range) == 2
):

    start_date, end_date = date_range

    filtered = filtered[
        (filtered["complaint_date"].dt.date >= start_date)
        &
        (filtered["complaint_date"].dt.date <= end_date)
    ]


# ============================================================
# 14. DASHBOARD TABS
# ============================================================

tab_overview, tab_category, tab_explorer = st.tabs([
    "📊 Overview",
    "📁 Category Detail",
    "📋 Data Explorer"
])


# ============================================================
# TAB 1: OVERVIEW
# ============================================================

with tab_overview:

    st.markdown("### 📊 Overall Performance")

    total_complaints = len(filtered)

    resolved_count = int(
        filtered["is_resolved"].sum()
    )

    unresolved_count = (
        total_complaints - resolved_count
    )

    resolution_rate = (
        resolved_count / total_complaints * 100
        if total_complaints > 0 else 0
    )

    avg_resolution = (
        filtered["resolution_days"].mean()
        if total_complaints > 0 else 0
    )

    churned_count = int(
        filtered["is_churned"].sum()
    )


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    k1, k2, k3, k4 = st.columns(4)

    with k1:

        st.metric(
            "Total Complaints",
            f"{total_complaints:,}"
        )

    with k2:

        st.metric(
            "Resolved Complaints",
            f"{resolved_count:,}"
        )

    with k3:

        st.metric(
            "Unresolved Complaints",
            f"{unresolved_count:,}"
        )

    with k4:

        st.metric(
            "Resolution Rate",
            f"{resolution_rate:.1f}%"
        )


    k5, k6 = st.columns(2)

    with k5:

        st.metric(
            "Average Resolution Days",
            f"{avg_resolution:.2f}"
            if pd.notna(avg_resolution) else "N/A"
        )

    with k6:

        st.metric(
            "Churned Customers",
            f"{churned_count:,}"
        )


    st.divider()


    # ========================================================
    # CHART 1 AND CHART 2
    # ========================================================

    chart1, chart2 = st.columns(2)


    # --------------------------------------------------------
    # CHART 1: VERTICAL BAR CHART
    # --------------------------------------------------------

    with chart1:

        st.subheader("1. Complaints by Category")

        category_data = (
            filtered["category"]
            .value_counts()
            .reset_index()
        )

        category_data.columns = [
            "Category",
            "Complaints"
        ]

        if not category_data.empty:

            fig = px.bar(
                category_data,
                x="Category",
                y="Complaints",
                color="Category",
                text="Complaints",
                color_discrete_sequence=[
                    "#E4002B",
                    "#2563EB",
                    "#16A34A",
                    "#F59E0B",
                    "#7C3AED",
                    "#0891B2"
                ]
            )

            fig.update_traces(
                textfont=dict(
                    color="#000000",
                    size=10
                ),
                textposition="outside"
            )

            fig = apply_chart_style(fig)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No category data available.")


    # --------------------------------------------------------
    # CHART 2: DONUT CHART
    # --------------------------------------------------------

    with chart2:

        st.subheader("2. Complaint Resolution Status")

        status_data = pd.DataFrame({

            "Status": [
                "Resolved",
                "Unresolved"
            ],

            "Count": [
                resolved_count,
                unresolved_count
            ]

        })

        if total_complaints > 0:

            fig = px.pie(
                status_data,
                names="Status",
                values="Count",
                hole=0.55,
                color="Status",
                color_discrete_map={
                    "Resolved": "#16A34A",
                    "Unresolved": "#E4002B"
                }
            )

            fig.update_traces(
                textinfo="label+percent",
                textfont=dict(
                    color="#000000",
                    size=11
                ),
                insidetextfont=dict(
                    color="#000000"
                ),
                outsidetextfont=dict(
                    color="#000000"
                )
            )

            fig = apply_chart_style(fig)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No complaint data available.")


    st.divider()


    # ========================================================
    # CHART 3 AND CHART 4
    # ========================================================

    chart3, chart4 = st.columns(2)


    # --------------------------------------------------------
    # CHART 3: HORIZONTAL BAR CHART
    # --------------------------------------------------------

    with chart3:

        st.subheader("3. Complaints by Channel")

        channel_data = (
            filtered["channel"]
            .value_counts()
            .reset_index()
        )

        channel_data.columns = [
            "Channel",
            "Complaints"
        ]

        if not channel_data.empty:

            fig = px.bar(
                channel_data,
                x="Complaints",
                y="Channel",
                orientation="h",
                color="Channel",
                text="Complaints",
                color_discrete_sequence=[
                    "#2563EB",
                    "#0891B2",
                    "#7C3AED",
                    "#F59E0B"
                ]
            )

            fig.update_traces(
                textfont=dict(
                    color="#000000",
                    size=10
                ),
                textposition="outside"
            )

            fig.update_layout(
                yaxis=dict(
                    categoryorder="total ascending"
                )
            )

            fig = apply_chart_style(fig)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No channel data available.")


    # --------------------------------------------------------
    # CHART 4: LINE CHART
    # --------------------------------------------------------

    with chart4:

        st.subheader("4. Monthly Complaint Trend")

        trend_data = filtered.dropna(
            subset=["complaint_date"]
        ).copy()

        if not trend_data.empty:

            trend_data["Month"] = (
                trend_data["complaint_date"]
                .dt.to_period("M")
                .astype(str)
            )

            monthly_data = (
                trend_data
                .groupby("Month")
                .size()
                .reset_index(name="Complaints")
                .sort_values("Month")
            )

            fig = px.line(
                monthly_data,
                x="Month",
                y="Complaints",
                markers=True
            )

            fig.update_traces(
                line=dict(
                    color="#2563EB",
                    width=3
                ),
                marker=dict(
                    color="#E4002B",
                    size=7
                )
            )

            fig = apply_chart_style(fig)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No date data available.")


    st.divider()


    # ========================================================
    # CHART 5: REGION HORIZONTAL BAR
    # ========================================================

    region_col, empty_col = st.columns(2)

    with region_col:

        st.subheader("5. Complaints by Region")

        region_data = (
            filtered["region"]
            .value_counts()
            .reset_index()
        )

        region_data.columns = [
            "Region",
            "Complaints"
        ]

        if not region_data.empty:

            fig = px.bar(
                region_data,
                x="Complaints",
                y="Region",
                orientation="h",
                color="Region",
                text="Complaints",
                color_discrete_sequence=[
                    "#16A34A",
                    "#E4002B",
                    "#2563EB",
                    "#F59E0B"
                ]
            )

            fig.update_traces(
                textfont=dict(
                    color="#000000",
                    size=10
                ),
                textposition="outside"
            )

            fig.update_layout(
                yaxis=dict(
                    categoryorder="total ascending"
                )
            )

            fig = apply_chart_style(fig)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No region data available.")


# ============================================================
# TAB 2: CATEGORY DETAIL
# ============================================================

with tab_category:

    st.markdown("### 📁 Category Analysis")

    if filtered.empty:

        st.warning(
            "No records available for the selected filters."
        )

    else:

        categories = sorted(
            filtered["category"].dropna().unique().tolist()
        )

        chosen_category = st.selectbox(
            "Select a Complaint Category",
            categories,
            key="detail_category"
        )

        category_df = filtered[
            filtered["category"] == chosen_category
        ]

        st.subheader(
            f"Analysis: {chosen_category}"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Total Complaints",
                f"{len(category_df):,}"
            )

        with c2:

            st.metric(
                "Resolved",
                f"{int(category_df['is_resolved'].sum()):,}"
            )

        with c3:

            rate = (
                category_df["is_resolved"].mean() * 100
                if len(category_df) > 0 else 0
            )

            st.metric(
                "Resolution Rate",
                f"{rate:.1f}%"
            )

        st.divider()

        detail1, detail2 = st.columns(2)


        # ----------------------------------------------------
        # CATEGORY CHANNEL PIE CHART
        # ----------------------------------------------------

        with detail1:

            st.subheader("Customer Complaint Channels")

            channel_detail = (
                category_df["channel"]
                .value_counts()
                .reset_index()
            )

            channel_detail.columns = [
                "Channel",
                "Count"
            ]

            if not channel_detail.empty:

                fig = px.pie(
                    channel_detail,
                    names="Channel",
                    values="Count",
                    hole=0.4
                )

                fig.update_traces(
                    textinfo="label+percent",
                    textfont=dict(
                        color="#000000",
                        size=11
                    ),
                    insidetextfont=dict(
                        color="#000000"
                    ),
                    outsidetextfont=dict(
                        color="#000000"
                    )
                )

                fig = apply_chart_style(fig)

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )


        # ----------------------------------------------------
        # RESOLUTION DAYS HISTOGRAM
        # ----------------------------------------------------

       
with detail2:

    if "resolution_days" in category_df.columns:

        st.subheader("Resolution Days")

        resolution_data = (category_df["resolution_days"]
            .dropna()
            .value_counts()
            .sort_index()
            .reset_index()
        )

        resolution_data.columns = [
            "Resolution Days",
            "Complaints"
        ]

        fig_cat2 = px.bar(
            resolution_data,
            x="Resolution Days",
            y="Complaints",
            color_discrete_sequence=["#E4002B"]
        )

        fig_cat2.update_traces(
            text=resolution_data["Complaints"],
            textposition="outside",
            marker_line_width=0
        )

        fig_cat2.update_layout(
            height=350,
            plot_bgcolor="black",
            paper_bgcolor="black",
            font=dict(color="white"),
            xaxis_title="Resolution Days",
            yaxis_title="Number of Complaints",
            showlegend=False,
            bargap=0.25
        )

        fig_cat2.update_xaxes(
            type="category"
        )

        fig_cat2.update_yaxes(
            rangemode="tozero"
        )

        st.plotly_chart(
            fig_cat2,
            use_container_width=True
        )


# ----------------------------------------------------
# MINI TABLE - COMPLAINT CHANNEL SUMMARY
# ----------------------------------------------------

st.divider()

st.subheader("Complaint Channel Summary")

mini_table = (
    category_df.groupby("channel")
    .agg(
        Total_Complaints=("is_resolved", "count"),
        Resolved=("is_resolved", "sum")
    )
    .reset_index()
)

mini_table.columns = [
    "Channel",
    "Total Complaints",
    "Resolved"
]

mini_table["Pending"] = (
    mini_table["Total Complaints"]
    - mini_table["Resolved"]
)

mini_table["Resolution Rate (%)"] = (
    mini_table["Resolved"]
    / mini_table["Total Complaints"]
    * 100
).round(1)

st.dataframe(
    mini_table,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# TAB 3: DATA EXPLORER
# ============================================================

with tab_explorer:

    st.markdown("### 📋 Customer Complaint Data Explorer")

    st.write(
        f"Showing **{len(filtered):,}** records "
        f"out of **{len(df):,}** total records."
    )

    if filtered.empty:

        st.warning(
            "No records match the selected filters."
        )

    else:

        search_text = st.text_input(
            "Search by Customer ID, Complaint ID or Category",
            key="data_search"
        )

        display_df = filtered.copy()

        if search_text:

            search_mask = (
                display_df.astype(str)
                .apply(
                    lambda column: column.str.contains(
                        search_text,
                        case=False,
                        na=False
                    )
                )
                .any(axis=1)
            )

            display_df = display_df[search_mask]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = display_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇ Download Filtered Data as CSV",
            data=csv_data,
            file_name="airtel_filtered_complaints.csv",
            mime="text/csv",
            use_container_width=True
        )


# ============================================================
# 15. FOOTER
# ============================================================

st.markdown("---")

st.markdown("""
<div class="footer">
    Airtel Customer Service Dashboard<br>
    Complaint Analysis | Customer Experience |
    Churn Monitoring
</div>
""", unsafe_allow_html=True)