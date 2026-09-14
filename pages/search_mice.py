import streamlit as st
import pandas as pd
import redcap_utils
import time
import datetime

st.subheader("Search Mice")
flag = ""

# --------------------------------------------------
# Create Search Sidebar
# --------------------------------------------------

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
            ":primary[:material/favorite: Create Breeding Cage]"
        ],
        width = "stretch",
    )

    st.subheader("Search Parameters")

    alive = st.radio(
        "Show only Alive Mice",
        options = ["Yes","No"],
        horizontal = True,
    )

    flag_choices = redcap_utils.get_field_choices("request_flag")
    flag_labels = [choice["label"] for choice in flag_choices]
        
    flag_label = st.selectbox(
        "Request Flag",
        options = flag_labels,
        index = None,
    )

    if flag_label != None:
        flag = next(
            choice["value"]
            for choice in flag_choices
            if choice["label"] == flag_label
        )

    group_view = st.selectbox(
        "Sort by Group",
        options = [None,"Cage Number", "Litter ID", "Genotype"],
        index = 1,
    )

    columns = redcap_utils.get_columns()
    column_ids = columns["id"].tolist()
    column_names = columns["name"].tolist()

    column_rename_map = dict(
        zip(column_ids, column_names)
    )

    columns_select_label = st.multiselect(
        "Display Columns",
        options = column_names,
        default = ["Mouse ID",
        "Sex",
        "Age (Days)",
        "Genotype",
        "Cage Number",
        "Request Flag",
        "Requestor"]
    )

    columns_select = []
    for i in columns_select_label:
        columns_select.append(redcap_utils.column_name_to_id(i))

# --------------------------------------------------
# Format Mouse Records
# --------------------------------------------------

df = st.session_state["redcap_df"].copy()
st.session_state["mice_request"] = []

upload_csv = pd.read_csv("genotypes.csv",dtype="str")
genotype_df = upload_csv
parental_cross_choices = genotype_df["Breeding Cross"].tolist()

genotype_choices = redcap_utils.get_genotypes()
genotype_labels = genotype_choices["label"]
genotype_variables = genotype_choices["variable"]

genotype_label_to_variable_map = dict(
    zip(genotype_labels, genotype_variables)
)
genotype_variable_to_label_map = dict(
    zip(genotype_variables, genotype_labels)
)

if alive == "Yes":
    df = df[df["mouse_sac_date"].astype(str).str.strip() == ""]

# --------------------------------------------------
# Search Mice
# --------------------------------------------------

grouped = ""
     
col1, col2, col3, col4 = st.columns(4,border = True)

with col1:
    mouse_number = st.text_input(
        "ID Number",
        placeholder = "Example: 501",
    )
    cage_number = st.text_input(
            "Cage Number",
            placeholder = "Example: 234567",
        )
    litter_number = st.text_input(
                "Litter Number",
                placeholder = "Example: L123456_1",
            )
with col2:
    selected_genotype_labels = st.multiselect(
        "Mouse Genotype",
        options=genotype_labels,
    )
    selected_genotype_variables = [
        genotype_label_to_variable_map[label]
        for label in selected_genotype_labels
    ]
    parental_cross = st.selectbox(
            "Parental Cross",
            options = parental_cross_choices,
            index = None,
        )
    parental_cage = st.text_input(
                "Parent Cage Number",
                placeholder = "Example: 123456",
            )
with col3:
    sex = st.selectbox(
            "Mouse Sex",
            options = ["Male","Female"],
            index = None,
        )
    min_age = st.text_input(
            "Minimum Age in Days",
            placeholder = "Example: 30",
        )
                
    max_age = st.text_input(
        "Maximum Age in Days",
        placeholder = "Example: 90",
    ) 
with col4:
    requestor = st.text_input(
            "Requestor",
            placeholder = "Name",
        )
    requested_experiment = st.multiselect(
        "Requested Experiment",
        options = ["Staining", 
                    "Ephys",
                    "CSPOT",
                    "OMR",
                    "Practice",
                    "ERG",
                    "Calcium Imaging",
                    "Retina Degeneration Evaluation",
                    "Antibody Testing",
                    "Cre Testing",
                    "Other"],
    )
    performed_experiment = st.multiselect(
        "Performed Experiment",
        options = ["Staining", 
                    "Ephys",
                    "CSPOT",
                    "OMR",
                    "Practice",
                    "ERG",
                    "Calcium Imaging",
                    "Retina Degeneration Evaluation",
                    "Antibody Testing",
                    "Cre Testing",
                    "Other"],
    )
