import streamlit as st
import pandas as pd
import redcap_utils
import time

st.subheader("New Breeding Cage")
st.markdown("")

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Litter Information
# --------------------------------------------------

df = st.session_state["redcap_df"]
mouse_names = st.session_state["mice_request"].copy()

df1 = df[(df["mouse_id"] == mouse_names[0])].reset_index(drop=True)
df2 = df[(df["mouse_id"] == mouse_names[1])].reset_index(drop=True)


if df1["mouse_sex"].iloc[0] == "male":
    sire_id = df1["mouse_id"].iloc[0]
    sire_genotype = redcap_utils.genotype_variable_to_label(df1["mouse_genotype"].iloc[0])
    sire_dob = df1["mouse_dob"].iloc[0]
    dame_id = df2["mouse_id"].iloc[0]
    dame_genotype = redcap_utils.genotype_variable_to_label(df2["mouse_genotype"].iloc[0])
    dame_dob = df2["mouse_dob"].iloc[0]
    
else:
    dame_id = df1["mouse_id"].iloc[0]
    dame_genotype = redcap_utils.genotype_variable_to_label(df1["mouse_genotype"].iloc[0])
    dame_dob = df1["mouse_dob"].iloc[0]
    sire_id = df2["mouse_id"].iloc[0]
    sire_genotype = redcap_utils.genotype_variable_to_label(df2["mouse_genotype"].iloc[0])
    sire_dob = df2["mouse_dob"].iloc[0]

st.markdown(f":primary-background[**Sire Information:**]")
cola, colb, colc, cold, cole = st.columns([0.1,1,1,1,1])
with colb:
    st.markdown(f":small[:material/pest_control_rodent: ID: {sire_id}]")
with colc:
    st.markdown(f":small[:material/genetics: Genotype: {sire_genotype}]")
with cold:
    st.markdown(f":small[:material/calendar_today: DOB: {sire_dob}]")

st.markdown(f":primary-background[**Dame Information:**]")
cola, colb, colc, cold, cole = st.columns([0.1,1,1,1,1])
with colb:
    st.markdown(f":small[:material/pest_control_rodent: ID: {dame_id}]")
with colc:
    st.markdown(f":small[:material/genetics: Genotype: {dame_genotype}]")
with cold:
    st.markdown(f":small[:material/calendar_today: DOB: {dame_dob}]")

st.divider()
cola, colb, = st.columns([2,1])
with cola:
    colc, cold = st.columns(2)
    with colc:
        breeding_cage = st.text_input(
            "Breeding Cage Number",
        )
    with cold:
        date_created = st.date_input(
            "Date Created",
            format = "YYYY-MM-DD",
        )
    notes = st.text_area(
        "Notes",
        placeholder="Optional notes about new breeding cage",
        height="stretch"
        )
    
st.divider()
    
submission_button = st.button("Submit New Breeding Cage to Redcap", type="primary")

# --------------------------------------------------
# Create Breeding Cage
# --------------------------------------------------

breed_info = []

if submission_button:

    with status_container:
        errors = []

        if breeding_cage == "":
            errors.append("Please input new cage number above.")

        if errors:
            st.write("Please fix the following issues:")
            
            for error in errors:
                st.error(f"{error}")

    # --------------------------------------------------
    # Redcap Data Submission
    # --------------------------------------------------
    
    if not errors:
        fields = {
            "mouse_transfer": "1",
            "mouse_transfer_notes": f"Mouse transferred to breeding cage: {breeding_cage}",
            "breeding_cage": breeding_cage,
            "breeding_partner": sire_id,
            "breeding_date_created": date_created.strftime("%Y-%m-%d"),
            "breeding_notes": notes,
            "breeding_information_complete": 2
        }
        redcap_utils.create_new_mouse_record(dame_id, fields)

        fields = {
            "mouse_transfer": "1",
            "mouse_transfer_notes": f"Mouse transferred to breeding cage: {breeding_cage}",
            "breeding_cage": breeding_cage,
            "breeding_partner": dame_id,
            "breeding_date_created": date_created.strftime("%Y-%m-%d"),
            "breeding_notes": notes,
            "breeding_information_complete": 2
        }
        redcap_utils.create_new_mouse_record(sire_id, fields)

        with status_container:
            st.sidebar.success(f"Breeding cage {breeding_cage} set up succesfully")
            st.sidebar.info("Returning you to Breeding Dashboard")
        
        time.sleep(2)
        st.session_state["redcap_df"] = redcap_utils.load_records()
        st.switch_page("pages/breeding_cages.py")
