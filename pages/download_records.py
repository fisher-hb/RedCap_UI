import time
import streamlit as st
import redcap_utils
import pandas as pd
from datetime import date, datetime
from pathlib import Path

mouse_ids = st.session_state["mice_request"].copy()
df = st.session_state["redcap_df"]

with st.sidebar:
    status_container = st.container()

    mouse_actions = st.menu_button(
            ":material/pest_control_rodent: **Record Actions**",
            
            options=[
                ":primary[:material/label: Request]",
                ":primary[:material/check_circle: Mark Available]",
                ":primary[:material/deceased: Sac]",
                ":primary[:material/experiment: Perform Experiment]",
                ":primary[:material/visibility: View Information]",
                ":primary[:material/edit: Edit Information]",
            ],
            width = "stretch",
        )

    st.divider()

st.subheader("Download Preferences")
st.markdown("")

cola, colb = st.columns([1,4],vertical_alignment="center")
with cola:
    mouse_info = st.checkbox("Mouse Information",value=True)
with colb:
    mouse_columns = st.multiselect(
        "Mouse Columns to Include",
        options = [
            "Mouse ID",
            "Protocol Number",
            "Ear ID Type",
            "Ear ID Number",
            "Ear ID Location",
            "Sex",
            "Date of Birth",
            "Age (Months)",
            "Age (Weeks)",
            "Age (Days)",
            "Genotype",
            "Cage Number",
            "Source",
            "Parental Cage",
            "Parental Cross",
            "Litter ID",
            "Wean/Arrival Date",
            "Genotyping Date",
            "Wellplate Number",
            "Sac Date",
            "Notes",
            "Genotyping Notes",
            "Transfer Notes",
            "Sac Notes"],
        default = [
            "Mouse ID",
            "Protocol Number",
            "Ear ID Type",
            "Ear ID Number",
            "Ear ID Location",
            "Sex",
            "Date of Birth",
            "Age (Days)",
            "Genotype",
            "Cage Number",
            "Source",
            "Parental Cage",
            "Parental Cross",
            "Litter ID",
            "Wean/Arrival Date",
            "Sac Date",
            "Notes",
            "Transfer Notes",
            "Sac Notes"] if mouse_info else [],
        label_visibility = "collapsed",
        disabled = False if mouse_info else True
    )

cola, colb = st.columns([1,4],vertical_alignment="center")
with cola:
    reservation_info = st.checkbox("Request Information")
with colb:
    reservation_columns = st.multiselect(
        "Request Columns to Include",
        options = [
            "Mouse ID",
            "Request Type",
            "Requestor",
            "Request Date",
            "Requested Experiment",
            "Requested Experiment Date",
            "Request Notes",
            "Requested Experiment Notes"],
        default = [
            "Mouse ID",
            "Request Type",
            "Requestor",
            "Request Date",
            "Requested Experiment",
            "Requested Experiment Date",
            "Request Notes",
            "Requested Experiment Notes"] if reservation_info else [],
        label_visibility = "collapsed",
        disabled = False if reservation_info else True
    )

cola, colb = st.columns([1,4],vertical_alignment="center")
with cola:
    breeding_info = st.checkbox("Breeding Information")
with colb:
    breeding_columns = st.multiselect(
        "Breeding Columns to Include",
        options = [
            "Mouse ID",
            "Breeding Cage Number",
            "Breeding Partner",
            "Date Created",
            "Date Seperated",
            "Breeding Notes"],
        default = [
            "Mouse ID",
            "Breeding Cage Number",
            "Breeding Partner",
            "Date Created",
            "Breeding Notes"] if breeding_info else [],
        label_visibility = "collapsed",
        disabled = False if breeding_info else True
    )

cola, colb = st.columns([1,4],vertical_alignment="center")
with cola:
    litter_info = st.checkbox("Litter Information")
