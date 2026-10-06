import streamlit as st
import pandas as pd
import redcap_utils
from datetime import date, timedelta
import math

def get_request_timing_category(request_date):

    if pd.isna(request_date):
        return "Later"

    request_date = pd.to_datetime(request_date, errors="coerce")

    if pd.isna(request_date):
        return "Later"

    request_date = request_date.date()
    today = date.today()
    seven_days = today + timedelta(days=7)

    if request_date < today:
        return "Overdue"
    elif request_date == today:
        return "Today"
    elif today < request_date <= seven_days:
        return "Upcoming 7 Days"
    else:
        return "Later"


def display_board(user_df):

    order = [
        "Today",
        "Upcoming 7 Days",
        "Later",
        "Overdue",
    ]

    category_colors = {
        "Today": "#5A755F",
        "Upcoming 7 Days": "#BCC9B7",
        "Later": "#ABA5B6",
        "Overdue": "#595365",
    }

    for i in range(len(order)):
        category = order[i]

        category_df = user_df[user_df["request_timing"] == category]
        color = category_colors.get(category, "#999999")

        st.markdown(
            f"""
            <div style="
                background-color: {color};
                color: white;
                padding: 5px;
                border-radius: 10px;
                text-align: center;
                font-weight: 500;
                margin-bottom: 5px;
            ">
                {category}
            </div>
            """,
            unsafe_allow_html=True,
        )
        category_df = category_df.sort_values(
            by="request_experiment_date_dt",
            na_position="last"
        )
        display_cols = [
            "mouse_id",
            "mouse_cage_number",
            "mouse_sex",
            "mouse_age_days",
            "genotype_label",
            "request_flag",
            "request_date",
            "request_notes",
            "request_experiment",
            "request_experiment_date",
            "request_experiment_notes",
        ]
        columns = redcap_utils.get_columns()
        column_ids = columns["id"].tolist()
        column_names = columns["name"].tolist()
    
        column_rename_map = dict(
            zip(column_ids, column_names)
        )
        display_df = category_df[display_cols]
        display_df = display_df.rename(columns=column_rename_map)
        display_df = display_df.rename(columns={"genotype_label": "Genotype"})
        st.dataframe(display_df,hide_index = True)
                
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
        st.metric("Alive Mice", len(current_df))
    with col1:
        st.metric("Total Mice", len(total_df))

    st.divider()
    st.subheader("Reservations")

    detail_container = st.container()

    reserved_df = current_experimental[current_experimental["request_flag"] != "available"]
    reserved_df = reserved_df[reserved_df["request_flag"] != ""]
    reserved_df["request_experiment_date_dt"] = pd.to_datetime(
            reserved_df["request_experiment_date"],
            errors="coerce"
        )
    reserved_df["request_timing"] = reserved_df["request_experiment_date_dt"].apply(
        get_request_timing_category
    )

    users = list(set(reserved_df["request_person"].tolist()))
    for i in range(len(users)):
        users[i] = users[i].replace(" ","").title()
    users = list(set(users))

    cols = [st.columns(1),st.columns(1),st.columns(1)]
    cols[0], cols[1], cols[2] = st.columns(3)
    rows = math.ceil(len(users)/3)

    for j in range(rows):
        for i in range(3):
            container_css = f"""
                <style>
                    .st-key-colorful_container{i}{j}"""""" {
                        background-color: #e8e6ec;
                        border: 0px solid #e8e6ec;
                        padding: 20px;
                        border-radius: 10px;
                    }
                </style>
                """
            st.markdown(container_css,unsafe_allow_html=True)
            if (i+(3*j))<len(users):
                with cols[i]:
                    with st.container(key=f"colorful_container{i}{j}", height=230):
                        user = users[i+(3*j)]
                        cola, colb = st.columns([1.5,1])
                        reserved_df['request_person'] = reserved_df['request_person'].str.title().replace(" ","")
                        user_df = reserved_df[reserved_df["request_person"] == user]
                        upcoming_mice = user_df[user_df["request_timing"].isin(["Today", "Upcoming 7 Days"])]
                        overdue_mice = user_df[user_df["request_timing"] == "Overdue"]
                        with cola:
                            st.markdown(f"##### {user}")
                        with colb:
                            button = st.button(
                                f":small[:gray[View Details | :material/person_search:]]",
                                key = f"button{i}{j}",
                                type="tertiary",)
                        create_cell(user_df)
            if button:
                with detail_container:
                    display_board(user_df)

    st.divider()
    st.subheader("Action Items")

    old_age_threshold_weeks = 18

    tab_old, tab_single, tab_unknown = st.tabs(
        [
            f"Old Mice > {old_age_threshold_weeks} Weeks",
            "Single-Housed Mice",
            "Unknown / Missing Data",
        ]
    )

    old_mice_df = current_df[current_df["mouse_age_weeks"].astype(float) > old_age_threshold_weeks]
    old_mice_df = old_mice_df[old_mice_df["breeding_cage"]==""]

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

        st.write(f"{len(old_display_df)} experimental mice are older than {old_age_threshold_weeks} weeks.")

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
    cage_occupancy_df = cage_occupancy_df[cage_occupancy_df["breeding_cage"]==""]

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
                    "request_flag": "Request Flag",
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

