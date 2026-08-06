import streamlit as st
import pandas as pd
import redcap_utils
import time

st.subheader("Update Mouse Genotypes")

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Cage order form
# --------------------------------------------------

st.divider()

upload_csv = st.file_uploader(
    "Upload CSV from Transnetyx", 
    accept_multiple_files=False, 
    type="csv",
)

sample_ids = []
mouse_ids = []
sample_results = []
genotypes = []
sample_wells = []
sample_notes = []
mouse_notes = []
exclusions = []

if upload_csv:
    genotype_df = pd.read_csv(upload_csv)
    wellplate = genotype_df.loc[0,"WellPlate"]

    mouse_number = len(genotype_df)

    for i, row in genotype_df.iterrows():
        sample_ids.append(str(genotype_df.loc[i,"Sample"]))
        sample_results.append(str(genotype_df.loc[i,"TranslatedResult"]))
        sample_wells.append(str(genotype_df.loc[i,"Well"]))

        parts = []
        for col in genotype_df.columns:
            if pd.isna(row[col]) or str(row[col]).strip() == "":
                continue
            parts.append(f"{col}: {row[col]}")
        line_string = " | ".join(parts)
        sample_notes.append(line_string)


# --------------------------------------------------
# Mouse Information
# --------------------------------------------------

st.divider()
submission_button = False
id_error = False
genotype_error = False

if upload_csv:

    st.subheader(f"Genotyping Results - Wellplate Number: {wellplate}")
    st.markdown("")
    st.markdown("")

    for i, row in genotype_df.iterrows():

        col1, col2 = st.columns([3,1.2])

        with col2:
            redcap_utils.display_wellplate(sample_wells[i])
            st.markdown("")
            st.markdown("")
            exclude = st.toggle(
                "Exclude from Redcap upload?",
                key = f"exclude{i}",
            )
            exclusions.append(exclude)

        with col1:
            cola, colb, colc = st.columns([1.1,3,0.5],vertical_alignment="center")
            with cola:
                st.markdown("Mouse ID:")
            with colb:
                mouse_id = st.text_input(
                    "Mouse ID",
                    key = f"id_{i}",
                    value = sample_ids[i],
                    label_visibility = "collapsed",
                )
                mouse_ids.append(redcap_utils.find_id_from_sample(mouse_id))
            with colc:
                if mouse_ids[i] != None:
                    st.caption(":green[:material/check_circle:]")
                else:
                    st.caption(":red[:material/error:]")
                    if not exclude:
                        id_error = True
                
            cola, colb, colc = st.columns([1.1,3,0.5],vertical_alignment="center")
            with cola:
                st.markdown("Genotype Result:")
            with colb:
                genotype = st.text_input(
                    "Genotype",
                    key = f"genotype_{i}",
                    value = redcap_utils.resolve_sex_specific_genotype(sample_results[i],mouse_ids[i]),
                    label_visibility = "collapsed",
                )
                genotypes.append(redcap_utils.genotype_label_to_variable(genotype))
            with colc:
                df = st.session_state["redcap_df"].copy()
                df = df[(df["redcap_repeat_instrument"].astype(str).str.strip() == "")]
                df = df[df["mouse_id"] == mouse_ids[i]]
                if mouse_ids[i] != None:
                    if df.iloc[0]["mouse_parental_cross"] == "":
                        sex, parental_cross = redcap_utils.get_parental_cross(mouse_ids[i])
                    else:
                        sex = df.iloc[0]["mouse_sex"]
                        parental_cross = df.iloc[0]["mouse_parental_cross"]
                    options = redcap_utils.get_possible_genotypes(parental_cross,sex)
                    options = options.rename(columns={"offspring_genotype": "Genotype Options"})
                    options = options["Genotype Options"]
                    if genotype in options.tolist():
                        st.caption(":green[:material/check_circle:]")
                    else:
                        with st.popover(":grey[:material/help:]",type="tertiary"):
                            st.caption("Invalid genotype for parental cross")
                            st.dataframe(
                                options,
                                hide_index = True,
                                )
                else:
                    st.caption(":red[:material/error:]")
                    if not exclude:
                        genotype_error = True
                        
            sample_note = f'''{sample_notes[i]}'''

            cola, colb, colc = st.columns([1.1,3,0.5],vertical_alignment="center")
            with cola:
                st.markdown("Notes:")

            with colb:
                mouse_note = st.text_area(
                    "Notes",
                    key = f"notes_{i}",
                    label_visibility = "collapsed",
                )
            if mouse_note != "":
                mouse_notes.append(f"{mouse_note}{sample_note}")
            else:
                mouse_notes.append(sample_notes[i])

        st.divider()

    submission_button = st.button(
    "Submit Records to RedCap", 
    type = "primary",
    )

# --------------------------------------------------
# Redcap Submission
# --------------------------------------------------

if submission_button:
    errors = []
    if not upload_csv:
        errors.append("Please upload transnetyx results.")
    if not wellplate:
        errors.append("Wellplate is required.")
    if id_error:
        errors.append("Please verify all mouse IDs")
    if genotype_error:
        errors.append("Please verify all genotype results")
    if errors:
        with status_container:
            st.write("Please fix the following issues:")
            for error in errors:
                st.error(f"{error}")
            st.divider()

    if not errors:
        with status_container:
            for i, row in genotype_df.iterrows():
                if exclusions[i] == False:
                    fields = {
                        "mouse_genotyping": "1",
                        "mouse_genotype": genotypes[i],
                        "mouse_wellplate_number": wellplate,
                        "mouse_genotype_notes": mouse_notes[i]
                        }
                    redcap_utils.create_new_mouse_record(mouse_ids[i], fields)
                    st.success(f"Mouse  {mouse_ids[i]}  added succesfully")
            st.info("Returning you to Dashboard")
        time.sleep(2)
        st.switch_page("pages/dashboard.py")