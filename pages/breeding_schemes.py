import streamlit as st
import pandas as pd
import time
import redcap_utils

st.subheader("Breeding Schemes")
st.markdown("")

with st.sidebar:
    status_container = st.container()

# --------------------------------------------------
# Litter Information
# --------------------------------------------------

upload_csv = pd.read_csv("genotypes.csv",dtype="str")

genotype_df = upload_csv

tab_names = [
    "Wild Type",
    "Cre Lines",
    "Fmr1 Core Lines",
    "Fmr1 Cre Lines",
    "Pvalb-tdTomato Lines",
    "OPN1 Lines",
    "Reporter Lines",
    ]

tabs = st.tabs(tab_names,width="stretch",on_change="rerun")

genotype_options = pd.DataFrame([])

if tabs[0].open:
    genotype_options = pd.DataFrame(
        [{"name": "C57BL/6J x C57BL/6J", "id": 0}
        ]
    )

if tabs[1].open:
    genotype_options = pd.DataFrame([
        {"name": "Gad2-cre(+/-) x C57BL/6J", "id": 3},
        {"name": "Gad2-cre(+/+) x C57BL/6J", "id": 19},
        {"name": "Pvalb-cre(+/-) x C57BL/6J", "id": 2},
        {"name": "Pvalb-cre(+/+) x C57BL/6J", "id": 18},
        {"name": "Six3-cre(+/-) x C57BL/6J", "id": 4},
    ])

if tabs[2].open:
    genotype_options = pd.DataFrame([
        {"name": "C57BL/6J x Fmr1(+/-)", "id": 1},
        {"name": "C57BL/6J x Fmr1(-/-)", "id": 16},
        {"name": "C57BL/6J x Fmr1(flox/flox)", "id": 8},
        {"name": "Fmr1(flox/y) x Fmr1(flox/flox)", "id": 9},
    ])

if tabs[3].open:
    genotype_options = pd.DataFrame([
        {"name": "Gad2-cre(+/-) x Fmr1(flox/flox)", "id": 12},
        {"name": "Pvalb-cre(+/-) x Fmr1(flox/flox)", "id": 11},
        {"name": "Six3-cre(+) x Fmr1(flox/flox)", "id": 10}
    ])

if tabs[4].open:
    genotype_options = pd.DataFrame([
        {"name": "Fmr1(-/y) x Pvalb-tdTomato(+)", "id": 5},
        {"name": "Fmr1(-/y); Pvalb-tdTomato(+) x C57BL/6J", "id": 6},
        {"name": "C57BL/6J x Fmr1(+/-); Pvalb-tdTomato(+)", "id": 7},
    ])

if tabs[5].open:
    genotype_options = pd.DataFrame([
        {"name": "OPN1(MW/y) x OPN1_LW_MW", "id": 14},
        {"name": "OPN1(SW/+) x OPN1(SW/+)", "id": 15},
    ])

if tabs[6].open:
    genotype_options = pd.DataFrame([
        {"name": "C57BL/6J x Ai148(+/+)", "id": 17},
        {"name": "Gad2-cre(+/+) x Ai148(+/+)", "id": 22},
        {"name": "Gad2-cre(+/-) x Ai14(+/+)", "id": 13},
        {"name": "Pvalb-cre(+/-) x Ai14(+/+)", "id": 21},
        {"name": "Six3-cre(+) x Ai14(+/+)", "id": 20},
    ])

