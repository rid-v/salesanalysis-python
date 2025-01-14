# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# App Title
st.title("Sales Analysis Web App")
st.write("An interactive platform to analyze sales data, generate business insights, and visualize trends.")

# Sidebar for Upload
st.sidebar.header("Upload Sales Data")
uploaded_file = st.sidebar.file_uploader("Upload your sales data (CSV format)", type="csv")

if uploaded_file:
    # Load Data
    sales_data = pd.read_csv(uploaded_file)

    # Ensure Date Parsing
    if "Date" in sales_data.columns:
        sales_data["Date"] = pd.to_datetime(sales_data["Date"], errors="coerce")
        sales_data.dropna(subset=["Date"], inplace=True)
        sales_data["Month"] = sales_data["Date"].dt.month_name()
        sales_data["Quarter"] = sales_data["Date"].dt.to_period("Q").astype(str)
        sales_data["Year"] = sales_data["Date"].dt.year
    else:
        st.error("The uploaded file does not contain a 'Date' column.")
        st.stop()

    # Calculate Revenue and Profit
    if "Revenue" not in sales_data.columns:
        if "Units Sold" in sales_data.columns and "Unit Price" in sales_data.columns:
            sales_data["Revenue"] = sales_data["Units Sold"] * sales_data["Unit Price"]
    if "Profit" not in sales_data.columns:
        if "Cost" in sales_data.columns and "Revenue" in sales_data.columns:
            sales_data["Profit"] = sales_data["Revenue"] - sales_data["Cost"]

    st.write("### Sales Data Overview", sales_data.head())

    # Filtering Options
    st.sidebar.header("Filters")
    year_filter = st.sidebar.multiselect("Filter by Year", options=sales_data["Year"].unique())
    if year_filter:
        sales_data = sales_data[sales_data["Year"].isin(year_filter)]

    # Check if "Region" column exists and add filter options accordingly
    if "Region" in sales_data.columns:
        region_filter = st.sidebar.multiselect("Filter by Region", options=sales_data["Region"].unique())
        if region_filter:
            sales_data = sales_data[sales_data["Region"].isin(region_filter)]
    else:
        st.warning("The uploaded file does not contain a 'Region' column.")

    # Key Insights
    st.write("### Key Insights")
    if "Revenue" in sales_data.columns:
        total_revenue = sales_data["Revenue"].sum()
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    if "Profit" in sales_data.columns:
        total_profit = sales_data["Profit"].sum()
        st.metric("Total Profit", f"${total_profit:,.2f}")

    # Quarterly Revenue Trends
    st.write("### Quarterly Revenue Trends")
    quarterly_summary = sales_data.groupby("Quarter").sum(numeric_only=True)[["Revenue"]]
    fig, ax = plt.subplots()
    sns.lineplot(data=quarterly_summary, x=quarterly_summary.index, y="Revenue", marker="o", ax=ax)
    ax.set_title("Quarterly Revenue Trends")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Revenue")
    st.pyplot(fig)

    # Top Performers
    if "Product" in sales_data.columns:
        st.write("### Top Performing Products")
        top_products = sales_data.groupby("Product").sum(numeric_only=True).sort_values(by="Revenue", ascending=False).head(5)
        st.bar_chart(top_products["Revenue"])

    if "Region" in sales_data.columns:
        st.write("### Top Performing Regions")
        top_regions = sales_data.groupby("Region").sum(numeric_only=True).sort_values(by="Revenue", ascending=False)
        st.write(top_regions)

    # Monthly Sales Trends
    st.write("### Monthly Sales Trends")
    monthly_summary = sales_data.groupby("Month").sum(numeric_only=True)[["Revenue"]]
    fig, ax = plt.subplots()
    sns.barplot(data=monthly_summary.reset_index(), x="Month", y="Revenue", ax=ax, order=pd.date_range("2025-01-01", "2025-12-31", freq="M").strftime("%B").unique())
    ax.set_title("Monthly Revenue Trends")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    st.pyplot(fig)

    # Regional Analysis
    if "Region" in sales_data.columns:
        st.write("### Regional Analysis")
        region = st.selectbox("Select a Region", sales_data["Region"].unique())
        regional_data = sales_data[sales_data["Region"] == region]
        st.write(f"Sales data for {region}", regional_data)

        # Regional sales chart
        fig, ax = plt.subplots()
        sns.barplot(data=regional_data, x=regional_data["Month"], y="Revenue", ax=ax)
        ax.set_title(f"Monthly Revenue in {region}")
        st.pyplot(fig)

    # Pie Chart for Revenue Distribution
    st.write("### Revenue Distribution by Region")
    if "Region" in sales_data.columns:
        region_summary = sales_data.groupby("Region").sum(numeric_only=True)["Revenue"]
        fig, ax = plt.subplots()
        ax.pie(region_summary, labels=region_summary.index, autopct="%1.1f%%", startangle=90)
        ax.set_title("Revenue Distribution by Region")
        st.pyplot(fig)

    # Download Report
    st.write("### Download Reports")
    report_csv = sales_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Full Sales Data",
        data=report_csv,
        file_name="sales_data_report.csv",
        mime="text/csv",
    )
else:
    st.write("Upload a CSV file to get started.")