with colb:
    litter_columns = st.multiselect(
        "Litter Columns to Include",
        options = [
            "Mouse ID",
            "Litter ID Number",
            "Litter DOB",
            "Wean Date",
            "Total Pups Weaned",
            "Total Pups Sacced",
            "Male Pups Weaned",
            "Male Pups Sacced",
            "Female Pups Weaned",
            "Female Pups Sacced",
            "Litter Notes",
            "Weaning Notes"],
        default = [
            "Mouse ID",
            "Litter ID Number",
            "Litter DOB",
            "Wean Date",
            "Total Pups Weaned",
            "Total Pups Sacced",
            "Male Pups Weaned",
            "Male Pups Sacced",
            "Female Pups Weaned",
            "Female Pups Sacced",
            "Litter Notes",
            "Weaning Notes"] if litter_info else [],
        label_visibility = "collapsed",
        disabled = False if litter_info else True
    )

cola, colb = st.columns([1,4],vertical_alignment="center")
with cola:
    experiment_info = st.checkbox("Experiment Information")
with colb:
    experiment_columns = st.multiselect(
        "Experiment Columns to Include",
        options = [
            "Mouse ID",
            "Experiment Type",
            "Experiment Date",
            "Experimentor",
            "Experiment Notes"],
        default = [
            "Mouse ID",
            "Experiment Type",
            "Experiment Date",
            "Experimentor",
            "Experiment Notes"] if experiment_info else [],
        label_visibility = "collapsed",
        disabled = False if experiment_info else True
    )

column_names = redcap_utils.get_export_columns()
column_ids = dict(
        zip(column_names["id"], column_names["name"])
    )

mouse = df[df["mouse_id"].isin(mouse_ids)]
mouse = mouse.rename(columns=column_ids)
info = mouse[mouse["redcap_repeat_instrument"]==""]
info = info[mouse_columns].copy()
reservation = mouse[mouse["redcap_repeat_instrument"]==""]
reservation = reservation[reservation_columns].copy()
breeding = mouse[mouse["redcap_repeat_instrument"]==""]
breeding = breeding[mouse["Breeding Cage Number"]!=""]
breeding = breeding[breeding_columns].copy()
litter = mouse[mouse["redcap_repeat_instrument"]=="litter_information"]
experiment = mouse[mouse["redcap_repeat_instrument"]=="experiment_information"]
experiment = experiment[experiment_columns].copy()

pages = []

if mouse_info or breeding_info or litter_info or experiment_info:
    st.divider()
    st.subheader("Preview Data")

if mouse_info:
    st.markdown("Mouse Information")
    st.dataframe(info,hide_index = True)
    pages.append("Mouse Information")

if reservation_info:
    st.markdown("Reservation Information")
    if len(reservation)>0:
        st.dataframe(reservation,hide_index = True)
        pages.append("Reservation Information")
    else:
        st.caption('<div style="padding-left: 30px; padding-bottom: 30px;">No Reservation Information to Export</div>', unsafe_allow_html=True)
     
if breeding_info:
    st.markdown("Breeding Information")
    if len(breeding)>0:
        st.dataframe(breeding,hide_index = True)
        pages.append("Breeding Information")
    else:
        st.caption('<div style="padding-left: 30px; padding-bottom: 30px;">No Breeding Information to Export</div>', unsafe_allow_html=True)
               
if litter_info:
    st.markdown("Litter Information")
    if len(litter)>0:
        st.dataframe(litter,hide_index = True)
        pages.append("Litter Information")
    else:
        st.caption('<div style="padding-left: 30px; padding-bottom: 30px;">No Litter Information to Export</div>', unsafe_allow_html=True)

if experiment_info: 
    st.markdown("Experiment Information")
    if len(experiment)>0:
        st.dataframe(experiment,hide_index = True)
        pages.append("Experiment Information")
    else:
        st.caption('<div style="padding-left: 30px; padding-bottom: 30px;">No Experiment Information to Export</div>', unsafe_allow_html=True)


from io import BytesIO

output = BytesIO()