for i in range(len(genotype_options)):
    index = genotype_options.loc[i,"id"]

    active = True if genotype_df.loc[index,"Status"] == "True" else False
    if active:
        text_color = "violet"
        deactivated = False
    else:
        text_color = "gray"
        deactivated = True

    expander = st.expander(
        f":{text_color}[**{genotype_df.loc[index,"Breeding Cross"]}**]",
    )

    with expander:
        st.markdown("")
        col1, col2 = st.columns([2,0.32], vertical_alignment="center")
        with col2:
            active = st.toggle(
                f"Activate_{i}{index}",
                label_visibility = "collapsed",
                value = True if genotype_df.loc[index,"Status"] == "True" else False
            )
        if active:
            text_color = "violet"
            deactivated = False
        else:
            text_color = "gray"
            deactivated = True
        with col1:
            count = redcap_utils.count_breeding(str(genotype_df.loc[index,"Breeding Cross"]))
            st.markdown(f":primary-background[:{text_color}[**{genotype_df.loc[index,"Breeding Cross"]}** :small[-- {count} Current Cages]]]")

        col1, col2, col3 = st.columns([0.2,2,0.2])
        with col2:
            cola, colb, colc = st.columns([1,1,1.2])
            with cola:
                st.caption("")
                st.write(f":{text_color}[:small[:material/male: Sire Genotype: {genotype_df.loc[index,"Sire Genotype"]}]]")
            with colb:
                st.caption("")
                st.write(f":{text_color}[:small[:material/female: Dame Genotype: {genotype_df.loc[index,"Dame Genotype"]}]]")
            with colc:
                st.caption("")
                st.write(f":{text_color}[:small[:material/join: Cross: {genotype_df.loc[index,"Breeding Cross"]}]]")

            general_notes = st.text_input(
                f"General Notes_{i}{index}",
                label_visibility = "collapsed",
                value = genotype_df.loc[index,"General Notes"] if (genotype_df.loc[index,"General Notes"] != "none") else "",
                placeholder = "Optional notes about breeding scheme",
                disabled = deactivated
            )

            st.divider()
            cola, colb = st.columns(2)
            with cola:
                male_offspring = genotype_df.loc[index,"Male Genotypes"]
                male_offspring_text = male_offspring
                if "|" in male_offspring:
                    split = [
                        genotype.strip()
                        for genotype in male_offspring.split("|")
                        if genotype.strip() != ""
                    ]
                    male_offspring_text = "\n".join(split)

                male_offspring_new = st.text_area(
                    ":material/male: Male Offspring Genotypes",
                    key = f"male_offspring_{i}{index}",
                    value = male_offspring_text,
                    disabled = deactivated,
                    height="content"
                )
                male_genotypes = male_offspring_new.replace("\n","|")
            
            with colb:
                female_offspring = genotype_df.loc[index,"Female Genotypes"]
                female_offspring_text = female_offspring
                if "|" in female_offspring:
                    split = [
                        genotype.strip()
                        for genotype in female_offspring.split("|")
                        if genotype.strip() != ""
                    ]
                    female_offspring_text = "\n".join(split)

                female_offspring_new = st.text_area(
                    ":material/female: Female Offspring Genotypes",
                    key = f"female_offspring_{i}{index}",
                    value = female_offspring_text,
                    disabled = deactivated,
                    height="content"
                )
                female_genotypes = female_offspring_new.replace("\n","|")

            st.divider()

            cola, colb = st.columns([4,0.7], vertical_alignment = "center")
            with cola:
                weaning_notes = st.text_input(
                    "Weaning Notes",
                    key = f"weaning_notes_{i}{index}",
                    label_visibility = "collapsed",
                    value = genotype_df.loc[index,"Weaning Notes"] if (genotype_df.loc[index,"Weaning Notes"] != "none") else "",
                    placeholder = "Optional notes about weaning",
                    disabled = deactivated
                )
            with colb:
                st.markdown(f":{text_color}[:small[:material/pest_control_rodent: Weaning]]",text_alignment = "right")
            
            cola, colb = st.columns([4,0.7], vertical_alignment = "center")
            with cola:
                genotyping_notes = st.text_input(
                    "Genotyping Notes",
                    key = f"genotyping_notes_{i}{index}",
                    label_visibility = "collapsed",
                    value = genotype_df.loc[index,"Genotyping Notes"] if (genotype_df.loc[index,"Genotyping Notes"] != "none") else "",
                    placeholder = "Optional notes about genotyping",
                    disabled = deactivated
                )
            with colb:
                st.markdown(f":{text_color}[:small[:material/genetics: Genotyping]]",text_alignment = "right")

            cola, colb = st.columns([4,0.7], vertical_alignment = "center")
            with cola:
                experiment_notes = st.text_input(
                    "Experiment Notes",
                    key = f"experiment_notes_{i}{index}",
                    label_visibility = "collapsed",
                    value = genotype_df.loc[index,"Experiment Notes"] if (genotype_df.loc[index,"Experiment Notes"] != "none") else "",
                    placeholder = "Optional notes about experimental usage",
                    disabled = deactivated
                )
            with colb:
                st.markdown(f":{text_color}[:small[:material/biotech: Experiments]]",text_alignment = "right")

            if (
                genotype_df.loc[index, "Male Genotypes"] == male_genotypes and
                genotype_df.loc[index, "Female Genotypes"] == female_genotypes and
                genotype_df.loc[index, "Genotyping Notes"] == genotyping_notes.strip() if genotyping_notes != "" else "none" and
                genotype_df.loc[index, "Weaning Notes"] == weaning_notes.strip() if weaning_notes != "" else "none" and
                genotype_df.loc[index, "Experiment Notes"] == experiment_notes.strip() if experiment_notes != "" else "none" and
                genotype_df.loc[index, "General Notes"] == general_notes.strip() if general_notes != "" else "none"
            ):
                save = False
            else:
                st.divider()
                save = st.button(
                    f":{text_color}[:material/save: Save Genotype Updates]",
                    key = f"save_button_{i}{index}",
                    type = "primary"
                )

            if save:
                genotype_df.loc[index, "Status"] == str(active)
                genotype_df.loc[index, "Male Genotypes"] = male_genotypes
                genotype_df.loc[index, "Female Genotypes"] = female_genotypes
                genotype_df.loc[index, "Genotyping Notes"] = genotyping_notes.strip() if genotyping_notes != "" else "none"
                genotype_df.loc[index, "Weaning Notes"] = weaning_notes.strip() if weaning_notes != "" else "none"
                genotype_df.loc[index, "Experiment Notes"] = experiment_notes.strip() if experiment_notes != "" else "none"
                genotype_df.loc[index, "General Notes"] = general_notes.strip() if general_notes != "" else "none"
                
                genotype_df.to_csv("genotypes.csv", index=False)

                with status_container:
                    st.success("Genotype Information Updated")
                    time.sleep(2)
                    st.rerun()


csv = genotype_df.to_csv().encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="genotypes.csv",
    mime="text/csv",
    icon=":material/download:",
    type = "tertiary"
)