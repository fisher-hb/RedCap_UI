import streamlit as st
import pandas as pd
import redcap_utils
import time

st.subheader("Search Mice")

# --------------------------------------------------
# Create Search Sidebar
# --------------------------------------------------

with st.sidebar:

    status_container = st.container()

    st.subheader("Mouse Options")

    col1, col2, col3, col4 = st.columns([1.2,1,1,1],gap="xsmall")
    with col1:
        request = st.button(":primary[:material/label: Request]",width = 100)
    with col2:
        sac = st.button(":primary[:material/deceased: Sac]",width = 70)
    with col3:
        edit = st.button(":primary[:material/edit: Edit]",width = 75)
    with col4:
        view = st.button(":primary[:material/visibility: View]",width = 75)

    st.subheader("Search Parameters")

    alive = st.radio(
        "Show only Alive Mice",
        options = ["Yes","No"],
        horizontal = True,
    )

    group_view = st.selectbox(
        "Sort by Group",
        options = [None,"Cage Number", "Litter ID", "Genotype", "Requestor"],
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
        "Cage Number",
        "Flag"]
    )

    columns_select = []
    for i in columns_select_label:
        columns_select.append(redcap_utils.column_name_to_id(i))

# --------------------------------------------------
# Format Mouse Records
# --------------------------------------------------

df = st.session_state["redcap_df"].copy()
st.session_state["mice_request"] = []

df = df[(df["redcap_repeat_instrument"] == "")]

df["mouse_age_days_numeric"] = pd.to_numeric(
    df["mouse_age_days"],
    errors="coerce",
)

df["age_weeks"] = (df["mouse_age_days_numeric"] / 7).round(1)
df["age_months"] = (df["mouse_age_days_numeric"] / 30.44).round(1)

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

genotype = ""
sex = ""
min_age = ""
max_age = ""
requestor = ""
flag = ""
grouped = ""

with st.form("search_form"):
     
    col1, col2, col3 = st.columns(3)

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

    with col3:
        requestor_label = st.text_input(
            "Requestor",
        )
        requestor = requestor_label.lower()

        flag_choices = redcap_utils.get_field_choices("flag")
        flag_labels = [choice["label"] for choice in flag_choices]
            
        flag_label = st.selectbox(
            "Flag",
            options = flag_labels,
            index = None
        )

        if flag_label != None:
            flag = next(
                choice["value"]
                for choice in flag_choices
                if choice["label"] == flag_label
            )
    st.markdown("")
    st.form_submit_button("Update Search Parameters",type="primary")


if selected_genotype_variables:
    df = df[df["mouse_genotype"].isin(selected_genotype_variables)]

if sex:
    df = df[df["mouse_sex"] == "male"] if sex == "Male" else df[df["mouse_sex"] == "female"]

if min_age:
    df = df[df["age_weeks"] > float(min_age)]

if max_age:
    df = df[df["age_weeks"] < float(max_age)]

if requestor:
    df = df[df["requestor"] == requestor]

if flag:
    df = df[df["flag"] == flag]

display_df = df[columns_select]
display_df = display_df.rename(columns=column_rename_map)

st.subheader("Mouse Records")

if group_view:
    grouped = redcap_utils.group_records(df,group_view)

selected_mouse_ids = []

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
            selected_mouse_ids.append(display_df.iloc[selected_row_index]["Mouse ID"])
            i = i+1

if request:
    if selected_mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for request")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = selected_mouse_ids
        st.switch_page("pages/request_mice.py")

sac_info = []
st.session_state["sac"] = pd.DataFrame([])
if sac:
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

if view:
    if selected_mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for viewing")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = selected_mouse_ids
        st.session_state["view_type"] = "view"
        st.switch_page("pages/mouse_visualization.py")

if view:
    if selected_mouse_ids == []:
        with status_container:
            st.error("Error: No mice selected for editing")
            time.sleep(2)
            st.rerun()
    else:
        st.session_state["mice_request"] = selected_mouse_ids
        st.session_state["view_type"] = "edit"
        st.switch_page("pages/mouse_visualization.py")    

with st.sidebar:
    st.divider()