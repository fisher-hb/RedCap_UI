import streamlit as st
import redcap_utils
import time

st.subheader("Wean New Litter")

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Litter Information
# --------------------------------------------------
info = st.session_state["litter"].copy()

sire_id = info.loc[0, "sire_id"]
dame_id = info.loc[0, "dame_id"]
breeding_cage = info.loc[0, "breeding_cage"]
litter_index = info.loc[0, "litter_index"]
litter_id = info.loc[0, "litter_id"]
parental_cross = info.loc[0, "parental_cross"]
dob_input = info.loc[0,"dob"]

litter_info = False

col1,col2 = st.columns(2)
with col1:
    st.markdown(f":material/pest_control_rodent: Litter ID: {litter_id}")
    st.markdown(f":material/calendar_month: Litter DOB: {dob_input}")
    st.markdown(f":material/genetics: Parental Cross: {parental_cross}")

    arrival_date = st.date_input(
        "Weaning Date",
        format = "YYYY-MM-DD",
    )
with col2:
    weaning_notes = st.text_area(
        "Weaning Notes",
        placeholder = "Optional notes about litter and weaning here",
        height = "stretch"
    )

st.divider()

# --------------------------------------------------
# Genotyping Information
# --------------------------------------------------

st.subheader("Tag and Tail Information")

option_map = {
    0: ":material/check: All",
    1: ":material/male: Male Only",
    2: ":material/female: Female Only",
    3: ":material/close: None",
}
tag_tail = st.segmented_control(
    "Which Mice are Being Genotyped?",
    options=option_map.keys(),
    format_func=lambda option: option_map[option],
    selection_mode="single",
    default = 0,
    width = "stretch"
)

if tag_tail == 0 or tag_tail == 1 or tag_tail == 2:
    wellplate = st.text_input(
        "Wellplate Number",
        placeholder = "Example: T2319693"
    )

    genotyped_date = st.date_input(
            "Date of Genotyping",
            format = "YYYY-MM-DD",
            value = arrival_date
        )

st.divider()

# --------------------------------------------------
# Male Pup Information
# --------------------------------------------------
    
col1,col2 = st.columns(2,border=True)

male_id_nums = []
male_id_locs = []
male_ids = []
male_genotypes = []
male_cages = []
male_notes = []

