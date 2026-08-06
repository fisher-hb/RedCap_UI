import streamlit as st

# --------------------------------------------------
# Create Overview Dashboard Tab
# --------------------------------------------------

def create_overview(total_df, current_df, current_experimental, current_breeding):
    st.subheader("Dashboard")
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1.2,1.2])
    with col5:
        non_breeding_cages = (current_experimental["mouse_cage_number"])
        st.metric("Current Non-Breeding Cages",non_breeding_cages.nunique()) 
    with col4:
        breeding_cages = (current_breeding["breeding_cage"])
        st.metric("Current Breeding Cages",breeding_cages.nunique()) 
    with col3:
        st.metric("Current Cages",non_breeding_cages.nunique()+breeding_cages.nunique()) 
    with col2:
        st.metric("Current Mice", len(current_df))
    with col1:
        st.metric("Total Mice", len(total_df))

    # --------------------------------------------------
    # Action items / alerts
    # --------------------------------------------------

    st.divider()
    st.subheader("Action Items")

    old_age_threshold_weeks = 22

    tab_old, tab_single, tab_unknown = st.tabs(
        [
            f"Old Mice > {old_age_threshold_weeks} Weeks",
            "Single-Housed Mice",
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
                "request_flag",
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
                    "request_flag": "Flag",
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
                "request_flag",
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
                    "request_flag": "Flag",
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

