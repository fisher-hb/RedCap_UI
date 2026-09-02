from numpy.strings import index
import streamlit as st
import time
from datetime import date
import redcap_utils

st.subheader("Add New Experiment")

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Mouse Information
# --------------------------------------------------

df = st.session_state["redcap_df"]
mouse_names = st.session_state["mice_request"].copy()
''
# --------------------------------------------------
# Create Expanders
# --------------------------------------------------

for i in range(len(mouse_names)):
    mouse_df = df[(df["mouse_id"] == mouse_names[i])]
    experiment_df = mouse_df[(mouse_df["redcap_repeat_instrument"] == "experiment_information")]
    expander = st.expander(
        f"{mouse_df["mouse_id"].iloc[0]}",
    )

    with expander:
        st.markdown("")
        st.markdown(f":primary-background[**Mouse ID -- {mouse_df["mouse_id"].iloc[0]}**]")
        experiments_performed = []
        for j in range(len(experiment_df)):
            experiments_performed.append(f":material/graph_6: {experiment_df["experiment_type"].iloc[j].title()}")

        tab_names = [":material/pest_control_rodent: Mouse Information"] + experiments_performed + [f":material/add: New Experiment"] if len(experiments_performed) > 0 else [f":material/pest_control_rodent: Mouse Information", f":material/add: New Experiment"]

        tabs = st.tabs(
            tab_names,
            key = f"tabs_{i}",
            width="stretch",
            on_change="rerun",
            default = f":material/add: New Experiment")
        
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
                        disabled = True,
                    )
                with colb:
                    mouse_cage_number = st.text_input(
                        "Cage Number",
                        key = f"mouse_cage_number{i}",
                        disabled = True,
                        value = mouse_df["mouse_cage_number"].iloc[0]
                    )
                with colc:
                    mouse_protocol = st.text_input(
                        "Protocol Year",
                        key = f"mouse_protocol{i}",
                        disabled = True,
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
                        disabled = True,
                    )
                with colb:
                    if mouse_ear_id == "Ear Tag": 
                        mouse_tag_number = st.text_input(
                            "Tag Number",
                            key = f"mouse_tag_number{i}",
                            disabled = True,
                            value = str(((mouse_df["mouse_id"].iloc[0]).split(":"))[1])
                        )
                    if mouse_ear_id == "Ear Punch":
                        mouse_id_location = st.selectbox(
                            "ID Location",
                            key = f"mouse_id_location{i}",
                            options = ["R","L","B","FR","FL","FRT","FN","FRY","FLY","FNY","FD","MN","MR","ML","MRT","MD","MLT"],
                            index = id_location_index,
                            disabled = True,
                        )
                with colc:
                    if mouse_ear_id == "Ear Tag": 
                        mouse_id_location = st.selectbox(
                            "ID Location",
                            key = f"mouse_id_location{i}",
                            options = ["R","L"],
                            index = id_location_index,
                            disabled = True,
                        )

                # Age information
                # st.divider()
                cola, colb, colc, cold = st.columns(4)
                with cola:
                    mouse_dob = st.date_input(
                        "Date of Birth",
                        key = f"mouse_dob{i}",
                        disabled = True,
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
                    disabled = True,
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
                        disabled = True,
                        value = genotype_label
                    )
                with colb:
                    mouse_source = st.text_input(
                        "Source",
                        key = f"mouse_source{i}",
                        disabled = True,
                        value = mouse_df["mouse_source"].iloc[0].title()
                    )
                with colc:
                    mouse_arrival_date = st.date_input(
                        "Wean/Arrival Date",
                        key = f"mouse_arrival_date{i}",
                        disabled = True,
                        value = None if mouse_df["mouse_arrival_date"].iloc[0]=="" else mouse_df["mouse_arrival_date"].iloc[0]
                    )

                # Parent Information
                # st.divider()
                cola, colb, colc = st.columns([1,2,1])
                with cola:
                    mouse_parental_cage = st.text_input(
                        "Parent Cage",
                        key = f"mouse_parent_cage{i}",
                        disabled = True,
                        value = mouse_df["mouse_parental_cage"].iloc[0]
                    )
                with colb:
                    mouse_parental_cross = st.text_input(
                        "Parental Cross",
                        key = f"mouse_parental_cross{i}",
                        disabled = True,
                        value = mouse_df["mouse_parental_cross"].iloc[0]
                    )
                with colc:
                    mouse_litter_id = st.text_input(
                        "Litter ID",
                        key = f"mouse_litter_id{i}",
                        disabled = True,
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
                        disabled = True,
                        index = int(mouse_df["mouse_genotyping"].iloc[0])
                    )
                if mouse_genotyping_performed == "Yes":
                    with colb:
                        mouse_genotyping_date = st.date_input(
                            "Genotyping Date",
                            key = f"mouse_genotyping_date{i}",
                            disabled = True,
                            value = None if mouse_df["mouse_genotyping_date"].iloc[0]=="" else mouse_df["mouse_genotyping_date"].iloc[0]
                        )
                    with colc:
                        mouse_wellplate_number = st.text_input(
                            "Wellplate Number",
                            key = f"mouse_wellplate_number{i}",
                            disabled = True,
                            value = mouse_df["mouse_wellplate_number"].iloc[0]
                        )
                    # st.divider()
                    mouse_genotype_notes = st.text_area(
                        "Genotyping Notes",
                        key = f"mouse_genotyping_notes{i}",
                        disabled = True,
                        value = mouse_df["mouse_genotype_notes"].iloc[0]
                    )

        for j in range(len(tab_names)-2):
            if tabs[j+1].open:
                col1, col2 = st.columns([0.1,2.3])
                with col2:
                    st.markdown(f"**{experiment_df["experiment_type"].iloc[j]} Information**")
    
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
                                value = experiment_df["experiment_type"].iloc[j].title(),
                                disabled = True,
                            )
    
                        colc, cold = st.columns([0.45,1],vertical_alignment="center")
                        with colc:
                            st.markdown(f":small[Date Performed]")
                        with cold: 
                            st.date_input(
                                "Experiment Date",
                                key = f"experiment_date{i}{j}",
                                label_visibility = "collapsed",
                                value = experiment_df["experiment_date"].iloc[j],
                                disabled = True
                            )

                        colc, cold = st.columns([0.45,1],vertical_alignment="center")
                        with colc:
                            st.markdown(f":small[Performed By]")
                        with cold: 
                            st.text_input(
                                "Experimentor",
                                key = f"experimentor{i}{j}",
                                label_visibility = "collapsed",
                                value = experiment_df["experiment_experimentor"].iloc[j].title(),
                                disabled = True
                            )
                    with colb:
                        st.text_area(
                            "Experiment Notes",
                            key = f"experiment_notes{i}{j}",
                            label_visibility="collapsed",
                            value = experiment_df["experiment_notes"].iloc[j],
                            disabled = True
                        )

        if tabs[len(tab_names)-1].open:
            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.markdown(f"**New Experiment Information**")
                if mouse_df["mouse_sac_date"].iloc[0] != "":
                    st.markdown(f":small[Please note: This mouse has been sacced already and is therefore only available for certain experiments at this time]")

            col1, col2, col3 = st.columns([0.2,2,0.2])
            with col2:
                cola, colb = st.columns(2)
                with cola:
                    colc, cold = st.columns([0.45,1],vertical_alignment="center")
                    with colc:
                        st.markdown(f":small[Experiment]")
                    with cold: 
                        experiment_type = st.selectbox(
                            "Experiment Type",
                            key = f"new_experiment_type{i}",
                            label_visibility = "collapsed",
                            index = None,
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
                    colc, cold = st.columns([0.45,1],vertical_alignment="center")
                    with colc:
                        st.markdown(f":small[Date Performed]")
                    with cold: 
                        experiment_date = st.date_input(
                            "Experiment Date",
                            key = f"new_experiment_date{i}",
                            label_visibility = "collapsed",
                        )
                    colc, cold = st.columns([0.45,1],vertical_alignment="center")
                    with colc:
                        st.markdown(f":small[Performed By]")
                    with cold: 
                        experimentor = st.text_input(
                            "Experimentor",
                            key = f"new_experimentor{i}",
                            label_visibility = "collapsed",
                        )
                    colc, cold = st.columns([1,0.65],vertical_alignment="center")
                    with colc:
                        st.markdown(f":small[Sacced For Experiment?]")
                    with cold: 
                        sacced = st.radio(
                            "Animal Sacced",
                            key = f"animal_sacced{i}",
                            label_visibility="collapsed",
                            options = ["Yes","No"],
                            index = None,
                            horizontal=True
                        )
                with colb:
                    experiment_notes = st.text_area(
                        "Experiment Notes",
                        key = f"new_experiment_notes{i}",
                        height = "stretch",
                        label_visibility="collapsed",
                        placeholder = "Optional notes about experiment"
                    )

            col1, col2 = st.columns([0.1,2.3])
            with col2:
                st.divider()
                submission_button = st.button(
                    "Submit to Redcap",
                    key = f"submission_button{i}",
                    type = "primary"
                )

            if submission_button:
                with status_container:
                    errors = []
                    if experiment_type == "":
                        errors.append("Experiment type is required.")
                    if sacced == None:
                        errors.append("Please indicate if mouse was sacced during experiment")
                    if errors:
                        st.write("Please fix the following issues:")
                        for error in errors:
                            st.error(f"{error}")
                        st.divider()
            
                    if not errors:
                        fields = {
                            "experiment_type": experiment_type.lower().replace(" ", "_"),
                            "experiment_experimentor": experimentor.lower(),
                            "experiment_date": experiment_date.strftime("%Y-%m-%d"),
                            "experiment_notes": experiment_notes,
                            "experiment_information_complete": "2",
                            }
                        redcap_utils.add_repeating_instance(mouse_df["mouse_id"].iloc[0],"experiment_information",str(len(tab_names)-1),fields)

                        if sacced == "Yes":
                            fields = {
                                "mouse_sac_date": experiment_date.strftime("%Y-%m-%d"),
                                "mouse_info_complete": "2",
                            }
                            redcap_utils.create_new_mouse_record(mouse_df["mouse_id"].iloc[0],fields)

                        st.success(f"Experiment added succesfully to mouse {mouse_df["mouse_id"].iloc[0]}")
                        time.sleep(2)
                        st.session_state["redcap_df"] = redcap_utils.load_records()
                        st.rerun()
    
        

            