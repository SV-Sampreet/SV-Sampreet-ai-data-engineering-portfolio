"""Streamlit dashboard for streaming analytics."""
import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import DatabaseConfig, SparkConfig
from src.storage.database import DatabaseStorage

# Page configuration
st.set_page_config(
    page_title="Real-Time Streaming Analytics",
    page_icon="📊",
    layout="wide"
)

# Initialize Spark session
@st.cache_resource
def get_spark():
    """Initialize Spark session."""
    from pyspark.sql import SparkSession
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("Dashboard") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    return spark

def main():
    """Main dashboard application."""
    st.title("📊 Real-Time Streaming Analytics Dashboard")
    st.markdown("Monitor transaction events, metrics, and detected anomalies.")

    # Initialize Spark
    spark = get_spark()

    # Initialize storage
    db_config = DatabaseConfig()
    storage = DatabaseStorage(spark, db_config)

    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        st.info(f"Database Type: {db_config.db_type}")
        st.info(f"Connection: {db_config.get_connection_string()}")

        st.header("Actions")
        if st.button("Refresh Data", type="primary"):
            st.rerun()

    # Main content
    tab1, tab2, tab3 = st.tabs(["Metrics", "Anomalies", "Category Analytics"])

    with tab1:
        st.header("Transaction Metrics")

        # Read metrics
        metrics_df = storage.read_metrics("metrics")

        if metrics_df is not None and metrics_df.count() > 0:
            metrics_pd = metrics_df.toPandas()

            # Summary cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Windows", len(metrics_pd))
            with col2:
                st.metric("Total Events", int(metrics_pd['event_count'].sum()))
            with col3:
                st.metric("Total Amount", f"${metrics_pd['total_amount'].sum():.2f}")
            with col4:
                st.metric("Avg Amount", f"${metrics_pd['avg_amount'].mean():.2f}")

            # Metrics table
            st.subheader("Windowed Metrics")
            st.dataframe(metrics_pd, use_container_width=True)

            # Line chart
            st.subheader("Transaction Trends")
            metrics_pd['window_start'] = pd.to_datetime(metrics_pd['window_start'])
            metrics_pd = metrics_pd.sort_values('window_start')
            st.line_chart(metrics_pd.set_index('window_start')[['event_count', 'total_amount']])
        else:
            st.warning("No metrics data available. Run the streaming processor first.")

    with tab2:
        st.header("Detected Anomalies")

        # Read anomalies
        anomalies_df = storage.read_anomalies("anomalies")

        if anomalies_df is not None and anomalies_df.count() > 0:
            anomalies_pd = anomalies_df.toPandas()

            st.metric("Total Anomalies", len(anomalies_pd))

            st.subheader("Anomaly Details")
            st.dataframe(anomalies_pd, use_container_width=True)

            # Anomaly chart
            st.subheader("Anomaly Amounts")
            st.bar_chart(anomalies_pd.set_index('event_id')['amount'])
        else:
            st.info("No anomalies detected yet.")

    with tab3:
        st.header("Category Analytics")

        # Read category metrics (from memory if running)
        try:
            category_metrics = spark.sql("SELECT * FROM category_metrics ORDER BY window_start DESC")

            if category_metrics.count() > 0:
                category_pd = category_metrics.toPandas()

                st.subheader("Category Performance")
                st.dataframe(category_pd, use_container_width=True)

                # Category breakdown
                st.subheader("Total by Category")
                category_totals = category_pd.groupby('category')[['event_count', 'total_amount']].sum().reset_index()
                st.bar_chart(category_totals.set_index('category')['total_amount'])
            else:
                st.warning("No category metrics available.")
        except Exception as e:
            st.warning(f"Category metrics not available: {e}")

if __name__ == "__main__":
    main()
