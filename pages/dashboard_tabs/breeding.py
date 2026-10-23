import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import redcap_utils
from datetime import date, datetime

# --------------------------------------------------
# Create Cages Dashboard Tab
# --------------------------------------------------

def create_breeding(current_breeding, all_breeding, genotype_groups):

    st.subheader("Dashboard")
    breeding_summary_df = pd.DataFrame()

    if current_breeding.empty:
        st.info("No breeding information rows found.")
    else:
        current_breeding_df = current_breeding

        breeding_cages = sorted(
            current_breeding_df["breeding_cage"].unique().tolist()
        )

        breeding_records = []

        for cage in breeding_cages:
            cage_mice = current_breeding[current_breeding["breeding_cage"] == cage]

            males = cage_mice[(cage_mice["mouse_sex"]) == "male"]
            females = cage_mice[(cage_mice["mouse_sex"]) == "female"]

            sire_genotype = males.iloc[0]["genotype_label"]
            dame_genotype = females.iloc[0]["genotype_label"]

            parental_cross = f"{sire_genotype} x {dame_genotype}"

            breeding_records.append(
                {
                    "breeding_cage": cage,
                    "parental_cross": parental_cross,
                    "sire_id": males.iloc[0]["mouse_id"],
                    "dame_id": females.iloc[0]["mouse_id"],
                }
            )

        breeding_summary_df = pd.DataFrame(breeding_records)

        if breeding_summary_df.empty:
            st.info("No current breeding cages found.")
        else:
            breeding_cross_counts_df = (
                breeding_summary_df
                .groupby("parental_cross")
                .size()
                .reset_index(name="breeding_cage_count")
                .sort_values("parental_cross")
            )

            breed_col1, breed_col2, breed_col3 = st.columns(3)

            with breed_col1:
                st.metric("Current Breeding Cages", breeding_summary_df["breeding_cage"].nunique())

            with breed_col2:
                st.metric("Unique Parental Crosses", breeding_cross_counts_df["parental_cross"].nunique())

            with breed_col3:
                cages_missing_parent = len(
                    breeding_summary_df[
                        breeding_summary_df["parental_cross"].str.contains("Unknown", na=False)
                    ]
                )
                st.metric("Cages Missing Parent Info", cages_missing_parent)

            st.divider()

            st.subheader("Current Breeding Cages by Parental Cross")
            fig = redcap_utils.plot_bar(
                breeding_cross_counts_df,
                x_col="parental_cross",
                y_col="breeding_cage_count",
                x_label="",
                y_label="Number of Breeding Cages",
                color = "#7D869C",
                figsize = [12,4],
                rotate_labels=True,
            )

            st.pyplot(fig)
            plt.close(fig)

    st.divider()
    st.subheader("Breeding Statistics by Genotype")
    breeding_cages_2 = sorted(all_breeding["breeding_cage"].unique().tolist())
    breeding_records = []

    for cage in breeding_cages_2:
        cage_mice = all_breeding[all_breeding["breeding_cage"] == cage]

        if len(cage_mice)>1:

            sire_genotype = cage_mice[(cage_mice["mouse_sex"]) == "male"].iloc[0]["genotype_label"]
            dame_genotype = cage_mice[(cage_mice["mouse_sex"]) == "female"].iloc[0]["genotype_label"]

            parental_cross = f"{sire_genotype} x {dame_genotype}"

            breeding_records.append(
                {
                    "parental_cross": parental_cross,
                    "dame_id": cage_mice[(cage_mice["mouse_sex"]) == "female"].iloc[0]["mouse_id"],
                }
            )

    breeding_records = pd.DataFrame(breeding_records)

    cross_counts = (
                    breeding_records
                    .groupby("parental_cross")
                    .size()
                    .reset_index(name="breeding_cage_count")
                    .sort_values("parental_cross")
                )

    full_df = st.session_state["redcap_df"].copy()
    full_df = full_df[(full_df["redcap_repeat_instrument"])!="experiment_info"]

    stats_table = []
    stats = []

    for i in range(len(cross_counts)):
        cross = cross_counts["parental_cross"].iloc[i]
        dames = breeding_records[(breeding_records["parental_cross"]) == cross]
        for j in range(len(dames)):
            record = full_df[(full_df["mouse_id"]) == dames["dame_id"].iloc[j]]
            litters = len(record)-1
            # start = datetime.strptime(record["breeding_date_created"].iloc[0], "%Y-%m-%d").date() if record["breeding_date_created"].iloc[0] != "" else ""
            start = datetime.strptime(record["mouse_dob"].iloc[0], "%Y-%m-%d").date() if record["mouse_dob"].iloc[0] != "" else ""
            sacced = True if record["mouse_sac_date"].iloc[0] != "" else False
            cage = record["breeding_cage"].iloc[0] if record["breeding_cage"].iloc[0] != "" else "False"
            males = 0
            females = 0

            end = date.today()
            for k in range(litters):
                weaned_m = int(record["litter_wean_num_m"].iloc[k+1]) if record["litter_wean_num_m"].iloc[k+1] != "" else 0
                sacced_m = int(record["litter_sac_num_m"].iloc[k+1]) if record["litter_sac_num_m"].iloc[k+1] != "" else 0
                weaned_f = int(record["litter_wean_num_f"].iloc[k+1]) if record["litter_wean_num_f"].iloc[k+1] != "" else 0
                sacced_f = int(record["litter_sac_num_f"].iloc[k+1]) if record["litter_sac_num_f"].iloc[k+1] != "" else 0
                males = males + sacced_m + weaned_m
                females = females + sacced_f + weaned_f
                if sacced:
                    end = datetime.strptime(record["litter_dob"].iloc[k+1], "%Y-%m-%d").date()

            time = (end-start).days

            if sacced:
                stats.append(
                    {
                        "cross": cross,
                        "Cage Number": cage,
                        "Total Litters": litters,
                        "Total Male Pups": males,
                        "Total Female Pups": females,
                        "start": start,
                        "end": end,
                        "Breeding Time (Days)": time,
                        "status": "sacced"
                    }
                )
            else:
                stats.append(
                    {
                        "cross": cross,
                        "Cage Number": cage,
                        "Total Litters": litters,
                        "Total Male Pups": males,
                        "Total Female Pups": females,
                        "start": start,
                        "end": end,
                        "Breeding Time (Days)": time,
                        "status": "current"
                    }
                )

    genotype_groups = {
        "Wild Type": [
            "C57BL/6J x C57BL/6J"
            ],
        "Cre Lines": [
            "Gad2-cre(+/+) x C57BL/6J",
            "Gad2-cre(+/-) x C57BL/6J",
            "Pvalb-cre(+/+) x C57BL/6J",
            "Pvalb-cre(+/-) x C57BL/6J",
            "Pvalb-cre(+/-) x Pvalb-cre(+/-)",
            "Six3-cre(+) x C57BL/6J",
            "Six3-cre(+) x Six3-cre(+)",
            ],
        "Fmr1 Core Lines": [
            "C57BL/6J x Fmr1(+/-)",
            "C57BL/6J x Fmr1(-/-)",
            "C57BL/6J x Fmr1(flox/flox)",
            "Fmr1(flox/y) x Fmr1(flox/flox)",
            ],
        "Fmr1 Cre Lines": [
            "Gad2-cre(+/-) x Fmr1(flox/flox)",
            "Pvalb-cre(+/-) x Fmr1(flox/flox)",
            "Six3-cre(+) x Fmr1(flox/flox)",
            ],
        "OPN1 Lines": [
            "OPN1(LW/+) x OPN1(LW/MW)",
            "OPN1(MW/y) x OPN1(LW/MW)",
            "OPN1(SW/+) x OPN1(SW/+)",
            ],
        "Pvalb-tdTomato Lines": [
            "C57BL/6J x Fmr1(+/-); Pvalb-tdTomato(+)",
            "Fmr1(-/y) x Fmr1(+/+); Pvalb-tdTomato(+)",
            "Fmr1(-/y) x Pvalb-tdTomato(+)",
            "Fmr1(-/y); Pvalb-tdTomato(+) x C57BL/6J",
            ],
        "Ai Reporter Lines": [
            "C57BL/6J x Ai148(+)",
            "Gad2-cre(+/+) x Ai148(+)",
            "Gad2-cre(+/-) x Ai14(+/+)",
            "Pvalb-cre(+/-) x Ai14(+/+)",
            "Six3-cre(+) x Ai14(+/+)",
        ]
    }

    cross_statistics = pd.DataFrame(stats)

    for i, (group_name, group_cross) in enumerate(genotype_groups.items()):
        group_expander = st.expander(
            f"**{group_name}**"
        )
          
        with group_expander:
            for j in range(len(group_cross)):

                display = cross_statistics[(cross_statistics["cross"]) == group_cross[j]]
                display_sacced = display[(display["status"]) == "sacced"]
                display_current = display[(display["status"]) == "current"]

                total_pups = pd.to_numeric(display_sacced["Total Male Pups"]).sum() + pd.to_numeric(display_sacced["Total Female Pups"]).sum()

                st.markdown(f"**{group_cross[j]}**")
                cola, colb, colc = st.columns([0.5,7,3])
                with colb:
                    if len(display_sacced)>0:
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Litters", f"{pd.to_numeric(display_sacced["Total Litters"]).mean():.2f}")
                        col2.metric("Pups per Litter", f"{total_pups/pd.to_numeric(display_sacced["Total Litters"]).sum():.2f}")
                        col3.metric("Male/Female (%)",f"{pd.to_numeric(display_sacced["Total Male Pups"]).sum()/(0.01*total_pups):.0f}/{pd.to_numeric(display_sacced["Total Female Pups"]).sum()/(0.01*total_pups):.0f}")
                        col4.metric("Time Breeding (Days)",f"{pd.to_numeric(display_sacced["Breeding Time (Days)"]).mean():.2f}")
                    else:
                        st.markdown(f":small[No generalized statistics are available for this cross]")
                    if len(display_current)>0:
                        with st.expander(f"Current Cages: {len(display_current)}"):
                            st.dataframe(display_current[["Cage Number","Total Litters","Total Male Pups","Total Female Pups","Breeding Time (Days)"]], hide_index = True)
                    if len(display_sacced)>0:
                        with st.expander(f"Former Cages: {len(display_sacced)}"):
                            st.dataframe(display_sacced[["Cage Number","Total Litters","Total Male Pups","Total Female Pups","Breeding Time (Days)"]], hide_index = True)
                if j < len(group_cross)-1:
                    st.divider()