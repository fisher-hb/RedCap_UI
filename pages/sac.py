import streamlit as st
import pandas as pd
import redcap_utils
import time

st.subheader("Sac Mice")
st.markdown("")

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Data Load
# --------------------------------------------------

df = st.session_state["redcap_df"]
df = df[df["redcap_repeat_instrument"] == ""]
df = df[df["mouse_sac_date"] == ""]
errors = []

# --------------------------------------------------
# Sac Information
# --------------------------------------------------

if st.session_state["sac"].empty:
    sac_type_input = None
elif "sac_type" not in st.session_state["sac"].columns:
    sac_type_input = None
else:
    info = st.session_state["sac"].copy()
    sac_type_value = info["sac_type"].iloc[0]
    if pd.isna(sac_type_value) or str(sac_type_value).strip() == "":
        sac_type_input = None
    else:
        sac_type_input = str(sac_type_value).strip()

if sac_type_input == "Breeding Cage":
    index = 0
elif sac_type_input == "Multiple Mice":
    index = 4
else:
    index = 3

sac_type = st.radio(
"Sac Type",
options = ["Breeding Cage","Single Cage", "Multiple Cages", "Individual Mouse", "Multiple Mice"],
label_visibility = "collapsed",
horizontal = True,
index = index,
)

st.divider()

if sac_type == None:
    buffer = 1;
elif sac_type == "Individual Mouse" or sac_type == "Multiple Mice":
    st.subheader("Mouse Information")
else:
    st.subheader("Cage Information")

# --------------------------------------------------
# Sac Breeding Cage
# --------------------------------------------------

breeding_cage_submit = False

if sac_type == "Breeding Cage":
    if sac_type_input == "Breeding Cage":
        sire_id = info.loc[0, "sire_id"]
        dame_id = info.loc[0, "dame_id"]
        breeding_cage = info.loc[0, "breeding_cage"]
    else:
        sire_id = ""
        dame_id = ""
        breeding_cage = ""
    
    col1, col2 = st.columns([1,1])

    with col1:
        cola, colb = st.columns([1,0.1],vertical_alignment = "center")
        with cola:
            cage_number = st.text_input(
                "Breeding Cage Number",
                value = breeding_cage
            )
        with colb:
            sac_df = df[df["breeding_cage"] == cage_number]
            sac_df = sac_df[sac_df["mouse_sac_date"] == ""]
            if sac_df.empty or cage_number == "":
                st.markdown("")
                st.caption(":red[:material/error:]")
                errors.append("Breeding cage number not found")
            else:
                sire_id = sac_df[sac_df["mouse_sex"] == "male"]["mouse_id"].iloc[0]
                dame_id = sac_df[sac_df["mouse_sex"] == "female"]["mouse_id"].iloc[0]
                st.markdown("")
                st.caption(":green[:material/check_circle:]")

        cola, colb = st.columns([1,0.1],vertical_alignment = "center")
        with cola:
            sac_date = st.date_input(
                "Sac Date",
                format = "YYYY-MM-DD",
            )
    
    with col2:
        notes = st.text_area(
            "Notes",
            placeholder = "Optional notes about mice",
            height = "stretch"
        )

    st.divider()
    breeding_cage_submit = st.button("Submit to Redcap",key="breeding_cage",type = "primary")

    if breeding_cage_submit:
        with status_container:
            if not cage_number:
                errors.append("Breeding cage number is required.")
            if errors:
                st.write("Please fix the following issues:")
                for error in errors:
                    st.error(f"{error}")
            if not errors:
                fields = {
                    "mouse_sac_date": sac_date.strftime("%Y-%m-%d"),
                    "mouse_sac_notes": notes,
                    "mouse_info_complete": "2"
                    }
                redcap_utils.create_new_mouse_record(sire_id,fields)
                redcap_utils.create_new_mouse_record(dame_id,fields)

                st.session_state["sac"] = pd.DataFrame([])

                st.info("Returning you to Breeding Dashboard")
                time.sleep(2)
                st.session_state["redcap_df"] = redcap_utils.load_records()
                st.switch_page("pages/breeding_cages.py")

# --------------------------------------------------
# Sac Single Cage
# --------------------------------------------------

single_cage_submit = False
sac_df = []
cage_number = ""

