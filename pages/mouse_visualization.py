from numpy.strings import index
import streamlit as st
from datetime import date
import redcap_utils
import time

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Mouse Information
# --------------------------------------------------

view_type = st.session_state.get("view_type", "view")
mouse_names = st.session_state["mice_request"]
df = st.session_state["redcap_df"]

if view_type == "view":
    disable = True
    st.subheader("View Mice")
else:
    disable = False
    st.subheader("Edit Mice")

st.markdown("")

if "mouse_editor_initialized" not in st.session_state or st.session_state["mouse_editor_initialized"] == False:
    for i in range(len(mouse_names)):
        redcap_utils.assign_session_data(mouse_names[i], i)
        st.session_state["mouse_editor_initialized"] = True

# --------------------------------------------------
# Create Expanders
# --------------------------------------------------

for i in range(len(mouse_names)):
    mouse_df = df[df["mouse_id"] == mouse_names[i]]
    info_df = mouse_df[mouse_df["redcap_repeat_instrument"] == ""]
    litters_df = mouse_df[mouse_df["redcap_repeat_instrument"] == "litter_information"]
    experiments_df = mouse_df[mouse_df["redcap_repeat_instrument"] == "experiment_information"]

    with st.expander(f"{mouse_names[i]}", expanded=(i == 0)):
        st.markdown("")
        col1, col2 = st.columns([3.2, 1],vertical_alignment="center")
        with col1:
            st.markdown(f":primary-background[**Mouse ID -- {mouse_names[i]}**]")
        with col2:
            if disable:
                edit_button = st.button(
                    ":material/edit: Edit Mouse Info",
                    key=f"edit_button_{i}",
                    type="tertiary",
                )
                if edit_button:
                    st.session_state["view_type"] = "edit"
                    redcap_utils.assign_session_data(mouse_names[i], i)
                    st.rerun()
            else:
                clear_button = st.button(
                    ":material/ink_eraser: Clear Edits",
                    key=f"clear_button_{i}",
                    type="tertiary",
                )
                if clear_button:
                    redcap_utils.assign_session_data(mouse_names[i], i)
                    st.rerun()
        
        tab_names = [
            "Mouse Information",
            "Breeding Information",
            "Litter Information",
            "Experiment Information",
            "Reservation",
        ]
        tabs = st.tabs(tab_names)

        # --------------------------------------------------
        # Mouse Information Tab
        # --------------------------------------------------
        with tabs[0]:
            st.markdown("")
            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**Basic Information**")
            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                # General Information
                cola, colb, colc = st.columns([0.7,1,1])
                with cola:
                    mouse_sex = st.radio(
                        "Sex",
                        key = f"mouse_sex{i}",
                        options = ["Male","Female"],
                        horizontal = True,
                        disabled = disable,
                    )
                with colb:
                    mouse_cage_number = st.text_input(
                        "Cage Number",
                        key = f"mouse_cage_number{i}",
                        disabled = disable,
                    )
                with colc:
                    mouse_protocol = st.text_input(
                        "Protocol Year",
                        key = f"mouse_protocol{i}",
                        disabled = disable,
                    )
                # Tag/Punch Information
                cola, colb, colc = st.columns([1,1,0.6])
                with cola:
                    mouse_ear_id = st.selectbox(
                        "Ear ID Type",
                        key = f"mouse_ear_id_type{i}",
                        options = ["Tag","Punch", "None"],
                        disabled = disable,
                    )
                with colb:
                    if mouse_ear_id == "Tag": 
                        mouse_tag_number = st.text_input(
                            "Tag Number",
                            key = f"mouse_ear_id{i}",
                            disabled = disable,
                            value = info_df["mouse_ear_id"].iloc[0]
                        )
                    if mouse_ear_id == "Punch":
                        mouse_id_location = st.selectbox(
                            "ID Location",
                            key = f"mouse_ear_id_location{i}",
                            options = ["R","L","B","FR","FL","FRT","FN","FRY","FLY","FNY","FD","MN","MR","ML","MRT","MD","MLT"],
                            disabled = disable,
                        )
                with colc:
                    if mouse_ear_id == "Tag":
                        mouse_id_location = st.selectbox(
                            "ID Location",
                            key = f"mouse_ear_id_location{i}",
                            options = ["R","L"],
                            disabled = disable,
                        )
                # Age information
                cola, colb, colc, cold = st.columns(4)
                with cola:
                    mouse_dob = st.date_input(
                        "Date of Birth",
                        key = f"mouse_dob{i}",
                        disabled = disable,
                    )
                days = (date.today() - mouse_dob).days
                weeks = days / 7
                months = days / (365.2425 / 12)
                with colb:
                    mouse_age_days = st.text_input(
                        "Age (Days)",
                        key = f"mouse_age_days{i}",
                        disabled = True,
                        value = days,
                    )
                with colc:
                    mouse_age_weeks = st.text_input(
                        "Age (Weeks)",
                        key = f"mouse_age_weeks{i}",
                        disabled = True,
                        value = f"{weeks:.2f}"
                    )
                with cold:
                    mouse_age_months = st.text_input(
                        "Age (Months)",
                        key = f"mouse_age_months{i}",
                        disabled = True,
                        value = f"{months:.2f}"
                    )
                mouse_notes = st.text_area(
                    "General Notes",
                    key = f"mouse_notes{i}",
                    disabled = disable,
                )
                st.divider()
            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**Genotype Information**")
            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                # Genotype Information
                cola, colb, colc = st.columns([2,1,1])
                with cola:
                    mouse_genotype = st.text_input(
                        "Genotype",
                        key = f"mouse_genotype{i}",
                        disabled = disable,
                    )
                with colb:
                    mouse_source = st.text_input(
                        "Source",
                        key = f"mouse_source{i}",
                        disabled = disable,
                    )
                with colc:
                    mouse_arrival_date = st.date_input(
                        "Wean/Arrival Date",
                        key = f"mouse_arrival_date{i}",
                        disabled = disable,
                    )
                # Parent Information
                cola, colb, colc = st.columns([1,2,1])
                with cola:
                    mouse_parental_cage = st.text_input(
                        "Parent Cage",
                        key = f"mouse_parental_cage{i}",
                        disabled = disable,
                    )
                with colb:
                    mouse_parental_cross = st.text_input(
                        "Parental Cross",
                        key = f"mouse_parental_cross{i}",
                        disabled = disable,
                    )
                with colc:
                    mouse_litter_id = st.text_input(
                        "Litter ID",
                        key = f"mouse_litter_id{i}",
                        disabled = disable,
                    )
                # Genotyping Information
                cola, colb, colc = st.columns([0.7,1,1])
                with cola:
                    mouse_genotyping = st.radio(
                        "Genotyping Performed?",
                        key = f"mouse_genotyping{i}",
                        options = ["Yes","No"],  
                        horizontal = True,
                        disabled = disable,
                    )
                if mouse_genotyping == "Yes":
                    with colb:
                        mouse_genotyping_date = st.date_input(
                            "Genotyping Date",
                            key = f"mouse_genotyping_date{i}",
                            disabled = disable,
                            value = info_df["mouse_genotyping_date"].iloc[0] if info_df["mouse_genotyping_date"].iloc[0] != "" else None
                        )
                    with colc:
                        mouse_wellplate_number = st.text_input(
                            "Wellplate Number",
                            key = f"mouse_wellplate_number{i}",
                            disabled = disable,
                            value = info_df["mouse_wellplate_number"].iloc[0]
                        )
                    mouse_genotype_notes = st.text_area(
                        "Genotyping Notes",
                        key = f"mouse_genotype_notes{i}",
                        disabled = disable,
                        value = info_df["mouse_genotype_notes"].iloc[0]
                    )
                st.divider()
            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**Transfer Information**")
            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                # Transfer Information
                cola, colb = st.columns([1,4])
                with cola:
                    mouse_transfer = st.radio(
                        "Mouse Transferred?",
                        key = f"mouse_transfer{i}",
                        options = ["Yes", "No"],
                        horizontal = True,
                        disabled = disable,
                    )
                if mouse_transfer == "Yes":
                    with colb:
                        mouse_transfer_notes = st.text_input(
                            "Transfer Notes",
                            key = f"mouse_transfer_notes{i}",
                            disabled = disable,
                            value = info_df["mouse_transfer_notes"].iloc[0]
                        )
                st.divider()
            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**Sac Information**")
            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                # Sac Information
                cola, colb, colc = st.columns([1,1,3])
                with cola:
                    mouse_sac = st.radio(
                        "Mouse Sacced?",
                        key = f"mouse_sacced{i}",
                        options = ["Yes", "No"],
                        horizontal = True,
                        disabled = disable,
                    )
                if mouse_sac == "Yes":
                    with colb:
                        mouse_sac_date = st.date_input(
                            "Mouse Sac Date",
                            key = f"mouse_sac_date{i}",
                            disabled = disable,
                            value = info_df["mouse_sac_date"].iloc[0] if info_df["mouse_sac_date"].iloc[0] != "" else None
                        )
                    with colc:
                        mouse_sac_notes = st.text_input(
                            "Sac Notes",
                            key = f"mouse_sac_notes{i}",
                            disabled = disable,
                        )
            if disable == False:               
                st.divider()

        with tabs[4]:
            st.markdown("")
            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**Reservation Information**")
            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                # Flag Information
                request_flag = st.radio(
                    "Flag",
                    key = f"request_flag{i}",
                    options = ["Available","Breeding","Reserved","Plan to Sac"],
                    horizontal = True,
                    disabled = disable,
                    label_visibility = "collapsed",
                )
                if request_flag == "Reserved" or request_flag == "Breeding" or request_flag == "Plan to Sac":
                    cola, colb = st.columns(2)
                    with cola:
                        requestor = st.text_input(
                            "Requestor",
                            key = f"request_person{i}",
                            disabled = disable,
                            value = info_df["request_person"].iloc[0]
                        )
                        request_date = st.date_input(
                            "Request Date",
                            key = f"request_date{i}",
                            disabled = disable,
                            value = info_df["request_date"].iloc[0] if info_df["request_date"].iloc[0] != "" else None
                        )
                    with colb:
                        request_notes = st.text_area(
                            "Request Notes",
                            key = f"request_notes{i}",
                            disabled = disable,
                            height = "stretch",
                            value = info_df["request_notes"].iloc[0]
                        )
            if request_flag == "Reserved":
                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    st.divider()
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown(f"**Experiment Information**")
                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    # Experiment Information
                    cola, colb = st.columns(2)
                    with cola:
                        request_experiment = st.text_input(
                            "Planned Experiment",
                            key = f"request_experiment{i}",
                            disabled = disable,
                            value = info_df["request_experiment"].iloc[0]
                        )
                        request_experiment_date = st.date_input(
                            "Planned Experiment Date",
                            key = f"request_experiment_date{i}",
                            disabled = disable,
                            value = info_df["request_experiment_date"].iloc[0] if info_df["request_experiment_date"].iloc[0] != "" else None
                        )
                    with colb:
                        request_experiment_notes = st.text_area(
                            "Experiment Notes",
                            key = f"request_experiment_notes{i}",
                            disabled = disable,
                            height = "stretch",
                            value = info_df["request_experiment_notes"].iloc[0]
                        )
            if disable == False:
                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    st.divider()

        with tabs[1]:
            st.markdown("")
            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**Breeding Information**")
            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                if info_df["breeding_cage"].iloc[0] == "":
                    st.markdown(f":small[No breeding information is available for this mouse.]")
                    breeding = False
                else:
                    breeding = True
                    # Breeding Information
                    cola, colb, colc = st.columns([1,1,1.8])
                    with cola:
                        breeding_cage = st.text_input(
                            "Breeding Cage Number",
                            key = f"breeding_cage{i}",
                            disabled = disable,
                        )
                        breeding_date_created = st.date_input(
                            "Date Created",
                            key = f"breeding_date_created{i}",
                            disabled = disable,
                        )
                    with colb:
                        breeding_partner = st.text_input(
                            "Breeding Partner",
                            key = f"breeding_partner{i}",
                            disabled = disable,
                        )
                        breeding_separated_date = st.date_input(
                            "Date Separated (Optional)",
                            key = f"breeding_separated_date{i}",
                            disabled = disable,
                        )
                    with colc:
                        breeding_notes = st.text_area(
                            "Breeding Notes",
                            key = f"breeding_notes{i}",
                            disabled = disable,
                            height = "stretch",
                        )
                st.divider()

        with tabs[2]:
            st.markdown("")
            if len(litters_df) == 0:
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown("**Litter Information**")
                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    st.markdown(f":small[No litter information is available for this mouse.]")
                    st.divider()
            
            for j in range(len(litters_df)):
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown(f":primary-background[**Litter: {litters_df["litter_id"].iloc[j]}**]")
                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    st.markdown(f":small[**Litter Information**]")
                    cola, colb = st.columns([1,2])
                    with cola:
                        litter_dob = st.date_input(
                            "Date of Birth",
                            key = f"litter_dob{i}{j}",
                            disabled = disable,
                        )
                        litter_wean_date = st.date_input(
                            "Weaning Date",
                            key = f"litter_wean_date{i}{j}",
                            disabled = disable,
                        )
                    with colb:
                        litter_notes_new = st.text_area(
                            "New Litter Notes",
                            key = f"litter_notes_new{i}{j}",
                            disabled = disable,
                            height = "stretch"
                        )
                    st.markdown(f":small[**Weaning Information**]")
                    cola, colb, colc = st.columns([1,1,2])
                    with cola:
                        litter_wean_num_m = st.text_input(
                            "Male Pups Weaned",
                            key = f"litter_wean_num_m{i}{j}",
                            disabled = disable,
                        )
                        litter_sac_num_m = st.text_input(
                            "Male Pups Sacced",
                            key = f"litter_sac_num_m{i}{j}",
                            disabled = disable,
                        )
                    with colb:
                        litter_wean_num_f = st.text_input(
                            "Female Pups Weaned",
                            key = f"litter_wean_num_f{i}{j}",
                            disabled = disable,
                        )
                        litter_sac_num_f = st.text_input(
                            "Female Pups Sacced",
                            key = f"litter_sac_num_f{i}{j}",
                            disabled = disable,
                        )
                    with colc:
                        litter_notes_wean = st.text_area(
                            "Weaning Notes",
                            key = f"litter_notes_wean{i}{j}",
                            disabled = disable,
                            height = "stretch",
                        )
                    if litters_df["litter_reserver"].iloc[j]!="":
                        st.markdown(f":small[**Reservation Information**]")
                        cola, colb = st.columns([1,2])
                        with cola:
                            litter_reserver = st.text_input(
                                "Reserved By",
                                key = f"litter_reserver{i}{j}",
                                disabled = disable,
                            )
                            litter_reservation = st.selectbox(
                                "Reservation Type",
                                key = f"litter_reservation{i}{j}",
                                options = ["Development","Breeding"],
                                disabled = disable,
                            )
                            litter_reservation_date = st.date_input(
                                "Reservation Date",
                                key = f"litter_reservation_date{i}{j}",
                                disabled = disable,
                            )
                        with colb:
                            litter_notes_reserve = st.text_area(
                                "Weaning Notes",
                                key = f"litter_notes_reserve{i}{j}",
                                disabled = disable,
                                height = "stretch",
                            )
                    st.divider()

        with tabs[3]:
            st.markdown("")
            if len(experiments_df) == 0:
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown("**Experiment Information**")
                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    st.markdown(f":small[No experiment information is available for this mouse.]")
                    st.divider()
            
            for j in range(len(experiments_df)):
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown(f"**{experiments_df["experiment_type"].iloc[j].title()} Information**")

                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    cola, colb = st.columns(2)
                    with cola:
                        colc, cold = st.columns([0.45,1],vertical_alignment="center")
                        with colc:
                            st.markdown(f":small[Experiment]")
                        with cold: 
                            st.text_input(
                                "Experiment Type",
                                key = f"experiment_type{i}{j}",
                                label_visibility = "collapsed",
                                disabled = disable,
                            )
    
                        colc, cold = st.columns([0.45,1],vertical_alignment="center")
                        with colc:
                            st.markdown(f":small[Date Performed]")
                        with cold: 
                            st.date_input(
                                "Experiment Date",
                                key = f"experiment_date{i}{j}",
                                label_visibility = "collapsed",
                                disabled = disable
                            )

                        colc, cold = st.columns([0.45,1],vertical_alignment="center")
                        with colc:
                            st.markdown(f":small[Performed By]")
                        with cold: 
                            st.text_input(
                                "Experimentor",
                                key = f"experiment_experimentor{i}{j}",
                                label_visibility = "collapsed",
                                disabled = disable
                            )
                    with colb:
                        st.text_area(
                            "Experiment Notes",
                            key = f"experiment_notes{i}{j}",
                            label_visibility="collapsed",
                            disabled = disable,
                            height = "stretch"
                        )
                    st.divider()
                # UPDATE GLOBAL MOUSE INFORMATION VARIABLE HERE

        col1, col2 = st.columns([0.1,2.3])
        with col2:
            if disable == False:
                update_button = st.button(
                    "Update Mouse Information",
                    key = f"update_mouse_info{i}",
                    type = "primary"
                )

                if update_button == True:
                    redcap_utils.submit_session_data(mouse_names[i],i,breeding,litters_df,experiments_df)
                    time.sleep(2)
                    st.session_state["mouse_editor_initialized"] == False
                    st.session_state["redcap_df"] = redcap_utils.load_records()
                    st.rerun()