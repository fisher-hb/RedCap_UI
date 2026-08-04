import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import redcap_utils

# --------------------------------------------------
# Import dashboard creation functions
# --------------------------------------------------
import pages.dashboard_tabs.overview as overview
import pages.dashboard_tabs.cages as cages
import pages.dashboard_tabs.breeding as breeding
import pages.dashboard_tabs.mice as mice

# --------------------------------------------------
# Load data
# --------------------------------------------------

df = st.session_state["redcap_df"].copy()
st.session_state["sac"] = pd.DataFrame([])

# --------------------------------------------------
# Prepare core dataframes
# --------------------------------------------------

df = df[(df["redcap_repeat_instrument"].astype(str).str.strip() == "")]

genotype_choices = redcap_utils.get_genotypes()
genotype_rename_map = dict(zip(genotype_choices["variable"], genotype_choices["label"]))
df["genotype_label"] = (df["mouse_genotype"].map(genotype_rename_map))

all_breeding = df[df["breeding_cage"].astype(str).str.strip() != ""]
all_experimental = df[df["breeding_cage"].astype(str).str.strip() == ""]

current_df = df[df["mouse_sac_date"].astype(str).str.strip() == ""]
current_breeding = current_df[current_df["breeding_cage"].astype(str).str.strip() != ""]
current_experimental = current_df[current_df["breeding_cage"].astype(str).str.strip() == ""]

# --------------------------------------------------
# Sidebar options
# --------------------------------------------------

with st.sidebar:
    st.subheader("Dashboard Options")

    alive = st.radio(
        "Show only Alive Mice",
        options = ["Yes","No"],
        horizontal = True,
    )

    st.divider()

# --------------------------------------------------
# Summary metrics
# --------------------------------------------------

overview_tab, cages_tab, mice_tab, breeding_tab = st.tabs(["Overview", "Cages", "Mice", "Breeding"], on_change="rerun")

if overview_tab.open:
    with overview_tab:
        overview.create_overview(current_df, current_experimental, current_breeding)

if cages_tab.open:
    with cages_tab:
        cages.create_cages(current_experimental)

if breeding_tab.open:
    with breeding_tab:
        breeding.create_breeding(current_breeding)

if mice_tab.open:
    with mice_tab:
        mice.create_mice(current_df, current_experimental, current_breeding)



st.subheader("Mouse Source Breakdown")

source_counts_df = (
    df
    .assign(source_label=(df["mouse_source"]))
    .assign(source_label=lambda x: x["source_label"].replace("", "Unknown"))
    .groupby("source_label")
    .size()
    .reset_index(name="count")
    .sort_values("source_label")
)

source_label_map = {
    "bred": "Bred in Lab",
    "jax": "Jackson Laboratory",
    "rederivation": "Rederivation",
    "cryorecovered": "Cryorecovered",
    "hyde": "Hyde Laboratory",
}

source_counts_df["source_label"] = (
    source_counts_df["source_label"]
    .map(source_label_map)
    .fillna(source_counts_df["source_label"])
)

fig = redcap_utils.plot_bar(
    source_counts_df,
    x_col="source_label",
    y_col="count",
    x_label="",
    y_label="Mice",
    color = "#7D869C",
    figsize=[8, 4],
    rotate_labels=True,
)

st.pyplot(fig)
plt.close(fig)


# --------------------------------------------------
# Genotype groups
# --------------------------------------------------

st.divider()
st.subheader("Alive Mice by Genotype Group")