if sac_type == "Single Cage":

    col1, col2 = st.columns(2)

    with col1:
        cola, colb = st.columns([1,0.1],vertical_alignment = "center")
        with cola:
            cage_number = st.text_input(
                "Cage Number",
            )
        with colb:
            sac_df = df[df["mouse_cage_number"] == cage_number]
            sac_df = sac_df[sac_df["mouse_transfer"] == ""]
            sac_df = sac_df[sac_df["mouse_sac_date"] == ""]
            mice = sac_df["mouse_id"]
            if mice.empty or cage_number == "":
                st.markdown("")
                st.caption(":red[:material/error:]")
                errors.append("Cage number not found")
            else:
                st.markdown("")
                st.caption(":green[:material/check_circle:]")

        cola, colb = st.columns([1,0.1],vertical_alignment = "center")
        with cola:
            sac_date = st.date_input(
                "Sac Date",
                format = "YYYY-MM-DD",
            )
    
    with col2:
        notes = st.text_area(
            "Notes",
            placeholder = "Optional notes about mice",
            height = "stretch"
        )

    st.divider()
    single_cage_submit = st.button("Submit to Redcap", type="primary")

    if single_cage_submit:
        with status_container:
            errors = []
            if not cage_number:
                errors.append("Cage Number is required.")
            if errors:
                st.write("Please fix the following issues:")
                for error in errors:
                    st.error(f"- {error}")

            if not errors:
                fields = {
                    "mouse_sac_date": sac_date.strftime("%Y-%m-%d"),
                    "mouse_sac_notes": notes,
                    "mouse_info_complete": "2"
                    }

                for mouse_id in mice:
                    mouse_id_str = str(mouse_id).strip()
                    redcap_utils.create_new_mouse_record(mouse_id_str,fields)
                    st.success(f"Mouse: {mouse_id_str} sac date has been updated")
                    
                st.info("Returning you to Dashboard")
                time.sleep(2)
                st.session_state["redcap_df"] = redcap_utils.load_records()
                st.switch_page("pages/dashboard.py")

# --------------------------------------------------
# Sac Multiple Cages Form
# --------------------------------------------------

single_cage_submit = False
cage_ids = []
sac_df = []

if sac_type == "Multiple Cages":

    col1,col2 = st.columns(2)

    with col1:
        cage_number = st.number_input(
            "Number of Cages Sacced",
            value = 0,
        )

        sac_date = st.date_input(
            "Sac Date",
            format = "YYYY-MM-DD",
        )
    
        notes = st.text_area(
            "Notes",
            placeholder = "Optional notes about mice",
            height = "stretch",
        )

    with col2:
        for i in range(cage_number):
            cola, colb = st.columns([1,0.1],vertical_alignment = "center")
            with cola:
                cage_number = st.text_input(
                    f"Cage {i+1} Number",
                )
            check_df = df[df["mouse_cage_number"] == cage_number]
            check_df = check_df[check_df["mouse_transfer"] == ""]
            check_df = check_df[check_df["mouse_sac_date"] == ""]
            with colb:
                if check_df.empty or cage_number == "":
                    st.markdown("")
                    st.caption(":red[:material/error:]")
                    errors.append("Cage number not found")
                else:
                    st.markdown("")
                    st.caption(":green[:material/check_circle:]")

    cage_ids.append(cage_number)
    sac_df = df[df["mouse_cage_number"].isin(cage_ids)]
    sac_df = sac_df[sac_df["mouse_transfer"] == ""]
    sac_df = sac_df[sac_df["mouse_sac_date"] == ""]
    mice = sac_df["mouse_id"]
    st.divider()

    multi_cage_submit = st.button("Submit to Redcap", type="primary")

    if multi_cage_submit:

        with status_container:
            errors = []
            for i in range(len(cage_ids)):
                cage_number = cage_ids[i]
                if not cage_number:
                    errors.append(f"Cage Number {i+1} is required.")

            if errors:
                st.write("Please fix the following issues:")

                for error in errors:
                    st.error(f"{error}")

            if not errors:
                fields = {
                    "mouse_sac_date": sac_date.strftime("%Y-%m-%d"),
                    "mouse_sac_notes": notes,
                    "mouse_info_complete": "2"
                    }
                
                for mouse_id in mice:
                    mouse_id_str = str(mouse_id).strip()
                    redcap_utils.create_new_mouse_record(mouse_id_str,fields)
                    st.success(f"Mouse: {mouse_id_str} sac date has been updated")
                    
                st.info("Returning you to Dashboard")

                time.sleep(2)
                st.session_state["redcap_df"] = redcap_utils.load_records()
                st.switch_page("pages/dashboard.py")