st.divider()

if mouse_number:
    mice_ids = redcap_utils.find_id_from_sample(mouse_number,return_all = True)
    if mice_ids is None:
        df = df[df["mouse_id"]==""]
    else:
        df = df[df["mouse_id"].isin(mice_ids.tolist())]

if cage_number:
    df = df[df["mouse_cage_number"] == cage_number]

if litter_number:
    df = df[df["mouse_litter_id"] == litter_number]

if selected_genotype_variables:
    df = df[df["mouse_genotype"].isin(selected_genotype_variables)]

if parental_cross:
    df = df[df["mouse_parental_cross"] == parental_cross]

if parental_cage:
    df = df[df["mouse_parental_cage"] == parental_cage]

if sex:
    df = df[df["mouse_sex"] == sex.lower()]

if min_age:
    df["mouse_age_days"] = pd.to_numeric(df["mouse_age_days"], errors="coerce")
    df = df[df["mouse_age_days"] >= float(min_age)]

if max_age:
    df["mouse_age_days"] = pd.to_numeric(df["mouse_age_days"], errors="coerce")
    df = df[df["mouse_age_days"] <= float(max_age)]

if requestor:
    df = df[df["request_person"].str.lower() == requestor.lower()]

if requested_experiment:
    requested_experiments = [s.lower().replace(" ","_") for s in requested_experiment]
    df = df[df["request_experiment"].isin(requested_experiments)]

if performed_experiment:
    performed_experiments = [s.lower().replace(" ","_") for s in performed_experiment]
    mice_ids = df[df["experiment_type"].isin(performed_experiments)]
    mice_ids = mice_ids["mouse_id"].tolist()
    df = df[df["mouse_id"].isin(mice_ids)]

if flag:
    df = df[df["request_flag"] == flag]

df = df[df["redcap_repeat_instrument"]==""].reset_index(drop=True)

display_df = df[columns_select]
display_df = display_df.rename(columns=column_rename_map)

st.subheader("Mouse Records")

if group_view:
    grouped = redcap_utils.group_records(df,group_view)

selected_mouse_ids = []
selected_mouse_sexes = []

if grouped:
    for group_value, group_df in grouped:
        group_label = str(group_value)

        if group_view == "Genotype":
            group_label = redcap_utils.genotype_variable_to_label(str(group_value))
        else:
            group_label = str(group_value)

        if len(group_df)>1:
            st.markdown(f"**:primary-background[{group_view}: {group_label} — {len(group_df)} mice]**")
        else:
            st.markdown(f"**:primary-background[{group_view}: {group_label} — {len(group_df)} mouse]**")
        display_df = group_df[columns_select].copy()

        display_df = display_df.rename(columns=column_rename_map)

        if "Genotype" in display_df.columns:
            display_df["Genotype"] = (
                display_df["Genotype"]
                .map(genotype_variable_to_label_map)
            )

        event = st.dataframe(
            display_df,
            width="stretch",
            hide_index=True,
            on_select = "rerun",
            selection_mode="multi-row",
        )

        if event.selection.rows:
            i = 0
            while i < len(event.selection.rows):
                selected_row_index = event.selection.rows[i]
                selected_mouse_sexes.append(display_df.iloc[selected_row_index]["Sex"])
                selected_mouse_ids.append(display_df.iloc[selected_row_index]["Mouse ID"])
                i = i+1

        st.divider()

else:
    if "Genotype" in display_df.columns:
        display_df["Genotype"] = (
            display_df["Genotype"]
            .map(genotype_variable_to_label_map)
        )

    event = st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        on_select = "rerun",
        selection_mode="multi-row",
    )

    if event.selection.rows:
        i = 0
        while i < len(event.selection.rows):
            selected_row_index = event.selection.rows[i]
            selected_mouse_sexes.append(display_df.iloc[selected_row_index]["Sex"])
            selected_mouse_ids.append(display_df.iloc[selected_row_index]["Mouse ID"])
            i = i+1