with col1:
    
    st.subheader("Male Pups")

    cola, colb = st.columns(2)
    with cola:
        number_of_males = st.number_input(
            "Weaned Pups",
            key = "weaned_males",
            value=0,
            min_value=0,
        )
    with colb:
        number_of_sacced_males = st.number_input(
            "Sacced Pups",
            key = "sacced_males",
            value=0,
            min_value=0,
        )
    number_of_sacced_males = int(number_of_sacced_males)
    number_of_males = int(number_of_males)
    
    if number_of_males > 0:
        male_cage_num = st.text_input(
            "Male Cage Number",
            placeholder = "Example: 123456",
        )

        if number_of_males > 5:
            male_cage_num2 = st.text_input(
                "Male Cage 2 Number",
                placeholder = "Example: 123456",
            )

        if male_cage_num != "" and number_of_males < 6:
            enter_male_info = True
        elif male_cage_num != "" and male_cage_num2 and number_of_males > 5:
            enter_male_info = True
        else:
            enter_male_info = False

        if enter_male_info:

            for i in range(1, number_of_males + 1):
                st.divider()
                st.markdown(f"**:blue-background[Male Mouse {i}]**")

                cage1_or2 = male_cage_num
                id_loc = None

                if tag_tail == 0 or tag_tail == 1:
                    cola, colb, colc = st.columns([0.9,3.1,1.2], gap="xsmall", vertical_alignment="center")
                    
                    with cola:
                        st.caption("Mouse ID")

                    with colb:
                        mouse_id_num = st.text_input(
                            f"Male Mouse {i} ID",
                            label_visibility = "collapsed",
                            placeholder = "Mouse ID"
                        )

                    if mouse_id_num != "" and int(mouse_id_num) % 2 == 0:
                        id_loc = "R"
                    elif mouse_id_num != "" and int(mouse_id_num) % 2 != 0:
                        id_loc = "L"

                    with colc:
                        mouse_id_loc = st.segmented_control(
                            f"male mouse {i} loc",
                            options = ["L", "R"],
                            selection_mode="single",
                            default = id_loc,
                            label_visibility = "collapsed"
                        )

                else:
                    mouse_id_num = st.text_input(
                        f"Male Mouse {i} ID",
                        value=f"{cage1_or2}_{i}",
                        label_visibility = "collapsed"
                    )
                    mouse_id_loc = None

                if number_of_males > 5:
                    cola, colb = st.columns([1.2,1], gap="xsmall", vertical_alignment="center")
                    with cola:
                        st.caption("Cage Number")
                    with colb:
                        cage1_or2 = st.radio(
                            f"Cage Assignment: M{i}?",
                            options = [
                                male_cage_num if male_cage_num != "" else "Cage 1",
                                male_cage_num2 if male_cage_num2 != "" else "Cage 2"],
                            index = 0 if i<number_of_males/2+1 else 1,
                            label_visibility="collapsed",
                            horizontal = True,
                        )


                genotype_df = redcap_utils.get_possible_genotypes(parental_cross,"male")
                genotype_labels = genotype_df["offspring_genotype"].tolist()
                
                cola, colb = st.columns([0.9,4.4], gap="xsmall", vertical_alignment="center")
                with cola:
                    st.caption("Genotype")
                with colb:
                    genotype_label = st.selectbox(
                        "Genotype",
                        key = f"genotype male {i}",
                        options = ["Waiting on Results"] if tag_tail == 0 or tag_tail == 1 else genotype_labels + ["Not Genotyped"],
                        index = 0 if tag_tail == 0 or tag_tail == 1 else None,
                        disabled = True if tag_tail == 0 or tag_tail == 1 else False,
                        label_visibility="collapsed"
                    )
                    genotype = redcap_utils.genotype_label_to_variable(genotype_label)

                cola, colb = st.columns([0.9,4.4], gap="xsmall")
                with cola:
                    st.caption("Notes")
                with colb:
                    male_note = st.text_area(
                        "Notes",
                        key = f"male note {i}",
                        label_visibility="collapsed",
                    )
                
                mouse_id = (f"{redcap_utils.dob_to_yymm(str(dob_input))}:{mouse_id_num}")

                if genotype_label != None:
                    genotype = redcap_utils.genotype_label_to_variable(genotype_label)

                male_id_nums.append(mouse_id_num)
                male_id_locs.append(mouse_id_loc)
                male_ids.append(mouse_id)
                male_genotypes.append(genotype)
                male_cages.append(cage1_or2)
                male_notes.append(male_note)
                
                
# --------------------------------------------------
# Female Pup Information
# --------------------------------------------------
    
female_id_nums = []
female_id_locs = []
female_ids = []
female_genotypes = []
female_cages = []
female_notes = []