# --------------------------------------------------
# Sac Individual Mouse Form
# --------------------------------------------------

if sac_type == "Individual Mouse":

    col1, col2 = st.columns(2)

    with col1:
        cola, colb = st.columns([1,0.1], vertical_alignment = "center")
        with cola:
            mouse_name = st.text_input(
                "Mouse ID",
            )
        with colb:
            st.caption("")
            mouse_id = redcap_utils.find_id_from_sample(mouse_name)
            if mouse_id != None:
                st.caption(":green[:material/check_circle:]")
            else:
                st.caption(":red[:material/error:]")
                errors.append("Mouse ID not found")

        
        cola, colb = st.columns([1,0.1], vertical_alignment = "center")
        with cola:
            sac_date = st.date_input(
                "Sac Date",
                format = "YYYY-MM-DD",
            )

    with col2:
        notes = st.text_area(
            "Notes",
            placeholder = "Optional notes about mouse",
            height = "stretch",
        )

    st.divider()

    single_mouse_submit = st.button("Submit to Redcap", type = "primary")

    if single_mouse_submit:

        with status_container:

            errors = []

            if not mouse_id:
                errors.append("Mouse ID is required.")

            if errors:
                st.write("Please fix the following issues:")

                for error in errors:
                    st.error(f"{error}")

            if not errors:

                fields = {
                    "mouse_sac_date": sac_date.strftime("%Y-%m-%d"),
                    "mouse_sac_notes": notes,
                    "mouse_info_complete": "2"
                    }
                
                redcap_utils.create_new_mouse_record(mouse_id,fields)
                st.success(f"Mouse: {mouse_name} sac date has been updated")
                
                st.info("Returning you to Dashboard")

                time.sleep(2)
                st.session_state["redcap_df"] = redcap_utils.load_records()
                st.switch_page("pages/dashboard.py")

# --------------------------------------------------
# Sac Multiple Mice Form
# --------------------------------------------------

if sac_type == "Multiple Mice":

    mouse_ids = []

    if sac_type_input == "Multiple Mice":
        mouse_names = st.session_state["mice_request"].copy()
        number_of_mice = len(mouse_names)
    else:
        number_of_mice = 1
        mouse_names = []

    col1,col2 = st.columns(2)

    with col1:
        mouse_number = st.number_input(
            "Number of Mice Sacced",
            value = number_of_mice,
        )

        sac_date = st.date_input(
            "Sac Date",
            format = "YYYY-MM-DD",
        )
    
        notes = st.text_area(
            "Notes",
            placeholder = "Optional notes about mice",
            height = "stretch",
        )

    with col2:
        if mouse_names == []:
            for i in range(mouse_number):
                cola, colb = st.columns([1,0.1], vertical_alignment = "center")
                with cola:
                    mouse_name = st.text_input(
                        f"Mouse Number {i+1}",
                    )
                with colb:
                    st.caption("")
                    mouse_id = redcap_utils.find_id_from_sample(mouse_name)
                    if mouse_id != None:
                        st.caption(":green[:material/check_circle:]")
                    else:
                        st.caption(":red[:material/error:]")
                mouse_ids.append(mouse_id)
        else:
            for i in range(mouse_number):
                mouse_id = st.text_input(
                    f"Mouse Number {i+1}",
                    value = mouse_names[i]
                )
                mouse_ids.append(mouse_id)

    st.divider()
    multiple_mice_submit = st.button("Submit to Redcap", type="primary")

    if multiple_mice_submit:
        with status_container:

            errors = []

            if not sac_date:
                errors.append("Breeding Cage Number is required.")

            if errors:
                st.write("Please fix the following issues:")

                for error in errors:
                    st.error(f"{error}")

            if not errors:

                fields = {
                    "mouse_sac_date": sac_date.strftime("%Y-%m-%d"),
                    "mouse_sac_notes": notes,
                    "mouse_info_complete": "2"
                    }
                
                for i in range(number_of_mice):
                    redcap_utils.create_new_mouse_record(mouse_ids[i], fields)
                    st.success(f"Mouse: {mouse_ids[i]} sac date has been updated")
                
                st.session_state["sac"] = pd.DataFrame([])
                st.info("Returning you to Mouse Search")
                time.sleep(2)
                st.session_state["redcap_df"] = redcap_utils.load_records()
                st.switch_page("pages/search_mice.py")