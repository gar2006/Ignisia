import streamlit as st

from app_utils import render_outlier_graphs


st.set_page_config(page_title="Ignisia Outliers", page_icon="⚠️", layout="wide")
st.title("Outliers")

results = st.session_state.get("results")

if not results:
    st.info("Run the pipeline from the home page first to inspect outlier clusters.")
else:
    render_outlier_graphs(results)