genotype_groups = {
    "Group 1: Ai14 Reporter Crosses": [
        "Ai14(+/-); Gad2-cre(+/-)",
        "Ai14(+/-); Gad2-cre(-/-)",
        "Ai14(+/-); Pvalb-cre(+/-)",
        "Ai14(+/-); Pvalb-cre(-/-)",
        "Ai14(+/-); Six3-cre(+)",
        "Ai14(+/-); Six3-cre(-)",
        "Ai14(+/+)",
        "Gad2-cre(+/-); Ai148(-)",
        "Ai148(+)",
        "Ai148(-)",
    ],
        "Group 2: Cre Lines": [
        "Gad2-cre(+/+)",
        "Gad2-cre(+/-)",
        "Gad2-cre(-/-)",
        "Pvalb-cre(-/-)",
        "Pvalb-cre(?/-)",
        "Pvalb-cre(+/-)",
        "Pvalb-cre(+/+)",
        "Six3-cre(-)",
        "Six3-cre(?/-)",
        "Six3-cre(+)",
    ],
    "Group 2: Fmr1 Core Genotypes": [
        "Fmr1(+/y)",
        "Fmr1(-/y)",
        "Fmr1(+/+)",
        "Fmr1(+/-)",
        "Fmr1(-/-)",
        "Fmr1(flox/y)",
        "Fmr1(flox/+)",
        "Fmr1(flox/flox)",
    ],
    "Group 3: Fmr1 Pvalb-tdTomato": [
        "Pvalb-tdTomato(+/-)",
        "Fmr1(+/y); Pvalb-tdTomato(-)",
        "Fmr1(+/y); Pvalb-tdTomato(+)",
        "Fmr1(-/y); Pvalb-tdTomato(-)",
        "Fmr1(-/y); Pvalb-tdTomato(+)",
        "Fmr1(+/+); Pvalb-tdTomato(-)",
        "Fmr1(+/+); Pvalb-tdTomato(+)",
        "Fmr1(+/-); Pvalb-tdTomato(-)",
        "Fmr1(+/-); Pvalb-tdTomato(+)",
    ],
    "Group 4: Fmr1 flox x Cre": [
        "Fmr1(flox/y); Gad2-cre(+/-)",
        "Fmr1(flox/y); Gad2-cre(-/-)",
        "Fmr1(flox/+); Gad2-cre(+/-)",
        "Fmr1(flox/+); Gad2-cre(-/-)",
        "Fmr1(flox/y); Pvalb-cre(+/-)",
        "Fmr1(flox/y); Pvalb-cre(-/-)",
        "Fmr1(flox/+); Pvalb-cre(+/-)",
        "Fmr1(flox/+); Pvalb-cre(-/-)",
        "Fmr1(flox/y); Six3-cre(+)",
        "Fmr1(flox/y); Six3-cre(-)",
        "Fmr1(flox/+); Six3-cre(+)",
        "Fmr1(flox/+); Six3-cre(-)",
    ],
    "Group 5: OPN1": [
        "OPN1(+/+)",
        "OPN1(LW/+)",
        "OPN1(LW/MW)",
        "OPN1(LW/y)",
        "OPN1(MW/MW)",
        "OPN1(MW/y)",
        "OPN1(SW/+)",
        "OPN1(SW/SW)",
    ],
    "Group 6: Retina Degeneration / Rho": [
        "RD10(-/-)",
        "RD10(+/-)",
        "RhoP23H",
    ],
}

all_genotype_counts_df = (
    current_df
    .groupby("genotype_label")
    .size()
    .reset_index(name="count")
)

genotype_count_map = dict(
    zip(all_genotype_counts_df["genotype_label"], all_genotype_counts_df["count"])
)

for group_name, group_genotypes in genotype_groups.items():

    group_df = pd.DataFrame({
        "genotype": group_genotypes,
        "count": [
            genotype_count_map.get(genotype, 0)
            for genotype in group_genotypes
            ],
        }
    )

    group_total = int(group_df["count"].sum())

    with st.expander(
        f"{group_name} — {group_total} alive mice",
    ):
        if group_df.empty:
            st.info("No alive mice in this genotype group.")
        else:
            st.markdown(group_name)
            fig = redcap_utils.plot_bar(
                group_df,
                x_col="genotype",
                y_col="count",
                x_label="",
                y_label="Mice",
                color = "#7D869C",
                figsize=[8, 4],
                rotate_labels=True,
            )

            st.pyplot(fig)
            plt.close(fig)

            st.dataframe(
                group_df.rename(
                    columns={
                        "genotype": "Genotype",
                        "count": "Alive Mice",
                    }
                ),
                hide_index=True,
                width="stretch",
            )


# --------------------------------------------------
# Action items / alerts
# --------------------------------------------------

st.divider()
st.subheader("Action Items")

old_age_threshold_weeks = 22

tab_old, tab_single, tab_cages, tab_unknown = st.tabs(
    [
        f"Old Mice > {old_age_threshold_weeks} Weeks",
        "Single-Housed Mice",
        "Cage Occupancy",
        "Unknown / Missing Data",
    ]
)

old_mice_df = current_df[current_df["mouse_age_weeks"].astype(float) > old_age_threshold_weeks]

