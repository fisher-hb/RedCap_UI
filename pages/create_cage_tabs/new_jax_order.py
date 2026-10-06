import streamlit as st
import pandas as pd
import redcap_utils
import time
from datetime import datetime

def new_jax_order():

    st.markdown("")
    st.subheader("New Jackson Laboratory Cage Order")
    st.markdown("")

    with st.sidebar:
        status_container = st.container()

    # --------------------------------------------------
    # Cage order form
    # --------------------------------------------------

    upload_order = st.file_uploader(
        "Upload Order Information (Optional)", 
        accept_multiple_files=False, 
        type="csv",
    )

    if upload_order:
        order_df = pd.read_csv(upload_order)

        num_input = order_df.loc[0,"Number of Mice"]
        sex_input = order_df.loc[0,"Sex of Mice"]
        genotype_input = order_df.loc[0,"Genotype"]
        strain_input = order_df.loc[0,"Strain"]
        link_input = order_df.loc[0,"Link"]
        id_input = order_df.loc[0,"Order ID"]
        notes_input = order_df.loc[0,"Notes"]

    st.divider()

    col1, col2 = st.columns([1.2,1], gap="medium")

    with col1:

        cola, colb = st.columns([0.6,3],vertical_alignment="center")
        with cola:
            st.markdown(f":small[Mice #]")
            st.markdown("")
            st.markdown(f":small[Sex of Mice]")
            st.markdown("")
            st.markdown(f":small[Genotype]")
        with colb:
            number_of_mice = st.number_input(
                "Number of Mice",
                value= num_input if upload_order else 1,
                disabled = True if upload_order else False,
                label_visibility = "collapsed",
            )
            number_of_mice = int(number_of_mice)

            genotype_choices = redcap_utils.get_genotypes()
            genotype_labels = genotype_choices["label"]

            if upload_order:
                sex = st.text_input(
                    "Sex of Mice",
                    value = sex_input,
                    disabled = True,
                    label_visibility = "collapsed",
                )
                genotype_label = st.text_input(
                    "Genotype",
                    value = genotype_input,
                    disabled = True,
                    label_visibility = "collapsed",
                )
            else:
                sex = st.selectbox(
                    "Sex of Mice",
                    options=["Male", "Female"],
                    index = None,
                    label_visibility = "collapsed",
                )
                genotype_label = st.selectbox(
                    "Genotype",
                    options = genotype_labels,
                    index = None,
                    label_visibility = "collapsed",
                )

            genotype = ""
            if genotype_label != None:
                genotype = redcap_utils.genotype_label_to_variable(genotype_label)

        cola, colb = st.columns([0.6,3],vertical_alignment="center")
        with cola:
            st.markdown(f":small[Strain #]")
            st.markdown("")
            st.markdown(f":small[Link]")
        with colb:
            strain = st.text_input(
                "Strain",
                placeholder = "Example: 000664",
                value = strain_input if upload_order else "",
                disabled = True if upload_order else False,
                label_visibility = "collapsed",
            )

            link = st.text_input(
                    "Link",
                    placeholder="Example: https://www.jax.org/strain/000664",
                    value = link_input if upload_order else "",
                    disabled = True if upload_order else False,
                    label_visibility = "collapsed",
                )

    with col2:
        cola, colb = st.columns([0.7,3],vertical_alignment="center")
        with cola:
            st.markdown(f":small[Order ID]")
        with colb:
            order_id = st.text_input(
                    "Order ID",
                    placeholder="Example: 44484",
                    value = id_input if upload_order else "",
                    disabled = True if upload_order else False,
                    label_visibility = "collapsed",
                )

        order_notes = st.text_area(
            "Order Notes",
            placeholder="Optional notes about this cage order.",
            value = notes_input if upload_order else "",
            height = "stretch",
            disabled = True if upload_order else False,
            label_visibility = "collapsed",
        )

        order_download = pd.DataFrame(
            [
                {"Number of Mice": number_of_mice, 
                "Sex of Mice": sex, 
                "Genotype": genotype_label, 
                "Strain": strain,
                "Link": link, 
                "Order ID": order_id,
                "Notes": order_notes},
            ]
        )
    
        csv = order_download.to_csv().encode("utf-8")
        today = datetime.now().strftime("%Y%m%d")

        st.download_button(
            label="Download Order Details",
            data=csv,
            file_name=f"JAX_Order_{today}.csv",
            icon=":material/download:",
            disabled = True if upload_order else False,
            width="stretch"
        )

        full_notes = f"Link: " + link + "\n\nStrain: " + strain + "\n\nOrder ID: " + order_id + "\n\n" + order_notes

    # --------------------------------------------------
    # Mouse Information
    # --------------------------------------------------

    st.divider()
    st.subheader("Mouse Information")
    st.markdown("")

    col1, col2 = st.columns([2,3], border=True)

    with col1:

        arrival_date = st.date_input(
            "Date of arrival",
            format = "YYYY-MM-DD",
        )   

        litter_id = st.text_input(
            "Litter ID",
            placeholder="Example: JAX_41670",
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

            cola, colb = st.columns([0.8,5.2])
            with cola:
                st.caption("Notes")
            with colb:
                mouse_note = st.text_area(
                    "Notes",
                    key = f"note {i}",
                    label_visibility="collapsed",
                )

            mouse_ids.append(f"{redcap_utils.dob_to_yymm(str(dob))}:{mouse_id_num}")
            mouse_notes.append(f"Link: " + link + "\n\nStrain: " + strain + "\n\n" + order_notes + "\n\n" + mouse_note)
            
            if i > 0 and i < number_of_mice:
                st.divider()

    st.divider()

    # --------------------------------------------------
    # Prepare Records for Export
    # --------------------------------------------------
    saved_orders_df = pd.read_csv("cage_orders.csv")
    index = len(saved_orders_df)

    saved_orders_df.loc[index, "Number of Mice"] = number_of_mice
    saved_orders_df.loc[index, "Sex of Mice"] = sex if sex else ""
    saved_orders_df.loc[index, "Genotype"] = genotype_label
    # saved_orders_df.loc[index, "Strain Number"] = str(strain) if strain else ""
    saved_orders_df.loc[index, "Link"] = link
    # saved_orders_df.loc[index, "Order ID"] = order_id
    saved_orders_df.loc[index, "Order Notes"] = order_notes
    saved_orders_df.loc[index, "Arrival Date"] = arrival_date.strftime("%Y-%m-%d")
    # saved_orders_df.loc[index, "Arrival Cage"] = arrival_cage_number
    saved_orders_df.loc[index, "Date of Birth"] = dob.strftime("%Y-%m-%d")
    saved_orders_df.loc[index, "Litter ID"] = litter_id
    saved_orders_df.loc[index, "Mouse IDs"] = ", ".join(mouse_ids)

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

        if not genotype:
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

            saved_orders_df.to_csv("cage_orders.csv", index=False)

            with status_container:
                for i in range(number_of_mice):
                    fields = {
                        "mouse_ear_id_type": "tag" if auto_generate == "Manually Entered" else "none",
                        "mouse_ear_id": mouse_id_nums[i] if auto_generate == "Manually Entered" else "",
                        "mouse_ear_id_location": mouse_id_locs[i].lower() if auto_generate == "Manually Entered" else "",
                        "mouse_protocol": "2024",
                        "mouse_sex": sex.lower(),
                        "mouse_cage_number": arrival_cage_number,
                        "mouse_genotype": genotype,
                        "mouse_arrival_date": arrival_date.strftime("%Y-%m-%d"),
                        "mouse_litter_id": litter_id,
                        "mouse_dob": dob.strftime("%Y-%m-%d"),
                        "mouse_source": "jax",
                        "mouse_notes": mouse_notes[i],
                        "mouse_info_complete": "0",
                        }
                    redcap_utils.create_new_mouse_record(mouse_ids[i], fields)
                    st.success(f"Mouse  {mouse_ids[i]}  added succesfully")
                st.info("Returning you to Dashboard")
                st.divider()
            time.sleep(2)
            st.switch_page("pages/dashboard.py")