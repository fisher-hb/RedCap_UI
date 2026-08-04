import streamlit as st
import pandas as pd
import redcap_utils
import time

st.subheader("Create New Breeding Cage")

# --------------------------------------------------
# Create Search Sidebar
# --------------------------------------------------

with st.sidebar:

    status_container = st.container()
    
    st.subheader("New Breeding Cage Info")

    cage_num = st.text_input(
        "New Breeding Cage Number",
        label_visibility = "collapsed",
        placeholder = "Enter new breeding cage number"
    )

    cage_date = st.date_input(
            "Date of Creation",
            format = "YYYY-MM-DD",
            label_visibility = "collapsed"
        )

    breed = st.button(
        "Create Breeding Cage",
        width = "stretch",
        type = "primary"
    )

    st.divider()
    st.subheader("Search Parameters")

    labeled = st.toggle(
        "Show Only Mice Marked for Breeding",
        value = False
    )

    group_view = st.selectbox(
        "Sort by Group",
        options = [None,"Cage Number", "Litter ID", "Genotype", "Flag"],
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
        "Age (Weeks)",
        "Genotype",
        "Cage Number"]
    )

    columns_select = []
    for i in columns_select_label:
        columns_select.append(redcap_utils.column_name_to_id(i))

    st.divider()

# --------------------------------------------------
# Format Mouse Records
# --------------------------------------------------

df = st.session_state["redcap_df"].copy()
st.session_state["mice_request"] = []

if "redcap_repeat_instrument" in df.columns:
        df = df[
            (df["redcap_repeat_instrument"].isna())
            | (df["redcap_repeat_instrument"].astype(str).str.strip() == "")
        ]

df["mouse_age_days_numeric"] = pd.to_numeric(
    df["mouse_age_days"],
    errors="coerce",
)

df["age_weeks"] = (df["mouse_age_days_numeric"] / 7).round(1)
df["age_months"] = (df["mouse_age_days_numeric"] / 30.44).round(1)

df = df[df["mouse_sac_date"].astype(str).str.strip() == ""]
df = df[df["breeding_cage"].astype(str).str.strip() == ""]

# --------------------------------------------------
# Search Parameters
# --------------------------------------------------

genotype = ""
sex = ""
min_age = ""
max_age = ""
requestor = ""
flag = ""
grouped = ""

with st.form("search_form"):
     
    col1, col2 = st.columns(2)

    genotype_choices = redcap_utils.get_genotypes()
    genotype_labels = genotype_choices["label"]
    genotype_variables = genotype_choices["variable"]
    
    genotype_label_to_variable_map = dict(
        zip(genotype_labels, genotype_variables)
    )
    genotype_variable_to_label_map = dict(
        zip(genotype_variables, genotype_labels)
    )

    with col1:

        selected_genotype_labels = st.multiselect(
            "Mouse Genotype",
            options=genotype_labels,
        )
            
        selected_genotype_variables = [
            genotype_label_to_variable_map[label]
            for label in selected_genotype_labels
        ]
        
        sex = st.selectbox(
            "Mouse Sex",
            options = ["Male","Female"],
            index = None,
        )
            
    with col2:
        min_age = st.text_input(
            "Minimum Age in Weeks",
            placeholder = "Example: 8",
        )
        
        max_age = st.text_input(
            "Maximum Age in Weeks",
            placeholder = "Example: 16",
        )

    st.markdown("")
    st.form_submit_button("Update Search Parameters",type="primary")

# --------------------------------------------------
# Define Dataset based on Search Parameters
# --------------------------------------------------

if selected_genotype_variables:
    df = df[df["mouse_genotype"].isin(selected_genotype_variables)]

if labeled:
    df = df[df["flag"]=="breeding"]

if sex:
    df = df[df["mouse_sex"] == "male"] if sex == "Male" else df[df["mouse_sex"] == "female"]

if min_age:
    df = df[df["age_weeks"] > int(min_age)]

if max_age:
    df = df[df["age_weeks"] < int(max_age)]

display_df = df[columns_select]
display_df = display_df.rename(columns=column_rename_map)

# --------------------------------------------------
# Display Mouse Records
# --------------------------------------------------

st.subheader("Mouse Records")

if group_view:
    grouped = redcap_utils.group_records(df,group_view)

selected_mouse_ids = []
selected_mouse_sexes = []

if grouped:
    for group_value, group_df in grouped:

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
                selected_mouse_ids.append(display_df.iloc[selected_row_index]["Mouse ID"])
                selected_mouse_sexes.append(display_df.iloc[selected_row_index]["Sex"])
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
            selected_mouse_ids.append(display_df.iloc[selected_row_index]["Mouse ID"])
            i = i+1

# --------------------------------------------------
# Create Breeding Cage
# --------------------------------------------------

breed_info = []

if breed:

    with status_container:
        errors = []

        if cage_num == "":
            errors.append("Please input new cage number above.")

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

    # --------------------------------------------------
    # Redcap Data Submission
    # --------------------------------------------------
    
    if not errors:
        fields = {
            "mouse_transfer": "1",
            "mouse_transfer_notes": f"Mouse transferred to breeding cage: {cage_num}",
            "breeding_cage": cage_num,
            "breeding_partner": selected_mouse_ids[1],
            "breeding_date_created": cage_date.strftime("%Y-%m-%d"),
        }
        redcap_utils.create_new_mouse_record(selected_mouse_ids[0], fields)

        fields = {
            "mouse_transfer": "1",
            "mouse_transfer_notes": f"Mouse transferred to breeding cage: {cage_num}",
            "breeding_cage": cage_num,
            "breeding_partner": selected_mouse_ids[0],
            "breeding_date_created": cage_date.strftime("%Y-%m-%d"),
        }
        redcap_utils.create_new_mouse_record(selected_mouse_ids[1], fields)

        with status_container:
            st.sidebar.success(f"Breeding cage {cage_num} set up succesfully")
            st.sidebar.info("Returning you to Breeding Dashboard")
        
        time.sleep(2)
        st.session_state["redcap_df"] = redcap_utils.load_records()
        st.switch_page("pages/breeding_cages.py")
