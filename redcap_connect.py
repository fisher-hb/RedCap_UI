import redcap
import streamlit as st

API_URL = st.secrets["API_URL"]
API_TOKEN = st.secrets["API_TOKEN"]

redCapProject = redcap.Project(API_URL, API_TOKEN)
print("Connected to REDCap project.")