with tab_old:
    old_display_df = old_mice_df[
        [
            "mouse_id",
            "mouse_sex",
            "genotype_label",
            "mouse_cage_number",
            "mouse_dob",
            "mouse_age_weeks",
            "flag",
        ]
    ].copy()

    old_display_df["mouse_age_weeks"] = old_display_df["mouse_age_weeks"].round(1)

    old_display_df = old_display_df.sort_values(
        "mouse_age_weeks",
        ascending=False
    )

    st.write(f"{len(old_display_df)} alive mice are older than {old_age_threshold_weeks} weeks.")

    st.dataframe(
        old_display_df.rename(
            columns={
                "mouse_id": "Mouse ID",
                "mouse_sex": "Sex",
                "genotype_label": "Genotype",
                "mouse_cage_number": "Cage Number",
                "mouse_dob": "Date of Birth",
                "mouse_age_weeks": "Age Weeks",
                "flag": "Flag",
            }
        ),
        hide_index=True,
        width="stretch",
    )

cage_occupancy_df = (current_experimental.assign(cage_number=current_experimental["mouse_cage_number"]))
cage_occupancy_df = cage_occupancy_df[cage_occupancy_df["cage_number"] != ""].copy()

cage_counts_df = (
    cage_occupancy_df
    .groupby("cage_number")
    .size()
    .reset_index(name="mouse_count")
    .sort_values(["mouse_count", "cage_number"], ascending=[False, True])
)

single_cage_numbers = cage_counts_df[cage_counts_df["mouse_count"] == 1]["cage_number"].tolist()

single_housed_df = cage_occupancy_df[cage_occupancy_df["cage_number"].isin(single_cage_numbers)].copy()

with tab_single:
    single_display_df = single_housed_df[
        [
            "mouse_id",
            "mouse_sex",
            "genotype_label",
            "mouse_cage_number",
            "mouse_dob",
            "mouse_age_weeks",
            "flag",
        ]
    ].copy()

    single_display_df["mouse_age_weeks"] = single_display_df["mouse_age_weeks"].round(1)

    single_display_df = single_display_df.sort_values(
        ["mouse_cage_number", "mouse_id"]
    )

    st.write(f"{len(single_display_df)} mice are currently single-housed.")

    st.dataframe(
        single_display_df.rename(
            columns={
                "mouse_id": "Mouse ID",
                "mouse_sex": "Sex",
                "genotype_label": "Genotype",
                "mouse_cage_number": "Cage Number",
                "mouse_dob": "Date of Birth",
                "mouse_age_weeks": "Age Weeks",
                "flag": "Flag",
            }
        ),
        hide_index=True,
        width="stretch",
    )

with tab_cages:
    st.dataframe(
        cage_counts_df.rename(
            columns={
                "cage_number": "Cage Number",
                "mouse_count": "Alive Mice in Cage",
            }
        ),
        hide_index=True,
        width="stretch",
    )


with tab_unknown:
    unknown_df = current_df[
        (current_df["mouse_genotype"] == "")
        | (current_df["mouse_cage_number"] == "")
        | (current_df["mouse_sex"] == "")
        | (current_df["mouse_dob"] == "")
    ].copy()

    st.write(f"{len(unknown_df)} mice have missing genotype, cage, sex, or DOB.")

    if len(unknown_df) > 0:
        st.dataframe(
            unknown_df[
                [
                    "mouse_id",
                    "mouse_sex",
                    "genotype_label",
                    "mouse_cage_number",
                    "mouse_dob",
                    "mouse_litter_id",
                    "mouse_parental_cage",
                ]
            ].rename(
                columns={
                    "mouse_id": "Mouse ID",
                    "mouse_sex": "Sex",
                    "genotype_label": "Genotype",
                    "mouse_cage_number": "Cage Number",
                    "mouse_dob": "Date of Birth",
                    "mouse_litter_id": "Litter ID",
                    "mouse_parental_cage": "Parental Cage",
                }
            ),
            hide_index=True,
            width="stretch",
        )
    else:
        st.success("No missing core data found.")


# --------------------------------------------------
# Optional: ungrouped genotype table
# --------------------------------------------------

st.divider()

with st.expander("All Alive Genotype Counts", expanded=False):
    all_genotype_counts_df = all_genotype_counts_df.sort_values("genotype_label")

    st.dataframe(
        all_genotype_counts_df.rename(
            columns={
                "genotype_label": "Genotype",
                "count": "Alive Mice",
            }
        ),
        hide_index=True,
        width="stretch",
    )