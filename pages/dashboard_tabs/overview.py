import streamlit as st

# --------------------------------------------------
# Create Overview Dashboard Tab
# --------------------------------------------------

def create_overview(current_df, current_experimental, current_breeding):
    st.subheader("Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col4:
        non_breeding_cages = (current_experimental["mouse_cage_number"])
        st.metric("Current Non-Breeding Cages",non_breeding_cages.nunique()) 
    with col3:
        breeding_cages = (current_breeding["breeding_cage"])
        st.metric("Current Breeding Cages",breeding_cages.nunique()) 
    with col2:
        st.metric("Current Cages",non_breeding_cages.nunique()+breeding_cages.nunique()) 
    with col1:
        st.metric("Current Mice", len(current_df))