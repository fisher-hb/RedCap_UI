import streamlit as st
import redcap_utils
import time

st.subheader("New Request")

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Display Mouse Information
# --------------------------------------------------

mouse_ids = st.session_state["mice_request"].copy()
df = st.session_state["redcap_df"].copy()
number_of_mice = len(mouse_ids)

print(number_of_mice)

display_columns = [
    "mouse_id", "mouse_sex", "mouse_age_weeks", "mouse_genotype", "mouse_cage_number",
    "mouse_ear_id_location", "mouse_dob", "mouse_age_days", "mouse_age_months",
    "mouse_parental_cage", "mouse_litter_id", "mouse_arrival_date", 
    "mouse_genotyping_date", "mouse_wellplate_number", "mouse_notes",
]

df = df[df["mouse_id"].isin(mouse_ids)]

df_request = df[display_columns].copy()

columns_df = redcap_utils.get_columns()
column_rename_map = dict(zip(columns_df["id"], columns_df["name"]))

# df_request = df.copy()
df_request = df_request.rename(columns=column_rename_map)

genotypes_df = redcap_utils.get_genotypes()
genotype_rename_map = dict(zip(genotypes_df["variable"], genotypes_df["label"]))

df_request["Genotype"] = (df_request["Genotype"].map(genotype_rename_map))

request_mice = st.dataframe(
        df_request,
        width="stretch",
        hide_index=True,
    )

csv = df_request.to_csv().encode("utf-8")
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="request_data.csv",
    mime="text/csv",
    icon=":material/download:",
)

# --------------------------------------------------
# Request Information
# --------------------------------------------------

st.divider()
st.subheader("Request Information")

col1, col2 = st.columns([1,2])
with col1:  
    requestor = st.text_input(
        "Requestor",
    )
    request_date = st.date_input(
        "Request Date",
        format = "YYYY-MM-DD",
    )
with col2:
    notes_request = st.text_area(
        "Request Notes",
        placeholder = "Optional notes about request.",
        height = "stretch",
    )

st.divider()

col1, col2 = st.columns([1,2])
with col1:  
    experiment = st.text_input(
        "Planned Experiment(s)",
    )
    experiment_date = st.date_input(
        "Anticipated Experiment Date",
        format = "YYYY-MM-DD",
    )
with col2:
    notes_experiment = st.text_area(
        "Experiment Notes",
        placeholder = "Optional notes about experiment.",
        height = "stretch",
    )

st.divider()
request_submit = st.button("Submit Request", type="primary")

if request_submit:
    errors = []
    if not requestor:
        errors.append("Requestor Name is Required.")
    if errors:
        with status_container:
            st.markdown("Please fix the following issues:")
            for error in errors:
                st.error(f"{error}")
            st.divider()
    
    if not errors:
        with status_container:
            for i in range(number_of_mice):
                fields = {
                    "flag": "reserved",
                    "request_person": requestor,
                    "request_date": request_date.strftime("%Y-%m-%d"),
                    "request_notes": notes_request,
                    "request_experiment": experiment,
                    "request_experiment_date": experiment_date.strftime("%Y-%m-%d"),
                    "request_experiment_notes": notes_experiment,
                    "request_complete": 2
                    }
                redcap_utils.create_new_mouse_record(mouse_ids[i], fields)
                st.success(f"Mouse  {mouse_ids[i]}  requested succesfully")
            st.info("Returning you to Mouse Search")
            st.divider()
        time.sleep(2)
        st.switch_page("pages/search_mice.py")