import streamlit as st
import pandas as pd
import redcap_utils
import time

st.subheader("Reserve Unweaned Litter")
st.markdown("")

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Litter Information
# --------------------------------------------------

info = st.session_state["litter"].copy()

sire_id = info.loc[0, "sire_id"]
dame_id = info.loc[0, "dame_id"]
litter_index = info.loc[0, "litter_index"]
breeding_cage = info.loc[0, "breeding_cage"]

col1, col2, col3 = st.columns([1,1,2])

with col1:
    litter_id = st.text_input(
        "Litter ID",
        value = f"L{breeding_cage}_{litter_index}",
    )
    requestor = st.text_input(
        "Requestor",
    )
with col2:
    request_date = st.date_input(
        "Request Date",
        format = "YYYY-MM-DD",
    )
    litter_reservation = st.selectbox(
        "Request Purpose",
        options = ["Development","Breeding"],
        index = None,
    )
with col3:
    notes = st.text_area(
        "Request Notes",
        placeholder="Optional notes about this requst",
        height = "stretch",
    )
    
st.divider()
    
submission_button = st.button("Submit Request to Redcap", type="primary")

# --------------------------------------------------
# Format Records for RedCap Submission
# --------------------------------------------------

if submission_button:

    with status_container:

        errors = []

        if not litter_id:
            errors.append("Litter ID is required.")

        if errors:
            st.write("Please fix the following issues:")

            for error in errors:
                st.error(f"{error}")

        if not errors:

            fields = {
                "litter_reservation": litter_reservation.lower,
                "litter_reservation_notes": notes if notes else "",
                "litter_reserver": requestor,
                "litter_reservation_date": request_date.strftime("%Y-%m-%d")
                }
            
            redcap_utils.add_repeating_instance(sire_id,"litter_information",str(litter_index),fields)
            redcap_utils.add_repeating_instance(dame_id,"litter_information",str(litter_index),fields)

            st.info("Returning you to Breeding Dashboard")
    time.sleep(2)
    st.session_state["redcap_df"] = redcap_utils.load_records()
    st.switch_page("pages/breeding_dashboard.py")