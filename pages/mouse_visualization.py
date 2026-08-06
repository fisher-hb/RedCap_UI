from numpy.strings import index
import streamlit as st
import pandas as pd
from datetime import date
import redcap_utils

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Mouse Information
# --------------------------------------------------

view_type = st.session_state["view_type"]
df = st.session_state["redcap_df"]

if view_type == "view":
    disable = True
    st.subheader("View Mice")
    st.markdown("")
else:
    disable = False
    st.subheader("Edit Mice")
    st.markdown("")

mouse_names = st.session_state["mice_request"].copy()

# --------------------------------------------------
# Create Expanders
# --------------------------------------------------

for i in range(len(mouse_names)):
    mouse_df = df[(df["mouse_id"] == mouse_names[i])]
    litter_df = mouse_df[(mouse_df["redcap_repeat_instrument"] == "litter_information")]
    expander = st.expander(
        f"{mouse_df["mouse_id"].iloc[0]}",
    )

    with expander:
        st.markdown("")
        col1, col2 = st.columns([3.2,1])
        with col1:
            st.markdown(f":primary-background[**Mouse ID -- {mouse_df["mouse_id"].iloc[0]}**]")
        with col2:
            if disable == True:
                edit_button = st.button(
                    ":material/edit: Edit Mouse Info",
                    key = f"edit_button_{i}",
                    type = "tertiary",
                )
                if edit_button == True:
                    disable = False
                    st.session_state["view_type"] = "edit"
                    st.rerun()

        if disable == True and mouse_df["breeding_cage"].iloc[0]=="":
            tab_names = ["Mouse Information", "Flags"]
        else:
            tab_names = ["Mouse Information", "Breeding Information", "Litter Information", "Flags"]

        tabs = st.tabs(
            tab_names,
            key = f"tabs_{i}",
            width="stretch",
            on_change="rerun")
        
        # --------------------------------------------------
        # Interpret Non-String Mouse Data
        # --------------------------------------------------

        # Sex
        sex = 0 if mouse_df["mouse_sex"].iloc[0]=="male" else 1
        
        # ID Type
        if mouse_df["mouse_ear_id_type"].iloc[0]=="tag":
            ear_id = 0
        elif mouse_df["mouse_ear_id_type"].iloc[0]=="punch":
            ear_id = 1
        else:
            ear_id = 2

        # Request Flag
        if mouse_df["request_flag"].iloc[0]=="available":
            mouse_flag = 0
        elif mouse_df["request_flag"].iloc[0]=="breeding":
            mouse_flag = 1
        elif mouse_df["request_flag"].iloc[0]=="reserved":
            mouse_flag = 2
        else:
            mouse_flag = None

        # Ear ID Location
        location_to_id = ({
            "r"  :  0,  "l"  :  1,  "b"  :  2, 
            "fr" :  3,  "fl" :  4,  "frt":  5,  "fn" :  6,
            "fry":  7,  "fly":  8,  "fny":  9,  "fd" : 10, 
            "mn" : 11,  "mr" : 12,  "ml" : 13,  "mrt": 14,  "md" : 15
        })
        id_location_index = location_to_id.get(mouse_df["mouse_ear_id_location"].iloc[0])

        # Genotype Label
        genotype_label = redcap_utils.genotype_variable_to_label(mouse_df["mouse_genotype"].iloc[0])

        # --------------------------------------------------
        # Mouse Information
        # --------------------------------------------------
        if tabs[0].open:

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
                        index = sex,
                        horizontal = True,
                        disabled = disable,
                    )
                with colb:
                    mouse_cage_number = st.text_input(
                        "Cage Number",
                        key = f"mouse_cage_number{i}",
                        disabled = disable,
                        value = mouse_df["mouse_cage_number"].iloc[0]
                    )
                with colc:
                    mouse_protocol = st.text_input(
                        "Protocol Year",
                        key = f"mouse_protocol{i}",
                        disabled = disable,
                        value = mouse_df["mouse_protocol"].iloc[0],
                    )

                # Tag/Punch Information
                # st.divider()
                cola, colb, colc = st.columns([1,1,0.6])
                with cola:
                    mouse_ear_id = st.selectbox(
                        "Ear ID",
                        key = f"mouse_ear_id{i}",
                        options = ["Ear Tag","Ear Punch", "None"],
                        index = ear_id,
                        disabled = disable,
                    )
                with colb:
                    if mouse_ear_id == "Ear Tag": 
                        mouse_tag_number = st.text_input(
                            "Tag Number",
                            key = f"mouse_tag_number{i}",
                            disabled = disable,
                            value = str(((mouse_df["mouse_id"].iloc[0]).split(":"))[1])
                        )
                    if mouse_ear_id == "Ear Punch":
                        mouse_id_location = st.selectbox(
                            "ID Location",
                            key = f"mouse_id_location{i}",
                            options = ["R","L","B","FR","FL","FRT","FN","FRY","FLY","FNY","FD","MN","MR","ML","MRT","MD","MLT"],
                            index = id_location_index,
                            disabled = disable,
                        )
                with colc:
                    if mouse_ear_id == "Ear Tag": 
                        mouse_id_location = st.selectbox(
                            "ID Location",
                            key = f"mouse_id_location{i}",
                            options = ["R","L"],
                            index = id_location_index,
                            disabled = disable,
                        )

                # Age information
                # st.divider()
                cola, colb, colc, cold = st.columns(4)
                with cola:
                    mouse_dob = st.date_input(
                        "Date of Birth",
                        key = f"mouse_dob{i}",
                        disabled = disable,
                        value = mouse_df["mouse_dob"].iloc[0]
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
                    value = mouse_df["mouse_notes"].iloc[0]
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
                        value = genotype_label
                    )
                with colb:
                    mouse_source = st.text_input(
                        "Source",
                        key = f"mouse_source{i}",
                        disabled = disable,
                        value = mouse_df["mouse_source"].iloc[0]
                    )
                with colc:
                    mouse_arrival_date = st.date_input(
                        "Wean/Arrival Date",
                        key = f"mouse_arrival_date{i}",
                        disabled = disable,
                        value = None if mouse_df["mouse_arrival_date"].iloc[0]=="" else mouse_df["mouse_arrival_date"].iloc[0]
                    )

                # Parent Information
                # st.divider()
                cola, colb, colc = st.columns([1,2,1])
                with cola:
                    mouse_parental_cage = st.text_input(
                        "Parent Cage",
                        key = f"mouse_parent_cage{i}",
                        disabled = disable,
                        value = mouse_df["mouse_parental_cage"].iloc[0]
                    )
                with colb:
                    mouse_parental_cross = st.text_input(
                        "Parental Cross",
                        key = f"mouse_parental_cross{i}",
                        disabled = disable,
                        value = mouse_df["mouse_parental_cross"].iloc[0]
                    )
                with colc:
                    mouse_litter_id = st.text_input(
                        "Litter ID",
                        key = f"mouse_litter_id{i}",
                        disabled = disable,
                        value = mouse_df["mouse_litter_id"].iloc[0]
                    )

                # Genotyping Information
                # st.divider()
                cola, colb, colc = st.columns([0.7,1,1])
                with cola:
                    mouse_genotyping_performed = st.radio(
                        "Genotyping Performed?",
                        key = f"mouse_genotyping{i}",
                        options = ["No","Yes"],  
                        horizontal = True,
                        disabled = disable,
                        index = int(mouse_df["mouse_genotyping"].iloc[0])
                    )
                if mouse_genotyping_performed == "Yes":
                    with colb:
                        mouse_genotyping_date = st.date_input(
                            "Genotyping Date",
                            key = f"mouse_genotyping_date{i}",
                            disabled = disable,
                            value = None if mouse_df["mouse_genotyping_date"].iloc[0]=="" else mouse_df["mouse_genotyping_date"].iloc[0]
                        )
                    with colc:
                        mouse_wellplate_number = st.text_input(
                            "Wellplate Number",
                            key = f"mouse_wellplate_number{i}",
                            disabled = disable,
                            value = mouse_df["mouse_wellplate_number"].iloc[0]
                        )
                    # st.divider()
                    mouse_genotype_notes = st.text_area(
                        "Genotyping Notes",
                        key = f"mouse_genotyping_notes{i}",
                        disabled = disable,
                        value = mouse_df["mouse_genotype_notes"].iloc[0]
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
                        index = 1 if mouse_df["mouse_transfer"].iloc[0]=="" else int(mouse_df["mouse_transfer"].iloc[0])
                    )
                if mouse_transfer == "Yes":
                    with colb:
                        mouse_transfer_notes = st.text_input(
                            "Transfer Notes",
                            key = f"mouse_transfer_notes{i}",
                            disabled = disable,
                            value = mouse_df["mouse_transfer_notes"].iloc[0]
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
                        index = 1 if mouse_df["mouse_sac_date"].iloc[0]=="" else 0
                    )
                if mouse_sac == "Yes":
                    with colb:
                        mouse_sac_date = st.date_input(
                            "Mouse Sac Date",
                            key = f"mouse_sac_date{i}",
                            disabled = disable,
                            value = None if mouse_df["mouse_sac_date"].iloc[0]=="" else mouse_df["mouse_sac_date"].iloc[0]
                        )
                    with colc:
                        mouse_sac_notes = st.text_input(
                            "Sac Notes",
                            key = f"mouse_sac_notes{i}",
                            disabled = disable,
                            value = mouse_df["mouse_sac_notes"].iloc[0]
                        )
                st.divider()

        if (tab_names == ["Mouse Information", "Breeding Information", "Litter Information", "Flags"] and tabs[3].open) or (tab_names == ["Mouse Information", "Flags"] and tabs[1].open):
            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**Reservation Information**")

            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                # Flag Information
                flag = st.radio(
                    "Flag",
                    key = f"mouse_flag{i}",
                    options = ["Available","Breeding","Reserved"],
                    horizontal = True,
                    disabled = disable,
                    index = mouse_flag,
                    label_visibility = "collapsed",
                )
                cola, colb = st.columns(2)
                with cola:
                    requestor = st.text_input(
                        "Requestor",
                        key = f"requestor{i}",
                        disabled = disable,
                        value = mouse_df["requestor"].iloc[0]
                    )
                    request_date = st.date_input(
                        "Request Date",
                        key = f"request_date{i}",
                        disabled = disable,
                        value = None if mouse_df["request_date"].iloc[0]=="" else mouse_df["request_date"].iloc[0]
                    )
                with colb:
                    request_notes = st.text_area(
                        "Request Notes",
                        key = f"request_notes{i}",
                        disabled = disable,
                        height = "stretch",
                        value = mouse_df["request_notes"].iloc[0],
                    )
                st.divider()

            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**Experiment Information**")

            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                # Experiment Information
                cola, colb = st.columns(2)
                with cola:
                    experiment = st.text_input(
                        "Planned Experiments",
                        key = f"planned_experiment{i}",
                        disabled = disable,
                        value = mouse_df["experiment"].iloc[0],
                    )
                    experiment_date = st.date_input(
                        "Planned Experiment Date",
                        key = f"experiment_date{i}",
                        disabled = disable,
                        value = None if mouse_df["experiment_date"].iloc[0]=="" else mouse_df["experiment_date"].iloc[0]
                    )
                with colb:
                    experiment_notes = st.text_area(
                        "Experiment Notes",
                        key = f"experiment_notes{i}",
                        disabled = disable,
                        height = "stretch",
                        value = mouse_df["experiment_notes"].iloc[0],
                    )
                st.divider()

        if (mouse_df["breeding_cage"].iloc[0] != "" or disable==False) and tabs[1].open:
            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**Breeding Information**")

            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                # Breeding Information
                cola, colb, colc = st.columns([1,1,1.8])
                with cola:
                    breeding_cage = st.text_input(
                        "Breeding Cage Number",
                        key = f"breeding_cage{i}",
                        disabled = disable,
                        value = mouse_df["breeding_cage"].iloc[0],
                    )
                    breeding_date_created = st.date_input(
                        "Date Created",
                        key = f"breeding_date_created{i}",
                        disabled = disable,
                        value = None if mouse_df["breeding_date_created"].iloc[0]=="" else mouse_df["breeding_date_created"].iloc[0]
                    )
                with colb:
                    breeding_partner = st.text_input(
                        "Breeding Partner",
                        key = f"breeding_partner{i}",
                        disabled = disable,
                        value = mouse_df["breeding_partner"].iloc[0],
                    )
                    breeding_separated_date = st.date_input(
                        "Date Separated (Optional)",
                        key = f"breeding_separated_date{i}",
                        disabled = disable,
                        value = None if mouse_df["breeding_separated_date"].iloc[0]=="" else mouse_df["breeding_separated_date"].iloc[0]
                    )
                with colc:
                    breeding_notes = st.text_area(
                        "Breeding Notes",
                        key = f"breeding_notes{i}",
                        disabled = disable,
                        height = "stretch",
                        value = mouse_df["breeding_notes"].iloc[0],
                    )
                st.divider()

        if (mouse_df["breeding_cage"].iloc[0] != "" or disable==False) and tabs[2].open:
            if len(litter_df) == 0:
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown("**Litter Information**")
                    col1, col2, col3 = st.columns([0.2,2,0.2])
                    with col2:
                        st.markdown(f":small[No litter information is available for this mouse.]")
                    st.divider()
            
            for i in range(len(litter_df)):
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown(f":primary-background[**Litter: {litter_df["litter_id"].iloc[i]}**]")

                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    st.markdown(f":small[**Litter Information**]")
                    cola, colb, colc = st.columns(3)
                    with cola:
                        litter_dob = st.date_input(
                            "Date of Birth",
                            key = f"litter_dob{i}",
                            disabled = disable,
                            value = None if litter_df["litter_dob"].iloc[i]=="" else litter_df["litter_dob"].iloc[i]
                        )
                    with colb:
                        litter_date_to_wean = st.date_input(
                            "Calculated Weaning Date",
                            key = f"litter_date_to_wean{i}",
                            disabled = True,
                            value = litter_df["litter_date_to_wean"].iloc[i]
                        )
                    with colc:
                        litter_wean_date = st.date_input(
                            "Actual Weaning Date",
                            key = f"litter_wean_date{i}",
                            disabled = disable,
                            value = None if litter_df["litter_wean_date"].iloc[i]=="" else litter_df["litter_wean_date"].iloc[i]
                        )
                    litter_notes_new = st.text_input(
                        "New Litter Notes",
                        key = f"litter_notes_new{i}",
                        disabled = disable,
                        value = litter_df["litter_notes_new"].iloc[i],
                    )
                    st.markdown(f":small[**Weaning Information**]")
                    cola, colb, colc = st.columns([1,1,2])
                    with cola:
                        litter_wean_num_m = st.text_input(
                            "Male Pups Weaned",
                            key = f"litter_wean_num_m{i}",
                            disabled = disable,
                            value = litter_df["litter_wean_num_m"].iloc[i]
                        )
                        litter_sac_num_m = st.text_input(
                            "Male Pups Sacced",
                            key = f"litter_sac_num_m{i}",
                            disabled = disable,
                            value = litter_df["litter_sac_num_m"].iloc[i]
                        )
                    with colb:
                        litter_wean_num_f = st.text_input(
                            "Female Pups Weaned",
                            key = f"litter_wean_num_f{i}",
                            disabled = disable,
                            value = litter_df["litter_wean_num_f"].iloc[i]
                        )
                        litter_sac_num_f = st.text_input(
                            "Female Pups Sacced",
                            key = f"litter_sac_num_f{i}",
                            disabled = disable,
                            value = litter_df["litter_sac_num_f"].iloc[i]
                        )
                    with colc:
                        litter_notes_wean = st.text_area(
                            "Weaning Notes",
                            key = f"litter_notes_wean{i}",
                            disabled = disable,
                            height = "stretch",
                            value = litter_df["litter_notes_wean"].iloc[i],
                        )
                    if litter_df["litter_reserver"].iloc[i]!="":
                        st.markdown(f":small[**Reservation Information**]")
                        cola, colb = st.columns([1,2])
                        with cola:
                            litter_reserver = st.text_input(
                                "Reserved By",
                                key = f"litter_reserver{i}",
                                disabled = disable,
                                value = litter_df["litter_reserver"].iloc[i],
                            )

                            if litter_df["litter_reservation"].iloc[i]=="development":
                                litter_flag = 0
                            elif litter_df["litter_reservation"].iloc[i]=="breeding":
                                litter_flag = 1
                            else:
                                litter_flag = None

                            litter_reservation = st.selectbox(
                                "Reservation Type",
                                key = f"litter_reservation{i}",
                                options = ["Development","Breeding"],
                                disabled = disable,
                                index = litter_flag,
                            )
                            litter_reservation_date = st.date_input(
                                "Reservation Date",
                                key = f"litter_reservation_date{i}",
                                disabled = disable,
                                value = None if litter_df["litter_reservation_date"].iloc[i]=="" else litter_df["litter_reservation_date"].iloc[i]
                            )
                        with colb:
                            litter_notes_reserve = st.text_area(
                                "Weaning Notes",
                                key = f"litter_notes_reserve{i}",
                                disabled = disable,
                                height = "stretch",
                                value = litter_df["litter_notes_reserve"].iloc[i],
                            )
                    st.divider()

        col1, col2 = st.columns([0.1,2.3])
        with col2:
            if disable == False:
                update_button = st.button(
                    "Update Mouse Information",
                    key = f"update_mouse_info{i}",
                    type = "primary"
                )

                if update_button == True:
                    print("update mouse information")

            