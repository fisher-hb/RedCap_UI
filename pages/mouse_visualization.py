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
mouse_names = st.session_state["mice_request"].copy()

tab_type = 0
if view_type == "view":
    disable = True
    st.subheader("View Mice")
    st.markdown("")
else:
    disable = False
    st.subheader("Edit Mice")
    st.markdown("")

if st.session_state["mouse_info"].empty:
    mouse_df = df[df["mouse_id"].isin(mouse_names)].reset_index(drop=True)
    st.session_state["mouse_info_unedited"] = mouse_df
    st.session_state["mouse_info"] = mouse_df

# --------------------------------------------------
# Create Expanders
# --------------------------------------------------

mice_df = st.session_state["mouse_info"].reset_index(drop=True)
local = [mice_df, mice_df]

for i in range(len(mouse_names)):
    df_local = mice_df[(mice_df["mouse_id"] == mouse_names[i])]
    mouse_local = df_local[(df_local["redcap_repeat_instrument"] == "")]
    litters_local = df_local[(df_local["redcap_repeat_instrument"] == "litter_information")]
    experiments_local = df_local[(df_local["redcap_repeat_instrument"] == "experiment_information")]
    local[i] = pd.concat([mouse_local, litters_local, experiments_local], ignore_index=True)

    expander = st.expander(
        f"{mouse_local["mouse_id"].iloc[0]}",
    )
    with expander:
        st.markdown("")
        col1, col2 = st.columns([3.2,1])
        with col1:
            st.markdown(f":primary-background[**Mouse ID -- {mouse_local["mouse_id"].iloc[0]}**]")
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
            else:
                reset_button = st.button(
                    ":material/ink_eraser: Clear Edits",
                    key = f"clear_button_{i}",
                    type = "tertiary",
                )
                if reset_button == True:
                    st.session_state["mouse_info"] = st.session_state["mouse_info_unedited"]
                    st.rerun()

        if disable == True and mouse_local["breeding_cage"].iloc[0]=="" and len(experiments_local) == 0:
            tab_names = ["Mouse Information", "Reservation"]
            tab_type = 1
        elif disable == True and mouse_local["breeding_cage"].iloc[0]=="":
            tab_names = ["Mouse Information", "Experiment Information", "Reservation"]
            tab_type = 2
        elif disable == True and len(experiments_local) == 0:
            tab_names = ["Mouse Information", "Breeding Information", "Litter Information", "Reservation"]
            tab_type = 3
        else:
            tab_names = ["Mouse Information", "Breeding Information", "Litter Information", "Experiment Information", "Reservation"]
            tab_type = 4

        tabs = st.tabs(
            tab_names,
            key = f"tabs_{i}",
            width="stretch",
            on_change="rerun")
        
        # --------------------------------------------------
        # Interpret Non-String Mouse Data
        # --------------------------------------------------

        # Sex
        sex = 0 if mouse_local["mouse_sex"].iloc[0] == "male" else 1
        
        # ID Type
        if mouse_local["mouse_ear_id_type"].iloc[0]=="tag":
            ear_id = 0
        elif mouse_local["mouse_ear_id_type"].iloc[0]=="punch":
            ear_id = 1
        else:
            ear_id = 2

        # Request Flag
        if mouse_local["request_flag"].iloc[0]=="available":
            mouse_flag = 0
        elif mouse_local["request_flag"].iloc[0]=="breeding":
            mouse_flag = 1
        elif mouse_local["request_flag"].iloc[0]=="reserved":
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
        id_location_index = location_to_id.get(mouse_local["mouse_ear_id_location"].iloc[0])

        # Genotype Label
        genotype_label = redcap_utils.genotype_variable_to_label(mouse_local["mouse_genotype"].iloc[0])

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
                        value = mouse_local["mouse_cage_number"].iloc[0]
                    )
                with colc:
                    mouse_protocol = st.text_input(
                        "Protocol Year",
                        key = f"mouse_protocol{i}",
                        disabled = disable,
                        value = mouse_local["mouse_protocol"].iloc[0],
                    )
                # Tag/Punch Information
                cola, colb, colc = st.columns([1,1,0.6])
                with cola:
                    mouse_ear_id = st.selectbox(
                        "Ear ID Type",
                        key = f"mouse_ear_id{i}",
                        options = ["Tag","Punch", "None"],
                        index = ear_id,
                        disabled = disable,
                    )
                with colb:
                    if mouse_ear_id == "Tag": 
                        mouse_tag_number = st.text_input(
                            "Tag Number",
                            key = f"mouse_tag_number{i}",
                            disabled = disable,
                            value = mouse_local["mouse_ear_id"].iloc[0],
                        )
                    if mouse_ear_id == "Punch":
                        mouse_id_location = st.selectbox(
                            "ID Location",
                            key = f"mouse_id_location{i}",
                            options = ["R","L","B","FR","FL","FRT","FN","FRY","FLY","FNY","FD","MN","MR","ML","MRT","MD","MLT"],
                            index = id_location_index,
                            disabled = disable,
                        )
                with colc:
                    if mouse_ear_id == "Tag":
                        mouse_id_location = st.selectbox(
                            "ID Location",
                            key = f"mouse_id_location{i}",
                            options = ["R","L"],
                            index = id_location_index,
                            disabled = disable,
                        )

                # Age information
                cola, colb, colc, cold = st.columns(4)
                with cola:
                    mouse_dob = st.date_input(
                        "Date of Birth",
                        key = f"mouse_dob{i}",
                        disabled = disable,
                        value = mouse_local["mouse_dob"].iloc[0]
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
                    value = mouse_local["mouse_notes"].iloc[0]
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
                    genotype_variable = redcap_utils.genotype_label_to_variable(mouse_genotype)
                with colb:
                    mouse_source = st.text_input(
                        "Source",
                        key = f"mouse_source{i}",
                        disabled = disable,
                        value = mouse_local["mouse_source"].iloc[0].title()
                    )
                with colc:
                    mouse_arrival_date = st.date_input(
                        "Wean/Arrival Date",
                        key = f"mouse_arrival_date{i}",
                        disabled = disable,
                        value = None if mouse_local["mouse_arrival_date"].iloc[0]=="" else mouse_local["mouse_arrival_date"].iloc[0]
                    )

                # Parent Information
                cola, colb, colc = st.columns([1,2,1])
                with cola:
                    mouse_parental_cage = st.text_input(
                        "Parent Cage",
                        key = f"mouse_parent_cage{i}",
                        disabled = disable,
                        value = mouse_local["mouse_parental_cage"].iloc[0]
                    )
                with colb:
                    mouse_parental_cross = st.text_input(
                        "Parental Cross",
                        key = f"mouse_parental_cross{i}",
                        disabled = disable,
                        value = mouse_local["mouse_parental_cross"].iloc[0]
                    )
                with colc:
                    mouse_litter_id = st.text_input(
                        "Litter ID",
                        key = f"mouse_litter_id{i}",
                        disabled = disable,
                        value = mouse_local["mouse_litter_id"].iloc[0]
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
                        index = 1 - int(mouse_local["mouse_genotyping"].iloc[0])
                    )
                if mouse_genotyping == "Yes":
                    with colb:
                        mouse_genotyping_date = st.date_input(
                            "Genotyping Date",
                            key = f"mouse_genotyping_date{i}",
                            disabled = disable,
                            value = None if mouse_local["mouse_genotyping_date"].iloc[0]=="" else mouse_local["mouse_genotyping_date"].iloc[0]
                        )
                    with colc:
                        mouse_wellplate_number = st.text_input(
                            "Wellplate Number",
                            key = f"mouse_wellplate_number{i}",
                            disabled = disable,
                            value = mouse_local["mouse_wellplate_number"].iloc[0]
                        )
                    mouse_genotype_notes = st.text_area(
                        "Genotyping Notes",
                        key = f"mouse_genotyping_notes{i}",
                        disabled = disable,
                        value = mouse_local["mouse_genotype_notes"].iloc[0]
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
                        index = 1 if mouse_local["mouse_transfer"].iloc[0]=="" else 1-int(mouse_local["mouse_transfer"].iloc[0])
                    )
                if mouse_transfer == "Yes":
                    with colb:
                        mouse_transfer_notes = st.text_input(
                            "Transfer Notes",
                            key = f"mouse_transfer_notes{i}",
                            disabled = disable,
                            value = mouse_local["mouse_transfer_notes"].iloc[0]
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
                        index = 1 if mouse_local["mouse_sac_date"].iloc[0]=="" else 0
                    )
                if mouse_sac == "Yes":
                    with colb:
                        mouse_sac_date = st.date_input(
                            "Mouse Sac Date",
                            key = f"mouse_sac_date{i}",
                            disabled = disable,
                            value = None if mouse_local["mouse_sac_date"].iloc[0]=="" else mouse_local["mouse_sac_date"].iloc[0]
                        )
                    with colc:
                        mouse_sac_notes = st.text_input(
                            "Sac Notes",
                            key = f"mouse_sac_notes{i}",
                            disabled = disable,
                            value = mouse_local["mouse_sac_notes"].iloc[0]
                        )
            if disable == False:               
                st.divider()

            fields = {
                "mouse_sex" : mouse_sex.lower(),
                "mouse_cage_number" : mouse_cage_number,
                "mouse_protocol" : mouse_protocol,
                "mouse_ear_id_type" : mouse_ear_id.lower(),
                "mouse_ear_id" : mouse_tag_number if mouse_ear_id == "Tag" else "",
                "mouse_ear_id_location" : mouse_id_location.lower() if mouse_ear_id != "None" else "",
                "mouse_dob" : mouse_dob.strftime("%Y-%m-%d"),
                "mouse_notes" : mouse_notes,
                "mouse_genotype" : genotype_variable,
                "mouse_source" : mouse_source.lower(),
                "mouse_arrival_date" : mouse_arrival_date.strftime("%Y-%m-%d"),
                "mouse_parental_cage" : mouse_parental_cage,
                "mouse_parental_cross" : mouse_parental_cross,
                "mouse_litter_id" : mouse_litter_id,
                "mouse_genotyping" : "1" if mouse_genotyping == "Yes" else "0",
                "mouse_genotyping_date" : mouse_genotyping_date.strftime("%Y-%m-%d") if mouse_genotyping == "Yes" and mouse_genotyping_date != None else "",
                "mouse_wellplate_number" : mouse_wellplate_number if mouse_genotyping == "Yes" else "",
                "mouse_genotype_notes" : mouse_genotype_notes if mouse_genotyping == "Yes" else "",
                "mouse_transfer" : "1" if mouse_transfer == "Yes" else "0",
                "mouse_transfer_notes" : mouse_transfer_notes if mouse_transfer == "Yes" else "",
                "mouse_sac_date" : mouse_sac_date.strftime("%Y-%m-%d") if mouse_sac == "Yes" and mouse_sac_date != None else "",
                "mouse_sac_notes" : mouse_sac_notes if mouse_sac == "Yes" else "",
            }

            columns_to_update = list(fields.keys())
            values_to_assign = list(fields.values())
            mouse_local.loc[mouse_local.index[0], columns_to_update] = values_to_assign
            local[i] = pd.concat([mouse_local, litters_local, experiments_local], ignore_index=True)
            st.session_state["mouse_info"] = pd.concat(local, ignore_index=True)

        if tabs[len(tab_names)-1].open:
            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**Reservation Information**")

            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                # Flag Information
                request_flag = st.radio(
                    "Flag",
                    key = f"mouse_flag{i}",
                    options = ["Available","Breeding","Reserved","Plan to Sac"],
                    horizontal = True,
                    disabled = disable,
                    index = mouse_flag,
                    label_visibility = "collapsed",
                )
                if request_flag == "Reserved" or request_flag == "Breeding" or request_flag == "Plan to Sac":
                    cola, colb = st.columns(2)
                    with cola:
                        requestor = st.text_input(
                            "Requestor",
                            key = f"requestor{i}",
                            disabled = disable,
                            value = mouse_local["request_person"].iloc[0]
                        )
                        request_date = st.date_input(
                            "Request Date",
                            key = f"request_date{i}",
                            disabled = disable,
                            value = None if mouse_local["request_date"].iloc[0]=="" else mouse_local["request_date"].iloc[0]
                        )
                    with colb:
                        request_notes = st.text_area(
                            "Request Notes",
                            key = f"request_notes{i}",
                            disabled = disable,
                            height = "stretch",
                            value = mouse_local["request_notes"].iloc[0],
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
                            "Planned Experiments",
                            key = f"request_experiment{i}",
                            disabled = disable,
                            value = mouse_local["request_experiment"].iloc[0],
                        )
                        request_experiment_date = st.date_input(
                            "Planned Experiment Date",
                            key = f"request_experiment_date{i}",
                            disabled = disable,
                            value = None if mouse_local["request_experiment_date"].iloc[0]=="" else mouse_local["request_experiment_date"].iloc[0]
                        )
                    with colb:
                        request_experiment_notes = st.text_area(
                            "Experiment Notes",
                            key = f"request_experiment_notes{i}",
                            disabled = disable,
                            height = "stretch",
                            value = mouse_local["request_experiment_notes"].iloc[0],
                        )
            if disable == False:
                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    st.divider()

            if request_flag != None and request_flag != "Available":
                fields = {
                    "request_flag" : request_flag.lower().replace(" ","_"),
                    "request_person" : requestor,
                    "request_date" : request_date.strftime("%Y-%m-%d") if request_date != None else "",
                    "request_notes" : request_notes,
                    "request_experiment" : request_experiment.lower().replace(" ","_") if request_flag == "Reserved" else "",
                    "request_experiment_date" : request_experiment_date.strftime("%Y-%m-%d") if request_flag == "Reserved" and request_experiment_date != None else "",
                    "request_experiment_notes" : request_experiment_notes if request_flag == "Reserved" else "",
                }
                columns_to_update = list(fields.keys())
                values_to_assign = list(fields.values())
                mouse_local.loc[mouse_local.index[0], columns_to_update] = values_to_assign
                local[i] = pd.concat([mouse_local, litters_local, experiments_local], ignore_index=True)
                st.session_state["mouse_info"] = pd.concat(local, ignore_index=True)

        if (mouse_local["breeding_cage"].iloc[0] != "" or disable==False) and tabs[1].open:
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
                        value = mouse_local["breeding_cage"].iloc[0],
                    )
                    breeding_date_created = st.date_input(
                        "Date Created",
                        key = f"breeding_date_created{i}",
                        disabled = disable,
                        value = None if mouse_local["breeding_date_created"].iloc[0]=="" else mouse_local["breeding_date_created"].iloc[0]
                    )
                with colb:
                    breeding_partner = st.text_input(
                        "Breeding Partner",
                        key = f"breeding_partner{i}",
                        disabled = disable,
                        value = mouse_local["breeding_partner"].iloc[0],
                    )
                    breeding_separated_date = st.date_input(
                        "Date Separated (Optional)",
                        key = f"breeding_separated_date{i}",
                        disabled = disable,
                        value = None if mouse_local["breeding_separated_date"].iloc[0]=="" else mouse_local["breeding_separated_date"].iloc[0]
                    )
                with colc:
                    breeding_notes = st.text_area(
                        "Breeding Notes",
                        key = f"breeding_notes{i}",
                        disabled = disable,
                        height = "stretch",
                        value = mouse_local["breeding_notes"].iloc[0],
                    )
                st.divider()

            fields = {
                "breeding_cage" : breeding_cage,
                "breeding_date_created" : breeding_date_created.strftime("%Y-%m-%d") if breeding_date_created != None else "",
                "breeding_partner" : breeding_partner,
                "breeding_separated_date" : breeding_separated_date.strftime("%Y-%m-%d") if breeding_separated_date != None else "",
                "breeding_notes" : breeding_notes,
            }
            columns_to_update = list(fields.keys())
            values_to_assign = list(fields.values())
            mouse_local.loc[mouse_local.index[0], columns_to_update] = values_to_assign
            local[i] = pd.concat([mouse_local, litters_local, experiments_local], ignore_index=True)
            st.session_state["mouse_info"] = pd.concat(local, ignore_index=True)

        if (mouse_local["breeding_cage"].iloc[0] != "" or disable==False) and tabs[2].open:
            if len(litters_local) == 0:
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown("**Litter Information**")
                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    st.markdown(f":small[No litter information is available for this mouse.]")
                    st.divider()
            
            for j in range(len(litters_local)):
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown(f":primary-background[**Litter: {litters_local["litter_id"].iloc[j]}**]")

                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    st.markdown(f":small[**Litter Information**]")
                    cola, colb, colc = st.columns(3)
                    with cola:
                        litter_dob = st.date_input(
                            "Date of Birth",
                            key = f"litter_dob{i}{j}",
                            disabled = disable,
                            value = None if litters_local["litter_dob"].iloc[j]=="" else litters_local["litter_dob"].iloc[j]
                        )
                    with colb:
                        litter_date_to_wean = st.date_input(
                            "Calculated Weaning Date",
                            key = f"litter_date_to_wean{i}{j}",
                            disabled = True,
                            value = litters_local["litter_date_to_wean"].iloc[j]
                        )
                    with colc:
                        litter_wean_date = st.date_input(
                            "Actual Weaning Date",
                            key = f"litter_wean_date{i}{j}",
                            disabled = disable,
                            value = None if litters_local["litter_wean_date"].iloc[j]=="" else litters_local["litter_wean_date"].iloc[i]
                        )
                    litter_notes_new = st.text_input(
                        "New Litter Notes",
                        key = f"litter_notes_new{i}{j}",
                        disabled = disable,
                        value = litters_local["litter_notes_new"].iloc[j],
                    )
                    st.markdown(f":small[**Weaning Information**]")
                    cola, colb, colc = st.columns([1,1,2])
                    with cola:
                        litter_wean_num_m = st.text_input(
                            "Male Pups Weaned",
                            key = f"litter_wean_num_m{i}{j}",
                            disabled = disable,
                            value = litters_local["litter_wean_num_m"].iloc[j]
                        )
                        litter_sac_num_m = st.text_input(
                            "Male Pups Sacced",
                            key = f"litter_sac_num_m{i}{j}",
                            disabled = disable,
                            value = litters_local["litter_sac_num_m"].iloc[j]
                        )
                    with colb:
                        litter_wean_num_f = st.text_input(
                            "Female Pups Weaned",
                            key = f"litter_wean_num_f{i}{j}",
                            disabled = disable,
                            value = litters_local["litter_wean_num_f"].iloc[j]
                        )
                        litter_sac_num_f = st.text_input(
                            "Female Pups Sacced",
                            key = f"litter_sac_num_f{i}{j}",
                            disabled = disable,
                            value = litters_local["litter_sac_num_f"].iloc[j]
                        )
                    with colc:
                        litter_notes_wean = st.text_area(
                            "Weaning Notes",
                            key = f"litter_notes_wean{i}{j}",
                            disabled = disable,
                            height = "stretch",
                            value = litters_local["litter_notes_wean"].iloc[j],
                        )
                    if litters_local["litter_reserver"].iloc[j]!="":
                        st.markdown(f":small[**Reservation Information**]")
                        cola, colb = st.columns([1,2])
                        with cola:
                            litter_reserver = st.text_input(
                                "Reserved By",
                                key = f"litter_reserver{i}{j}",
                                disabled = disable,
                                value = litters_local["litter_reserver"].iloc[j],
                            )

                            if litters_local["litter_reservation"].iloc[j]=="development":
                                litter_flag = 0
                            elif litters_local["litter_reservation"].iloc[j]=="breeding":
                                litter_flag = 1
                            else:
                                litter_flag = None

                            litter_reservation = st.selectbox(
                                "Reservation Type",
                                key = f"litter_reservation{i}{j}",
                                options = ["Development","Breeding"],
                                disabled = disable,
                                index = litter_flag,
                            )
                            litter_reservation_date = st.date_input(
                                "Reservation Date",
                                key = f"litter_reservation_date{i}{j}",
                                disabled = disable,
                                value = None if litters_local["litter_reservation_date"].iloc[j]=="" else litters_local["litter_reservation_date"].iloc[j]
                            )
                        with colb:
                            litter_notes_reserve = st.text_area(
                                "Weaning Notes",
                                key = f"litter_notes_reserve{i}{j}",
                                disabled = disable,
                                height = "stretch",
                                value = litters_local["litter_notes_reserve"].iloc[j],
                            )
                    st.divider()

        if (len(experiments_local) > 0 or disable==False)and tabs[len(tab_names)-2].open:
            if len(experiments_local) == 0:
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown("**Experiment Information**")
                col1, col2, col3 = st.columns([0.2,2,0.2])
                with col2:
                    st.markdown(f":small[No experiment information is available for this mouse.]")
                    st.divider()
            
            for j in range(len(experiments_local)):
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown(f"**{experiments_local["experiment_type"].iloc[j].title()} Information**")

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
                                value = experiments_local["experiment_type"].iloc[j].title(),
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
                                value = experiments_local["experiment_date"].iloc[j],
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
                                value = experiments_local["experiment_experimentor"].iloc[j].title(),
                                disabled = disable
                            )
                    with colb:
                        st.text_area(
                            "Experiment Notes",
                            key = f"experiment_notes{i}{j}",
                            label_visibility="collapsed",
                            value = experiments_local["experiment_notes"].iloc[j],
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
                    print("update mouse information")