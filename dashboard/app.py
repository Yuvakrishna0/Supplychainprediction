import os
import pandas as pd
import psycopg2
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine, text

# ---- CONFIG ----
st.set_page_config(page_title="Supply Chain Risk Dashboard", layout="wide")

# ---- TITLE ----
st.title("🌍 Supply Chain Disruption Early Warning System")

st.markdown("""
This dashboard visualizes **daily AI-predicted supply chain disruption risks**.
Data is fetched directly from the live Neon PostgreSQL database.
""")

# ---- DATABASE CONNECTION ----
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://neondb_owner:npg_k5JYXPoFzM1N@ep-wandering-salad-a1c7264o-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)

engine = create_engine(DATABASE_URL)

@st.cache_data(ttl=600)
def load_scores():
    try:
        q = "SELECT * FROM scores_daily ORDER BY ds;"
        return pd.read_sql(q, engine)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame()

df = load_scores()

if df.empty:
    st.warning("⚠️ No predictions available yet. Please run your training pipeline first.")
else:
    st.success("✅ Data loaded successfully")

    # ---- RISK LINE CHART ----
    st.header("📈 Daily Predicted Supply Chain Risk")
    fig = px.line(df, x="ds", y="risk_p",
                  title="Risk Probability Over Time",
                  markers=True, template="plotly_dark")
    fig.update_layout(yaxis_title="Risk Probability (0–1)", xaxis_title="Date")
    st.plotly_chart(fig, use_container_width=True)

    # ---- TABLE ----
    st.subheader("📋 Latest Predictions")
    st.dataframe(df.tail(10))

    # ---- WORLD MAP / COUNTRY RISK ----
    st.header("🌐 Global Risk Heatmap (by Country)")
    try:
        q = """
        SELECT re."ActionGeo_CountryCode" as country, AVG(s.risk_p) as avg_risk
        FROM raw_events re
        JOIN scores_daily s ON DATE(re.event_time) = s.ds
        GROUP BY country;
        """
        country_df = pd.read_sql(text(q), engine)

        if not country_df.empty:
            fig_map = px.choropleth(
                country_df,
                locations="country",
                color="avg_risk",
                color_continuous_scale="Reds",
                title="Average Predicted Supply Chain Risk by Country",
                projection="natural earth"
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No geographic data yet for risk mapping.")
    except Exception as e:
        st.error(f"Map generation failed: {e}")

st.markdown("---")
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
