import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import redcap_utils
from datetime import date, datetime

# --------------------------------------------------
# Create Cages Dashboard Tab
# --------------------------------------------------

def create_breeding(current_breeding, all_breeding):

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



    for i in range(len(cross_counts)):
        cross = cross_counts["parental_cross"].iloc[i]
        dames = breeding_records[(breeding_records["parental_cross"]) == cross]
        stats = []
        for j in range(len(dames)):
            record = full_df[(full_df["mouse_id"]) == dames["dame_id"].iloc[j]]
            litters = len(record)-1
            start = datetime.strptime(record["breeding_date_created"].iloc[0], "%Y-%m-%d").date() if record["breeding_date_created"].iloc[0] != "" else ""
            sacced = True if record["mouse_sac_date"].iloc[0] != "" else False
            males = 0
            females = 0
            for k in range(litters):
                weaned_m = int(record["litter_wean_num_m"].iloc[k+1]) if record["litter_wean_num_m"].iloc[k+1] != "" else 0
                sacced_m = int(record["litter_sac_num_m"].iloc[k+1]) if record["litter_sac_num_m"].iloc[k+1] != "" else 0
                weaned_f = int(record["litter_wean_num_f"].iloc[k+1]) if record["litter_wean_num_f"].iloc[k+1] != "" else 0
                sacced_f = int(record["litter_sac_num_f"].iloc[k+1]) if record["litter_sac_num_f"].iloc[k+1] != "" else 0
                males = males + sacced_m + weaned_m
                females = females + sacced_f + weaned_f
                end = datetime.strptime(record["litter_dob"].iloc[k+1], "%Y-%m-%d").date()

            if start != "" and sacced:
                time = (end-start).days
            elif start != "" and not sacced:
                time = (date.today() - start).days
            else:
                time = ""

            stats.append(
                {
                    "litters": litters,
                    "males": males,
                    "females": females,
                    "time": time,
                }
            )
            
        st.markdown(cross)
        cross_statistics = pd.DataFrame(stats)
        average_litters = pd.to_numeric(cross_statistics["litters"]).mean()
        average_males = (pd.to_numeric(cross_statistics["males"]).mean())/average_litters if average_litters != 0 else 0
        average_females = (pd.to_numeric(cross_statistics["females"]).mean())/average_litters if average_litters != 0 else 0
        average_pups = average_males + average_females
        average_time = pd.to_numeric(cross_statistics["time"]).mean()

        st.markdown(f"{average_litters:.2f}")
        st.markdown(f"{average_pups:.2f}")
        st.markdown(f"{average_time:.0f}")
