import time
import streamlit as st
import redcap_utils
from datetime import date, datetime

mouse_ids = st.session_state["mice_request"].copy()
df = st.session_state["redcap_df"]

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Request Information
# --------------------------------------------------

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Request Information")
with col2:
    request_type = st.radio(
        "Request Type",
        options=["Reserved", "Breeding", "Plan to Sac"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        key="request_type",
    )


for i, mouse_id in enumerate(mouse_ids):

    mouse_df = df[df["redcap_repeat_instrument"] == ""]
    mouse_df = mouse_df[mouse_df["mouse_id"] == mouse_id]

    with st.expander(f"{mouse_id}", expanded=(i == 0)):
        st.markdown("")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f":primary-background[**Mouse ID -- {mouse_id}**]")
        with col2:
            if i == 0 and len(mouse_ids)>1:
                copy_info = st.button(
                    ":material/content_copy: Copy Request Info to All Mice",
                    type="tertiary"
                )
            else:
                copy_info = False

        st.session_state[f"requestor{i}"] = mouse_df["request_person"].iloc[0]
        st.session_state[f"request_date{i}"] = None if mouse_df["request_date"].iloc[0] == "" else datetime.strptime(mouse_df["request_date"].iloc[0], "%Y-%m-%d").date()
        st.session_state[f"request_notes{i}"] = mouse_df["request_notes"].iloc[0]
        st.session_state[f"request_experiment_date{i}"] = None if mouse_df["request_experiment_date"].iloc[0] == "" else datetime.strptime(mouse_df["request_experiment_date"].iloc[0], "%Y-%m-%d").date()
        st.session_state[f"request_experiment{i}"] = mouse_df["request_experiment"].iloc[0].title().replace("_"," ")
        st.session_state[f"request_experiment_notes{i}"] = mouse_df["request_experiment_notes"].iloc[0]

        if copy_info == True:
            for j in range(1,len(mouse_ids)):
                st.session_state[f"requestor{j}"] = st.session_state["requestor0"]
                st.session_state[f"request_date{j}"] = st.session_state["request_date0"]
                st.session_state[f"request_notes{j}"] = st.session_state["request_notes0"]
                st.session_state[f"request_experiment_date{j}"] = st.session_state["request_experiment_date0"]
                if request_type == "Reserved":
                    st.session_state[f"request_experiment{j}"] = st.session_state["request_experiment0"]
                    st.session_state[f"request_experiment_notes{j}"] = st.session_state["request_experiment_notes0"]
                    st.rerun()

        col1, col2 = st.columns([1, 2])
        with col1:
            requestor = st.text_input(
                "Requestor",
                key=f"requestor{i}",
            )
            request_date = st.date_input(
                "Request Date",
                format="YYYY-MM-DD",
                key=f"request_date{i}",
            )
        with col2:
            request_notes = st.text_area(
                "Request Notes",
                placeholder="Optional notes about request.",
                key=f"request_notes{i}",
                height = "stretch",
            )

        if request_type == "Reserved":
            st.divider()

            col1, col2 = st.columns([1, 2])

            with col1:
                request_experiment = st.selectbox(
                    "Planned Experiment",
                    options=[
                        "Staining",
                        "Ephys",
                        "CSPOT",
                        "OMR",
                        "Practice",
                        "ERG",
                        "Calcium Imaging",
                        "Retina Degeneration Evaluation",
                        "Antibody Testing",
                        "Cre Testing",
                        "Other",
                    ],
                    key=f"request_experiment{i}",
                )

                request_experiment_date = st.date_input(
                    "Anticipated Experiment Date",
                    format="YYYY-MM-DD",
                    key=f"request_experiment_date{i}",
                    value = "today"
                )

            with col2:
                request_experiment_notes = st.text_area(
                    "Experiment Notes",
                    placeholder="Optional notes about experiment.",
                    key=f"request_experiment_notes{i}",
                    height = "stretch",
                )

        elif request_type == "Breeding":
            with col1:
                request_experiment_date = st.date_input(
                    "Anticipated Breeding Date",
                    format="YYYY-MM-DD",
                    key=f"request_experiment_date{i}",
                    value = "today"
                )

        else:
            with col1:
                request_experiment_date = st.date_input(
                    "Anticipated Sac Date",
                    format="YYYY-MM-DD",
                    key=f"request_experiment_date{i}",
                    value = "today"
                )

        st.markdown("")
# --------------------------------------------------
# Submit
# --------------------------------------------------

st.divider()
request_submit = st.button("Submit Request", type="primary")

if request_submit:
    errors = []

    for i, mouse_id in enumerate(mouse_ids):
        if not st.session_state.get(f"requestor{i}", "").strip():
            errors.append(f"{mouse_id}: Requestor Name is required.")

    if errors:
        with status_container:
            st.markdown("Please fix the following issues:")
            for error in errors:
                st.error(error)
            st.divider()

    else:
        with status_container:
            for i, mouse_id in enumerate(mouse_ids):
                fields = {
                    "request_flag": request_type.lower().replace(" ", "_"),
                    "request_person": st.session_state[f"requestor{i}"],
                    "request_date": st.session_state[f"request_date{i}"].strftime("%Y-%m-%d"),
                    "request_notes": st.session_state[f"request_notes{i}"],
                    "request_experiment_date": st.session_state[f"request_experiment_date{i}"].strftime("%Y-%m-%d"),
                    "request_complete": 2,
                }

                if request_type == "Reserved":
                    fields["request_experiment"] = st.session_state[f"request_experiment{i}"]
                    fields["request_experiment_notes"] = st.session_state[f"request_experiment_notes{i}"]

                redcap_utils.create_new_mouse_record(mouse_id, fields)
                st.success(f"Mouse {mouse_id} requested successfully")

            st.info("Returning you to Mouse Search")
            st.divider()

        time.sleep(2)
        st.session_state["redcap_df"] = redcap_utils.load_records()
        st.switch_page("pages/search_mice.py")