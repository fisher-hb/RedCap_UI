import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import redcap_utils

# --------------------------------------------------
# Create Cages Dashboard Tab
# --------------------------------------------------

def create_breeding(current_breeding):

    st.subheader("Dashboard")
    breeding_summary_df = pd.DataFrame()

    if current_breeding.empty:
        st.info("No breeding information rows found.")
    else:
        if "breeding_separated_date" in current_breeding.columns:
            current_breeding_df = current_breeding[
                current_breeding["breeding_separated_date"].isna()
                | (current_breeding["breeding_separated_date"].astype(str).str.strip() == "")
            ].copy()

        breeding_cages = sorted(
            current_breeding_df["breeding_cage"].dropna().unique().tolist()
        )

        breeding_records = []

        for cage in breeding_cages:
            cage_mice = current_breeding[
                current_breeding["breeding_cage"] == cage
            ].copy()

            males = cage_mice[(cage_mice["mouse_sex"]).str.lower() == "male"]

            females = cage_mice[(cage_mice["mouse_sex"]).str.lower() == "female"]

            sire_genotype = (
                males.iloc[0]["genotype_label"]
                if len(males) > 0
                else "Unknown sire"
            )

            dame_genotype = (
                females.iloc[0]["genotype_label"]
                if len(females) > 0
                else "Unknown dame"
            )

            parental_cross = f"{sire_genotype} x {dame_genotype}"

            breeding_records.append(
                {
                    "breeding_cage": cage,
                    "parental_cross": parental_cross,
                    "sire_id": males.iloc[0]["mouse_id"] if len(males) > 0 else "",
                    "dame_id": females.iloc[0]["mouse_id"] if len(females) > 0 else "",
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
                st.metric("Current Breeding Cages", len(breeding_summary_df))

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

            st.subheader("Breeding Cages by Parental Cross")
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

            with st.expander("View Parental Cross Details", expanded=False):
                st.dataframe(
                    breeding_summary_df.rename(
                        columns={
                            "breeding_cage": "Breeding Cage",
                            "parental_cross": "Parental Cross",
                            "sire_id": "Sire ID",
                            "dame_id": "Dame ID",
                            "num_alive_mice_in_cage": "Alive Mice in Cage",
                            "num_males": "Males",
                            "num_females": "Females",
                        }
                    ),
                    hide_index=True,
                    width="stretch",
                )