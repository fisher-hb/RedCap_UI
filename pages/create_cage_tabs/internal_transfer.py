import streamlit as st
import pandas as pd
import redcap_utils
import time
from datetime import datetime

def create_internal_transfer():

    st.markdown("")
    st.subheader("New Internal Transfer")
    st.markdown("")

    with st.sidebar:
        status_container = st.container()

    # --------------------------------------------------
    # Cage transfer information
    # --------------------------------------------------

    col1, col2 = st.columns([1.2,1], gap="medium")

    with col1:

        cola, colb = st.columns([0.8,3],vertical_alignment="center")
        with cola:
            st.markdown(f":small[Number of Mice]")
            st.markdown("")
            st.markdown(f":small[Sex of Mice]")
            st.markdown("")
            st.markdown(f":small[Genotype]")
            st.markdown("")
            st.markdown(f":small[Origin of Mice]")
        with colb:
            number_of_mice = st.number_input(
                "Number of Mice",
                value = 1,
                label_visibility = "collapsed",
            )
            number_of_mice = int(number_of_mice)

            genotype_choices = redcap_utils.get_genotypes()
            genotype_labels = genotype_choices["label"].tolist()

            sex = st.selectbox(
                "Sex of Mice",
                options=["Male", "Female"],
                index = None,
                label_visibility = "collapsed",
            )
            genotype_label = st.selectbox(
                "Genotype",
                options = ["Varies by Mouse"] + genotype_labels,
                index = None,
                label_visibility = "collapsed",
            )

            transfer_lab = st.text_input(
                "Origin",
                placeholder = "Example: Hyde",
                label_visibility = "collapsed",
            )

    with col2:

        order_notes = st.text_area(
            "Order Notes",
            placeholder="Optional notes about this cage order.",
            height = "stretch",
            label_visibility = "collapsed",
        )

    # --------------------------------------------------
    # Mouse Information
    # --------------------------------------------------

    st.divider()
    st.subheader("Mouse Information")
    st.markdown("")

    col1, col2 = st.columns([2,3], border=True)

    with col1:

        arrival_date = st.date_input(
            "Date of transfer",
            format = "YYYY-MM-DD",
        )   

        litter_id = st.text_input(
            "Litter ID",
            placeholder="Optional Litter ID Number",
        )

        dob = st.date_input(
            "Date of birth",
            format = "YYYY-MM-DD",
        )

        arrival_cage_number = st.text_input(
            "Arrival Cage number",
            placeholder="Example: 123456",
        )

        st.markdown("")

        auto_generate = st.radio(
            "How should mouse IDs be created?",
            options=[
                "Automatically Generated",
                "Manually Entered",
            ],
            horizontal = True
        )

    with col2:

        mouse_id_nums = []
        mouse_id_locs = []
        mouse_ids = []
        mouse_notes = []
        mouse_genotypes = []
        
        for i in range(1, number_of_mice + 1):
            st.markdown(f"**:primary-background[Mouse {i}]**")
            if auto_generate == "Automatically Generated":
                cola, colb = st.columns([0.8,5], vertical_alignment="center")
                with cola:
                    st.caption("Mouse ID")

                with colb:
                    mouse_id_num = st.text_input(
                        f"Mouse {i} ID",
                        label_visibility = "collapsed",
                        value=f"{arrival_cage_number}_{i}"
                    )
            elif auto_generate == "Manually Entered":
                cola, colb, colc = st.columns([0.8,3.8,1.2], vertical_alignment="center")
                id_loc = None
                with cola:
                    st.caption("Mouse ID")

                with colb:
                    mouse_id_num = st.text_input(
                        f"Mouse {i} ID",
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

                mouse_id_locs.append(mouse_id_loc)
                mouse_id_nums.append(mouse_id_num)
            else:
                mouse_id_locs = []
                mouse_id_num = ""

            if genotype_label == "Varies by Mouse":
                cola, colb = st.columns([0.8,5.2],vertical_alignment="center")
                with cola:
                    st.caption("Genotype")
                with colb:
                    mouse_genotype_label = st.selectbox(
                        f"genotype {i}",
                        options = genotype_labels,
                        index = None,
                        label_visibility = "collapsed",
                    )

            cola, colb = st.columns([0.8,5.2])
            with cola:
                st.caption("")
                st.caption("Notes")
            with colb:
                mouse_note = st.text_area(
                    "Notes",
                    key = f"note {i}",
                    label_visibility="collapsed",
                )

            mouse_ids.append(f"{redcap_utils.dob_to_yymm(str(dob))}:{mouse_id_num}")
            mouse_notes.append(order_notes + "\n\n" + mouse_note)

            if genotype_label == "Varies by Mouse" and mouse_genotype_label != None:
                genotype = redcap_utils.genotype_label_to_variable(mouse_genotype_label)
            else:
                genotype = redcap_utils.genotype_label_to_variable(genotype_label)

            mouse_genotypes.append(genotype)
            
            if i > 0 and i < number_of_mice:
                st.divider()

    st.divider()

    submission_button = st.button("Submit Records to RedCap", type = "primary")

    # --------------------------------------------------
    # Redcap Submission
    # --------------------------------------------------

    if submission_button:

        errors = []

        for i in range(number_of_mice):
            if mouse_ids[i] == "":
                errors.append("Mouse ID numbers required for all individual mice")
        
        if arrival_cage_number == "":
            errors.append("Arrival Cage number is required.")

        if not sex:
            errors.append("Sex is required.")

        if not genotype_label:
            errors.append("Genotype is required.")

        if not arrival_date:
            errors.append("Arrival date is required.")

        if not dob:
            errors.append("Date of birth is required.")

        if errors:
            with status_container:
                st.write("Please fix the following issues:")
                for error in errors:
                    st.error(f"{error}")
                st.divider()

        if not errors:

            with status_container:
                for i in range(number_of_mice):
                    fields = {
                        "mouse_ear_id_type": "tag" if auto_generate == "Manually Entered" else "none",
                        "mouse_ear_id": mouse_id_nums[i] if auto_generate == "Manually Entered" else "",
                        "mouse_ear_id_location": mouse_id_locs[i].lower() if auto_generate == "Manually Entered" else "",
                        "mouse_protocol": "2024",
                        "mouse_sex": sex.lower(),
                        "mouse_cage_number": arrival_cage_number,
                        "mouse_genotype": mouse_genotypes[i],
                        "mouse_arrival_date": arrival_date.strftime("%Y-%m-%d"),
                        "mouse_litter_id": litter_id,
                        "mouse_dob": dob.strftime("%Y-%m-%d"),
                        "mouse_source": transfer_lab.lower(),
                        "mouse_notes": mouse_notes[i],
                        "mouse_info_complete": "0",
                        }
                    redcap_utils.create_new_mouse_record(mouse_ids[i], fields)
                    st.success(f"Mouse  {mouse_ids[i]} transferred succesfully")
                st.info("Returning you to Dashboard")
                st.divider()
            time.sleep(2)
            st.switch_page("pages/dashboard.py")