with col2:
    
    st.subheader("Female Pups")

    cola, colb = st.columns(2)
    with cola:
        number_of_females = st.number_input(
            "Weaned Pups",
            key = "weaned_females",
            value=0,
            min_value=0,
        )
    with colb:
        number_of_sacced_females = st.number_input(
            "Sacced Pups",
            key = "sacced_females",
            value=0,
            min_value=0,
        )
    number_of_sacced_females = int(number_of_sacced_females)
    number_of_females = int(number_of_females)

    if number_of_females > 0:
        female_cage_num = st.text_input(
            "Female Cage Number",
            placeholder = "Example: 123456",
        )

        if number_of_females > 5:
            female_cage_num2 = st.text_input(
                "Female Cage 2 Number",
                placeholder = "Example: 123456",
            )

        if female_cage_num != "" and number_of_females < 6:
            enter_female_info = True
        elif female_cage_num != "" and female_cage_num2 and number_of_females > 5:
            enter_female_info = True
        else:
            enter_female_info = False

        if enter_female_info:

            for i in range(1, number_of_females + 1):
                st.divider()
                st.markdown(f"**:red-background[Female Mouse {i}]**")

                cage1_or2 = female_cage_num
                id_loc = None

                if tag_tail == 0 or tag_tail == 2:
                    cola, colb, colc = st.columns([0.9,3.1,1.2], gap="xsmall", vertical_alignment="center")
                    
                    with cola:
                        st.caption("Mouse ID")

                    with colb:
                        mouse_id_num = st.text_input(
                            f"Female Mouse {i} ID",
                            label_visibility = "collapsed",
                            placeholder = "Mouse ID"
                        )

                    if mouse_id_num != "" and int(mouse_id_num) % 2 == 0:
                        id_loc = "R"
                    elif mouse_id_num != "" and int(mouse_id_num) % 2 != 0:
                        id_loc = "L"

                    with colc:
                        mouse_id_loc = st.segmented_control(
                            f"female mouse {i} loc",
                            options = ["L", "R"],
                            selection_mode="single",
                            default = id_loc,
                            label_visibility = "collapsed"
                        )

                else:
                    mouse_id_num = st.text_input(
                        f"Female Mouse {i} ID",
                        value=f"{cage1_or2}_{i}",
                        label_visibility = "collapsed"
                    )
                    mouse_id_loc = None

                if number_of_females > 5:
                    cola, colb = st.columns([1.2,1], gap="xsmall", vertical_alignment="center")
                    with cola:
                        st.caption("Cage Number")
                    with colb:
                        cage1_or2 = st.radio(
                            f"Cage Assignment: F{i}?",
                            options = [
                                female_cage_num if female_cage_num != "" else "Cage 1",
                                female_cage_num2 if female_cage_num2 != "" else "Cage 2"],
                            index = 0 if i<number_of_females/2+1 else 1,
                            label_visibility="collapsed",
                            horizontal = True,
                        )


                genotype_df = redcap_utils.get_possible_genotypes(parental_cross,"female")
                genotype_labels = genotype_df["offspring_genotype"].tolist()
                
                cola, colb = st.columns([0.9,4.4], gap="xsmall", vertical_alignment="center")
                with cola:
                    st.caption("Genotype")
                with colb:
                    genotype_label = st.selectbox(
                        "Genotype",
                        key = f"genotype female {i}",
                        options = ["Waiting on Results"] if tag_tail == 0 or tag_tail == 2 else genotype_labels + ["Not Genotyped"],
                        index = 0 if tag_tail == 0 or tag_tail == 2 else None,
                        disabled = True if tag_tail == 0 or tag_tail == 2 else False,
                        label_visibility="collapsed"
                    )
                    genotype = redcap_utils.genotype_label_to_variable(genotype_label)

                cola, colb = st.columns([0.9,4.4], gap="xsmall")
                with cola:
                    st.caption("Notes")
                with colb:
                    female_note = st.text_area(
                        "Notes",
                        key = f"female note {i}",
                        label_visibility="collapsed",
                    )
                
                mouse_id = (f"{redcap_utils.dob_to_yymm(str(dob_input))}:{mouse_id_num}")

                if genotype_label != None:
                    genotype = redcap_utils.genotype_label_to_variable(genotype_label)

                female_id_nums.append(mouse_id_num)
                female_id_locs.append(mouse_id_loc)
                female_ids.append(mouse_id)
                female_genotypes.append(genotype)
                female_cages.append(cage1_or2)
                female_notes.append(female_note)
                
st.divider()

submission_button = st.button(
    "Submit to Redcap", 
    type="primary",
    )

# --------------------------------------------------
# Format Records for RedCap Submission
# --------------------------------------------------

