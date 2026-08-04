import streamlit as st
import pandas as pd
import redcap_utils
import time

st.subheader("New Litter")
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

col1, col2 = st.columns(2)

with col1:
    litter_id = st.text_input(
        "Litter ID",
        value = f"L{breeding_cage}_{litter_index}",
    )

    litter_dob = st.date_input(
        "Litter Date of Birth",
        format = "YYYY-MM-DD",
    )
with col2:
    notes = st.text_area(
        "Notes",
        placeholder="Optional notes about new litter",
        height="stretch"
        )
    
st.divider()
    
submission_button = st.button("Submit New Litter to Redcap", type="primary")

# --------------------------------------------------
# Format Records for RedCap Submission
# --------------------------------------------------

if submission_button:

    with status_container:

        errors = []

        if not litter_id:
            errors.append("Litter ID is required.")

        if not litter_dob:
            errors.append("Date of Birth is required.")

        if errors:
            st.write("Please fix the following issues:")

            for error in errors:
                st.error(f"{error}")

        if not errors:

            fields = {
                "redcap_repeat_instrument": "litter_information",
                "redcap_repeat_instance": str(litter_index),
                "litter_id": str(litter_id),
                "litter_dob": litter_dob.strftime("%Y-%m-%d"),
                "litter_notes_new": notes if notes else "",
                }
            redcap_utils.create_new_mouse_record(dame_id, fields)
            redcap_utils.create_new_mouse_record(sire_id, fields)
            st.success(f"Litter {litter_id} added successfully")
    
            st.info("Returning you to Breeding Cages")
    time.sleep(2)
    st.session_state["redcap_df"] = redcap_utils.load_records()
    st.switch_page("pages/breeding_cages.py")