if mouse_actions == ":primary[:material/label: Request]":
    mouse_info = df[df["mouse_id"].isin(selected_mouse_ids)]
    reservation = mouse_info["request_flag"].tolist()
    if selected_mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for request")
            time.sleep(2)
            st.rerun()
    #elif any(flag == "reserved" for flag in reservation):
    #    with status_container:
    #        st.error("Error: One or more selected mice are reserved and cannot be requested.")
    #        time.sleep(2)
    #        st.rerun()
    else:
        st.session_state["mice_request"] = selected_mouse_ids
        for i in range(len(selected_mouse_ids)):
            st.session_state[f"requestor{i}"] = ""
            st.session_state[f"request_date{i}"] = datetime.date.today()
            st.session_state[f"request_notes{i}"] = ""
            st.session_state[f"request_experiment_date{i}"] = datetime.date.today()
            st.session_state[f"request_experiment{i}"] = None
            st.session_state[f"request_experiment_notes{i}"] = ""
        st.switch_page("pages/request_mice.py")

sac_info = []
st.session_state["sac"] = pd.DataFrame([])
if mouse_actions == ":primary[:material/deceased: Sac]":
    if selected_mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for saccing")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = selected_mouse_ids
        sac_info.append(
                {
                    "sac_type": "Multiple Mice",
                }
            )
        st.session_state["sac"] = pd.DataFrame(sac_info)
        st.switch_page("pages/sac.py")

if mouse_actions == ":primary[:material/visibility: View Information]":
    if selected_mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for viewing")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = selected_mouse_ids
        st.session_state["view_type"] = "view"
        st.switch_page("pages/mouse_visualization.py")

if mouse_actions == ":primary[:material/edit: Edit Information]":
    if selected_mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for editing")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = selected_mouse_ids
        st.session_state["view_type"] = "edit"
        st.switch_page("pages/mouse_visualization.py")

if mouse_actions == ":primary[:material/experiment: Perform Experiment]":
    if selected_mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for experiment")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = selected_mouse_ids
        st.session_state["view_type"] = 1
        st.switch_page("pages/perform_experiment.py")    

if mouse_actions == ":primary[:material/check_circle: Mark Available]":
    if selected_mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected")
            time.sleep(2)
            st.rerun()
    else:
        for i in range(len(selected_mouse_ids)):
            df = df[df["redcap_repeat_instrument"]==""]
            mouse = df[df["mouse_id"]==selected_mouse_ids[i]]
            current_notes = f"{mouse["request_notes"].iloc[0]}\n{mouse["request_experiment_notes"].iloc[0]}"
            notes = f"Previously reserved by: {mouse["request_person"].iloc[0].title()} for {mouse["request_experiment"].iloc[0].replace("_"," ")}\n {current_notes}"
            fields = {
                "request_flag": "available",
                "request_person": "",
                "request_date": "",
                "request_notes": notes,
                "request_experiment": "",
                "request_experiment_date": "",
                "request_experiment_notes": "",
            }
            redcap_utils.create_new_mouse_record(selected_mouse_ids[i], fields)
        st.session_state["redcap_df"] = redcap_utils.load_records()
        st.rerun()

if mouse_actions == ":primary[:material/favorite: Create Breeding Cage]":
    with status_container:
        errors = []
        if selected_mouse_ids == []:
            errors.append("No mice selected for breeding.")
        if not "female" in selected_mouse_sexes:
            errors.append("Please select at least one dame.")
        if not "male" in selected_mouse_sexes:
            errors.append("Please select one sire.")
        options = [
            ['male','female'],
            ['female','male'],
            ['male','female','female'],
            ['female','male','female'],
            ['female','female','male']
        ]
        if not selected_mouse_sexes in options:
            errors.append("Please make sure to select one of the approved breeding schemes (1M x 1F or 1M x 2F)")
        if errors:
            st.write("Please fix the following issues:")
            for error in errors:
                st.error(f"{error}")
                time.sleep(3)
                st.rerun()
        if not errors:
            st.session_state["mice_request"] = selected_mouse_ids
            st.switch_page("pages/new_breeding_cage.py")

with st.sidebar:
    st.divider()

st.session_state["mouse_info"] = pd.DataFrame(columns=df.columns.tolist())
st.session_state["mouse_editor_initialized"] = False