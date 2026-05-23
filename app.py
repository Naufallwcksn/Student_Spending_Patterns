import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon=":moneybag:",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/Naufallwcksn/Student_Spending_Patterns/refs/heads/main/CodingCamp/personal_finance_tracker_dataset.csv"
    )

    df['date'] = pd.to_datetime(df['date'])

    df['is_overspending'] = (
        df['monthly_expense_total'] >
        df['monthly_income']
    )

    return df

df = load_data()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title(":pushpin: Filter Dashboard")

income_filter = st.sidebar.multiselect(
    "Pilih Income Type",
    options=df['income_type'].unique(),
    default=df['income_type'].unique()
)

stress_filter = st.sidebar.multiselect(
    "Pilih Financial Stress Level",
    options=df['financial_stress_level'].unique(),
    default=df['financial_stress_level'].unique()
)

date_range = st.sidebar.date_input(
    ":calendar: Pilih Rentang Tanggal",
    value=(
        df['date'].min(),
        df['date'].max()
    ),
    min_value=df['date'].min(),
    max_value=df['date'].max()
)

# =====================================================
# FILTER DATA
# =====================================================

start_date, end_date = date_range

filtered_df = df[
    (df['income_type'].isin(income_filter)) &
    (df['financial_stress_level'].isin(stress_filter)) &
    (df['date'] >= pd.to_datetime(start_date)) &
    (df['date'] <= pd.to_datetime(end_date))
]

# =====================================================
# TITLE
# =====================================================

st.title(":moneybag: Personal Finance Analytics Dashboard")

st.markdown("""
Dashboard ini digunakan untuk menganalisis pola pengeluaran pengguna,
financial stress, savings behavior, dan perilaku overspending.
""")

# =====================================================
# KPI
# =====================================================

total_users = filtered_df.shape[0]
avg_income = filtered_df['monthly_income'].mean()
avg_expense = filtered_df['monthly_expense_total'].mean()
overspending_users = filtered_df['is_overspending'].sum()

success_rate = (
    filtered_df['savings_goal_met'].mean() * 100
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    ":busts_in_silhouette: Total Users",
    f"{total_users:,}"
)

col2.metric(
    ":money_with_wings: Avg Income",
    f"${avg_income:,.0f}"
)

col3.metric(
    "credit_card: Avg Expense",
    f"${avg_expense:,.0f}"
)

col4.metric(
    ":warning: Overspending",
    f"{overspending_users:,}"
)

col5.metric(
    ":dart: Savings Goal",
    f"{success_rate:.1f}%"
)

st.divider()

# =====================================================
# CHART ROW 1
# =====================================================

col1, col2 = st.columns(2)

with col1:

    income_dist = (
        filtered_df['income_type']
        .value_counts()
        .reset_index()
    )

    fig_income = px.pie(
        income_dist,
        names='income_type',
        values='count',
        title='Distribusi Income Type',
        hole=0.5
    )

    st.plotly_chart(
        fig_income,
        use_container_width=True
    )

with col2:

    overspend = (
        filtered_df['is_overspending']
        .value_counts()
        .reset_index()
    )

    fig_over = px.bar(
        overspend,
        x='is_overspending',
        y='count',
        title='Jumlah Overspending User',
        text_auto=True
    )

    st.plotly_chart(
        fig_over,
        use_container_width=True
    )

# =====================================================
# CHART ROW 2
# =====================================================

col1, col2 = st.columns(2)

with col1:

    essential_vs_discretionary = pd.DataFrame({
        'Category': [
            'Essential Spending',
            'Discretionary Spending'
        ],
        'Average': [
            filtered_df['essential_spending'].mean(),
            filtered_df['discretionary_spending'].mean()
        ]
    })

    fig_spending = px.bar(
        essential_vs_discretionary,
        x='Category',
        y='Average',
        title='Essential vs Discretionary Spending',
        text_auto=True
    )

    st.plotly_chart(
        fig_spending,
        use_container_width=True
    )

with col2:

    avg_income_expense = (
        filtered_df
        .groupby('income_type')[
            ['monthly_income',
             'monthly_expense_total']
        ]
        .mean()
        .reset_index()
    )

    fig_compare = go.Figure()

    fig_compare.add_trace(
        go.Bar(
            x=avg_income_expense['income_type'],
            y=avg_income_expense['monthly_income'],
            name='Income'
        )
    )

    fig_compare.add_trace(
        go.Bar(
            x=avg_income_expense['income_type'],
            y=avg_income_expense['monthly_expense_total'],
            name='Expense'
        )
    )

    fig_compare.update_layout(
        title='Income vs Expense by Income Type',
        barmode='group'
    )

    st.plotly_chart(
        fig_compare,
        use_container_width=True
    )

# =====================================================
# MONTHLY TREND
# =====================================================

st.subheader(":chart_with_upwards_trend: Monthly Expense Trend")

monthly_trend = (
    filtered_df
    .groupby(filtered_df['date'].dt.to_period('M'))[
        'monthly_expense_total'
    ]
    .mean()
    .reset_index()
)

monthly_trend['date'] = (
    monthly_trend['date'].astype(str)
)

fig_trend = px.line(
    monthly_trend,
    x='date',
    y='monthly_expense_total',
    markers=True,
    title='Average Monthly Expense Trend'
)

st.plotly_chart(
    fig_trend,
    use_container_width=True
)

# =====================================================
# FINANCIAL STRESS
# =====================================================

col1, col2 = st.columns(2)

with col1:

    stress_savings = (
        filtered_df
        .groupby('financial_stress_level')[
            'actual_savings'
        ]
        .mean()
        .reset_index()
    )

    fig_stress = px.bar(
        stress_savings,
        x='financial_stress_level',
        y='actual_savings',
        title='Average Savings by Financial Stress',
        text_auto=True
    )

    st.plotly_chart(
        fig_stress,
        use_container_width=True
    )

with col2:

    fig_box = px.box(
        filtered_df,
        x='income_type',
        y='monthly_expense_total',
        color='income_type',
        title='Expense Distribution by Income Type'
    )

    st.plotly_chart(
        fig_box,
        use_container_width=True
    )

# =====================================================
# CORRELATION HEATMAP
# =====================================================

st.subheader(":fire: Correlation Heatmap")

numeric_df = filtered_df.select_dtypes(
    include=np.number
)

corr = numeric_df.corr()

fig_heatmap = px.imshow(
    corr,
    text_auto=True,
    aspect="auto",
    title='Correlation Matrix'
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)

# =====================================================
# RAW DATA
# =====================================================

with st.expander(":page_facing_up: Lihat Dataset"):

    st.dataframe(filtered_df)

# =====================================================
# INSIGHT
# =====================================================

st.subheader(":pushpin: Business Insights")

st.success("""
1. Essential spending mendominasi total pengeluaran pengguna.

2. Terdapat cukup banyak pengguna yang mengalami overspending.

3. Pengguna dengan financial stress tinggi memiliki rata-rata tabungan lebih rendah.

4. Income type mempengaruhi pola pengeluaran pengguna.

5. Salary merupakan tipe pendapatan paling dominan dalam dataset.
""")

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")
st.caption("Personal Finance Dashboard • Streamlit Capstone Project")