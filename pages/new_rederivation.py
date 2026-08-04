import streamlit as st
import redcap_utils
import time

st.subheader("New Rederived Cage")

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Rederivation Information
# --------------------------------------------------

st.divider()

col1, col2 = st.columns([1,1.5])

with col1:
    source = st.text_input(
        "Origin of mice used for rederivation",
        placeholder = "Example: Dame Source, Sire Source"
    )

    parent_cage_number = st.text_input(
        "Rederivation Cage Number",
        placeholder = "Example: 123456_R"
    )

    dob = st.date_input(
        "Date of Birth",
        format = "YYYY-MM-DD",
    )

    arrival_date = st.date_input(
        "Date of Transfer into Colony",
        format = "YYYY-MM-DD",
    )

with col2:
    genotyped = st.radio(
        "Have the mice been genotyped?",
        options = ["yes","no"],
        index = 0,
        horizontal = True
    )

    genotype = ""

    if genotyped == "yes":
        cola, colb = st.columns(2)
        with cola:
            genotyped_date = st.date_input(
                "Date of Genotyping",
                format = "YYYY-MM-DD",
            )
        with colb:
            wellplate = st.text_input(
                "Wellplate Number",
                placeholder = "Example: T2319693"
            )
    notes = st.text_area(
        "Notes",
        placeholder="Optional notes about rederivation",
        height = "stretch"
        )

st.divider()

col1,col2 = st.columns(2,border=True)

male_id_nums = []
male_id_locs = []
male_ids = []
male_genotypes = []
male_cages = []

with col1:
    st.subheader("Male Mice")

    number_of_males = st.number_input(
        "Number of Male Mice",
        value = 0,
    )
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

                if genotyped == "yes":
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

                genotype_choices = redcap_utils.get_genotypes()
                genotype_labels = genotype_choices["label"]
                
                cola, colb = st.columns([0.9,4.4], gap="xsmall", vertical_alignment="center")
                with cola:
                    st.caption("Genotype")
                with colb:
                    genotype_label = st.selectbox(
                        "Genotype",
                        key = f"genotype male {i}",
                        options = ["Waiting on Results"] if genotyped == "yes" else genotype_labels,
                        index = 0 if genotyped == "yes" else None,
                        disabled = True if genotyped == "yes" else False,
                        label_visibility="collapsed"
                    )
                    genotype = redcap_utils.genotype_label_to_variable(genotype_label)
                
                mouse_id = (f"{redcap_utils.dob_to_yymm(str(dob))}:{mouse_id_num}")

                if genotype_label != None:
                    genotype = redcap_utils.genotype_label_to_variable(genotype_label)

                male_id_nums.append(mouse_id_num)
                male_id_locs.append(mouse_id_loc)
                male_ids.append(mouse_id)
                male_genotypes.append(genotype)
                male_cages.append(cage1_or2)

female_id_nums = []
female_id_locs = []
female_ids = []
female_genotypes = []
female_cages = []


with col2:
    
    st.subheader("Female Mice")

    number_of_females = st.number_input(
        "Number of Female Mice",
        value=0,
    )
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

                if genotyped == "yes":
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
                
                cola, colb = st.columns([0.9,4.4], gap="xsmall", vertical_alignment="center")
                with cola:
                    st.caption("Genotype")
                with colb:
                    genotype_label = st.selectbox(
                        "Genotype",
                        key = f"genotype female {i}",
                        options = ["Waiting on Results"] if genotyped == "yes" else genotype_labels,
                        index = 0 if genotyped == "yes" else None,
                        disabled = True if genotyped == "yes" else False,
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
                
                mouse_id = (f"{redcap_utils.dob_to_yymm(str(dob))}:{mouse_id_num}")

                if genotype_label != None:
                    genotype = redcap_utils.genotype_label_to_variable(genotype_label)

                female_id_nums.append(mouse_id_num)
                female_id_locs.append(mouse_id_loc)
                female_ids.append(mouse_id)
                female_genotypes.append(genotype)
                female_cages.append(cage1_or2)
            

st.divider()
submission_button = st.button("Submit Records to Redcap", type="primary")

if submission_button:
    
    with status_container:
        
        errors = []

        if number_of_males > 0 and not male_cage_num:
            errors.append("Cage number is required for male mice.")

        if number_of_females > 0 and not female_cage_num:
            errors.append("Cage number is required for female mice.")

        if number_of_males > 5 and not male_cage_num2:
            errors.append("Second cage number is required for male mice.")

        if number_of_females > 5 and not female_cage_num2:
            errors.append("Second cage number is required for female mice.")

        if not arrival_date:
            errors.append("Arrival date is required.")

        if not dob:
            errors.append("Date of birth is required.")

        if not parent_cage_number:
            errors.append("Rederivation Cage number is required.")

        if errors:
            st.write("Please fix the following issues:")

            for error in errors:
                st.error(f"{error}")
            st.divider()

        notes = f"Rederivation Information: " + source + "\n\nRederivation Cage: " + parent_cage_number + "\n\n" + notes

        if not errors:
            for i in range(number_of_males):
                fields = {
                    "mouse_ear_id_type": "tag" if genotyped == "yes" else "",
                    "mouse_ear_id": male_id_nums[i] if genotyped == "yes" else "",
                    "mouse_ear_tag_location": male_id_locs[i],
                    "mouse_protocol": "2024",
                    "mouse_sex": "male",
                    "mouse_cage_number": male_cages[i],
                    "mouse_genotype": male_genotypes[i],
                    "mouse_genotyping": 1 if genotyped == "yes" else 0,
                    "mouse_genotyping_date": genotyped_date if genotyped == "yes" else "",
                    "mouse_wellplate_number": wellplate if genotyped == "yes" else "",
                    "mouse_parental_cage": parent_cage_number,
                    "mouse_arrival_date": arrival_date.strftime("%Y-%m-%d"),
                    "mouse_litter_id": f"{parent_cage_number}_1",
                    "mouse_dob": dob.strftime("%Y-%m-%d"),
                    "mouse_source": "rederivation",
                    "mouse_notes": notes,
                    "mouse_info_complete": "0",
                    }
                redcap_utils.create_new_mouse_record(male_ids[i], fields)
                st.success(f"Mouse  {male_ids[i]}  added succesfully")

        for i in range(number_of_females):
            fields = {
                "mouse_ear_id_type": "tag" if genotyped == "yes" else "",
                "mouse_ear_id": female_id_nums[i] if genotyped == "yes" else "",
                "mouse_ear_tag_location": female_id_locs[i],
                "mouse_protocol": "2024",
                "mouse_sex": "female",
                "mouse_cage_number": female_cages[i],
                "mouse_genotype": female_genotypes[i],
                "mouse_genotyping": 1 if genotyped == "yes" else 0,
                "mouse_genotyping_date": genotyped_date if genotyped == "yes" else "",
                "mouse_wellplate_number": wellplate if genotyped == "yes" else "",
                "mouse_parental_cage": parent_cage_number,
                "mouse_arrival_date": arrival_date.strftime("%Y-%m-%d"),
                "mouse_litter_id": f"{parent_cage_number}_1",
                "mouse_dob": dob.strftime("%Y-%m-%d"),
                "mouse_source": "rederivation",
                "mouse_notes": notes,
                "mouse_info_complete": "0",
                }
            redcap_utils.create_new_mouse_record(female_ids[i], fields)
            st.success(f"Mouse  {female_ids[i]}  added succesfully")

        st.info("Returning you to Dashboard")
        st.divider()
    time.sleep(2)
    st.switch_page("pages/dashboard.py")