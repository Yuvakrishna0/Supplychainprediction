# dashboard/app.py
import os
import pandas as pd
import psycopg2
import streamlit as st
import plotly.express as px

# ---- CONFIG ----
st.set_page_config(page_title="Supply Chain Risk Dashboard", layout="wide")

# Get Neon connection from environment variable or manual paste
DATABASE_URL = 'postgresql://neondb_owner:npg_k5JYXPoFzM1N@ep-wandering-salad-a1c7264o-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

# ---- TITLE ----
st.title("🌍 Supply Chain Disruption Early Warning System")

st.markdown("""
This dashboard shows daily predicted risk levels for supply chain disruptions.
Data is fetched directly from the Neon PostgreSQL database.
""")

# ---- DATABASE CONNECTION ----
@st.cache_data(ttl=3600)
def load_data():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        df = pd.read_sql("SELECT * FROM scores_daily ORDER BY ds;", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data available in Neon database yet. Run your notebook first.")
else:
    st.success("Data loaded successfully ✅")

    # ---- PLOT ----
    fig = px.line(df, x="ds", y="risk_p", title="Daily Predicted Supply Chain Risk Probability", markers=True)
    fig.update_layout(yaxis_title="Risk Probability (0-1)", xaxis_title="Date", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # ---- TABLE ----
    st.subheader("📋 Latest Predictions")
    st.dataframe(df.tail(10))