def create_cell(user_df):
    user_df = user_df.sort_values(
        by="request_experiment_date_dt",
        na_position="last"
    )
    mouse = [" "," "," "]
    experiment = [" "," "," "]
    date = [" "," "," "]
    for i in range(min(len(user_df),3)):
        if user_df["request_flag"].iloc[i] == "breeding":
            experiment[i] = "Breeding"
        else:
            experiment[i] = user_df["request_experiment"].iloc[i]
        mouse[i] = user_df["mouse_id"].iloc[i]
        date[i] = user_df["request_experiment_date"].iloc[i].replace("-","")

    overdue_mice = user_df[user_df["request_timing"] == "Overdue"]

    test_html = f"""<p style="font-size: 14px; color: #262730; line-height: 0.4;">Reserved Mice: {str(len(user_df))}</p>
        <p style="font-size: 14px; color: #262730; line-height: 0.4;">Upcoming Experiments:</p>
        <table>
        <tbody>
        <tr style="height: 0px;">
        <td style="font-size: 14px; color: #262730; line-height: 0.5; width: 80px; height: 0px; border: 1px solid #e8e6ec;">{mouse[0] if mouse[0]!= "" else "Unknown"}</td>
        <td style="font-size: 14px; color: #262730; line-height: 0.5; width: 100px; height: 0px; border: 1px solid #e8e6ec;">{experiment[0] if experiment[0]!= "" else "Unknown"}</td>
        <td style="font-size: 14px; color: #262730; line-height: 0.5; width: 100px; height: 0px; border: 1px solid #e8e6ec;">{date[0] if date[0]!= "" else "Unknown"}</td>
        </tr>
        <tr style="height: 0px;">
        <td style="font-size: 14px; color: #262730; line-height: 0.5; width: 80px; height: 0px; border: 1px solid #e8e6ec;">{mouse[1] if mouse[1]!= "" else "Unknown"}</td>
        <td style="font-size: 14px; color: #262730; line-height: 0.5; width: 100px; height: 0px; border: 1px solid #e8e6ec;">{experiment[1] if experiment[1]!= "" else "Unknown"}</td>
        <td style="font-size: 14px; color: #262730; line-height: 0.5; width: 100px; height: 0px; border: 1px solid #e8e6ec;">{date[1] if date[1]!= "" else "Unknown"}</td>
        </tr>
        <tr style="height: 0px;">
        <td style="font-size: 14px; color: #262730; line-height: 0.5; width: 80px; height: 0px; border: 1px solid #e8e6ec;">{mouse[2] if mouse[2]!= "" else "Unknown"}</td>
        <td style="font-size: 14px; color: #262730; line-height: 0.5; width: 100px; height: 0px; border: 1px solid #e8e6ec;">{experiment[2] if experiment[2]!= "" else "Unknown"}</td>
        <td style="font-size: 14px; color: #262730; line-height: 0.5; width: 100px; height: 0px; border: 1px solid #e8e6ec;">{date[2] if date[2]!= "" else "Unknown"}</td>
        </tr>
        </tbody>
        </table>
        <p style="font-size: 14px; color: #262730; line-height: 0.3;">Overdue Experiments: {str(len(overdue_mice))}</p>
        """
    st.markdown(test_html,unsafe_allow_html=True)