if submission_button:
    
    with status_container:

        errors = []
        if number_of_males > 0 and not male_cage_num:
            errors.append("Cage number is required.")
        if number_of_females > 0 and not female_cage_num:
            errors.append("Cage number is required.")
        if number_of_males > 5 and not male_cage_num2:
            errors.append("Second cage number is required for male mice.")
        if number_of_females > 5 and not female_cage_num2:
            errors.append("Second cage number is required for female mice.")
        if errors:
            st.write("Please fix the following issues:")
            for error in errors:
                st.error(f"{error}")
            st.divider()

        if not errors:

            fields = {
                "litter_wean_date": arrival_date.strftime("%Y-%m-%d"),
                "litter_wean_num_m": str(number_of_males),
                "litter_wean_num_f": str(number_of_females),
                "litter_sac_num_m": str(number_of_sacced_males),
                "litter_sac_num_f": str(number_of_sacced_females),
                "litter_notes_wean": weaning_notes if weaning_notes else "",
                "litter_information_complete": "2",
                }
            
            redcap_utils.add_repeating_instance(sire_id,"litter_information",str(litter_index),fields)
            redcap_utils.add_repeating_instance(dame_id,"litter_information",str(litter_index),fields)

            for i in range(number_of_males):
                if str(male_id_locs[i]).lower() == "none":
                    ear_id_location = ""
                else:
                    ear_id_location = str(male_id_locs[i]).lower()
                fields = {
                    "mouse_ear_id_type": "tag" if tag_tail == 0 or tag_tail == 1 else "none",
                    "mouse_ear_id": male_id_nums[i] if tag_tail == 0 or tag_tail == 1 else "",
                    "mouse_ear_id_location": ear_id_location if tag_tail == 0 or tag_tail == 1 else "",
                    "mouse_protocol": "2024",
                    "mouse_sex": "male",
                    "mouse_cage_number": male_cages[i],
                    "mouse_genotype": male_genotypes[i],
                    "mouse_genotyping": "1" if tag_tail == 0 or tag_tail == 1 else "0",
                    "mouse_genotyping_date": genotyped_date.strftime("%Y-%m-%d") if tag_tail == 0 or tag_tail == 1 else "",
                    "mouse_wellplate_number": wellplate if tag_tail == 0 or tag_tail == 1 else "",
                    "mouse_parental_cage": breeding_cage,
                    "mouse_parental_cross": parental_cross,
                    "mouse_arrival_date": arrival_date.strftime("%Y-%m-%d"),
                    "mouse_litter_id": litter_id,
                    "mouse_dob": dob_input,
                    "mouse_source": "bred",
                    "mouse_notes": male_notes[i],
                    "mouse_info_complete": "0",
                    }
                redcap_utils.create_new_mouse_record(male_ids[i], fields)
                st.success(f"Mouse  {male_ids[i]}  added succesfully")

            for i in range(number_of_females):
                if str(female_id_locs[i]).lower() == "none":
                    ear_id_location = ""
                else:
                    ear_id_location = str(female_id_locs[i]).lower()
                fields = {
                    "mouse_ear_id_type": "tag" if tag_tail == 0 or tag_tail == 2 else "none",
                    "mouse_ear_id": female_id_nums[i] if tag_tail == 0 or tag_tail == 2 else "",
                    "mouse_ear_id_location": ear_id_location if tag_tail == 0 or tag_tail == 2 else "",
                    "mouse_protocol": "2024",
                    "mouse_sex": "female",
                    "mouse_cage_number": female_cages[i],
                    "mouse_genotype": female_genotypes[i],
                    "mouse_genotyping": "1" if tag_tail == 0 or tag_tail == 2 else "0",
                    "mouse_genotyping_date": genotyped_date.strftime("%Y-%m-%d") if tag_tail == 0 or tag_tail == 2 else "",
                    "mouse_wellplate_number": wellplate if tag_tail == 0 or tag_tail == 2 else "",
                    "mouse_parental_cage": breeding_cage,
                    "mouse_parental_cross": parental_cross,
                    "mouse_arrival_date": arrival_date.strftime("%Y-%m-%d"),
                    "mouse_litter_id": litter_id,
                    "mouse_dob": dob_input,
                    "mouse_source": "bred",
                    "mouse_notes": female_notes[i],
                    "mouse_info_complete": "0",
                    }
                redcap_utils.create_new_mouse_record(female_ids[i], fields)
                st.success(f"Mouse  {female_ids[i]}  added succesfully")
            
            st.info("Returning you to Breeding Cages")
            st.divider()
    time.sleep(2)
    st.session_state["redcap_df"] = redcap_utils.load_records()
    st.switch_page("pages/breeding_cages.py")