import streamlit as st
import matplotlib.pyplot as plt
import redcap_utils

# --------------------------------------------------
# Create Mice Dashboard Tab
# --------------------------------------------------

def create_mice(current_df, current_experimental, current_breeding):
    st.subheader("Dashboard")