with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    if "Mouse Information" in pages:
        info.to_excel(writer, sheet_name="Mouse Information", index=False)
    if "Reservation Information" in pages:
        reservation.to_excel(writer, sheet_name="Reservation Information", index=False)
    if "Breeding Information" in pages:
        breeding.to_excel(writer, sheet_name="Breeding Information", index=False)
    if "Litter Information" in pages:
        litter.to_excel(writer, sheet_name="Litter Information", index=False)
    if "Experiment Information" in pages:
        experiment.to_excel(writer, sheet_name="Experiment Information", index=False)

st.download_button(
    label="Download Mouse Data",
    data=output.getvalue(),
    file_name=f"{date.today().strftime("%y%m%d")}_mouse_records.xlsx",
    type = "primary",
    icon=":material/download:",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

if mouse_actions == ":primary[:material/label: Request]":
    mouse_info = df[df["mouse_id"].isin(mouse_ids)]
    reservation = mouse_info["request_flag"].tolist()
    if mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for request")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = mouse_ids
        for i in range(len(mouse_ids)):
            st.session_state[f"requestor{i}"] = ""
            st.session_state[f"request_date{i}"] = datetime.date.today()
            st.session_state[f"request_notes{i}"] = ""
            st.session_state[f"request_experiment_date{i}"] = datetime.date.today()
            st.session_state[f"request_experiment{i}"] = None
            st.session_state[f"request_experiment_notes{i}"] = ""
            st.session_state[f"new_request{i}"] = True
            st.session_state["copy_button"] == False
        st.switch_page("pages/request_mice.py")

sac_info = []
st.session_state["sac"] = pd.DataFrame([])
if mouse_actions == ":primary[:material/deceased: Sac]":
    if mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for saccing")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = mouse_ids
        sac_info.append(
                {
                    "sac_type": "Multiple Mice",
                }
            )
        st.session_state["sac"] = pd.DataFrame(sac_info)
        st.switch_page("pages/sac.py")

if mouse_actions == ":primary[:material/visibility: View Information]":
    if mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for viewing")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = mouse_ids
        st.session_state["view_type"] = "view"
        st.switch_page("pages/mouse_visualization.py")

if mouse_actions == ":primary[:material/edit: Edit Information]":
    if mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for editing")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = mouse_ids
        st.session_state["view_type"] = "edit"
        st.switch_page("pages/mouse_visualization.py")

if mouse_actions == ":primary[:material/experiment: Perform Experiment]":
    if mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for experiment")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = mouse_ids
        st.session_state["view_type"] = 1
        st.switch_page("pages/perform_experiment.py")    

if mouse_actions == ":primary[:material/check_circle: Mark Available]":
    if mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = mouse_ids
        @st.dialog("Verify Submission")
        def submit_available():
            selected_mouse_ids = st.session_state["mice_request"]
            st.write(f"Please verify that the following mice should be marked as available. :red[Note: This will overwrite any current reservations.]")
            st.dataframe(selected_mouse_ids,column_config={"value": "Mouse"})
            if st.button("Verify",type="primary"):
                st.success("Mice marked as available")
                df = st.session_state["redcap_df"].reset_index(drop=True)
                for i in range(len(selected_mouse_ids)):
                    df = df[df["redcap_repeat_instrument"]==""]
                    mouse = df[df["mouse_id"]==selected_mouse_ids[i]]
                    current_notes = f"{mouse["request_notes"].iloc[0]}\n{mouse["request_experiment_notes"].iloc[0]}"
                    if mouse["request_person"].iloc[0] == "":
                        notes = current_notes
                    else:
                        notes = f"Previously reserved by: {mouse["request_person"].iloc[0].title()} for {mouse["request_experiment"].iloc[0].replace("_"," ")}\n {current_notes}"
                    fields = {
                        "request_flag": "available",
                        "request_person": " ",
                        "request_date": "",
                        "request_notes": notes,
                        "request_experiment": "",
                        "request_experiment_date": "",
                        "request_experiment_notes": " ",
                    }
                    redcap_utils.create_new_mouse_record(selected_mouse_ids[i], fields)
                st.info("Reloading Database")
                st.session_state["redcap_df"] = redcap_utils.load_records()
                st.rerun()

        submit_available()