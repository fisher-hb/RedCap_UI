import streamlit as st
import pandas as pd
import redcap_utils

df = st.session_state["redcap_df"]

breeding_dashboard_df = redcap_utils.build_breeding_dashboard_table(df)

with st.sidebar:
    redcap_utils.show_breeding_status_key()
    st.divider()

# Filters
st.sidebar.header("Breeding Dashboard Filters")

filtered_df = breeding_dashboard_df.copy()

active_only = st.sidebar.radio(
    "Show Active Breeding Cages Only?",
    options=["Yes", "No"],
    horizontal=True,
)

status_options = breeding_dashboard_df["status"].dropna().unique().tolist()
status_options.append("Has Unweaned Litter")

selected_statuses = st.sidebar.multiselect(
    "Status",
    options=status_options,
    default=[],
)

if active_only == "Yes":
    filtered_df = filtered_df[filtered_df["status"] != "No Longer Active"]

if selected_statuses:
    filtered_df = filtered_df[
        filtered_df["status_multi"].apply(
            lambda statuses: any(status in statuses for status in selected_statuses)
            if isinstance(statuses, list) else False
        )
    ]

sort_mode = st.sidebar.selectbox(
    "Sort by",
    options=[
        "Breeding Cage",
        "Status",
        "Parental Cross",
        "Days Since Last Litter",
        "Sire Age",
        "Dame Age",
    ],
    index = 1,
)

# Summary metrics
st.subheader("Summary")

col1, col2, col3, col4, col5 = st.columns(5)

current_df = breeding_dashboard_df[breeding_dashboard_df["status"] != "No Longer Active"]

with col1:
    st.metric("Current Breeding Cages", len(current_df))

with col2:
    st.metric(
        "Litters to Wean",
        int(current_df["pups_ready_to_wean"].sum()),
    )

with col3:

    count_litters = current_df["current_litters"].apply(redcap_utils.has_nonempty_list).sum()

    st.metric(
        "Current Litters",
        count_litters
    )

with col4:
    st.metric(
        "Old Parent Cages",
        int(current_df["parent_old"].sum()),
    )

with col5:
    st.metric(
        "No Recent Litters",
        int(current_df["no_recent_litter"].sum()),
    )

st.divider()

if sort_mode == "Breeding Cage":
    filtered_df = filtered_df.sort_values("breeding_cage")

elif sort_mode == "Parental Cross":
    filtered_df = filtered_df.sort_values("parental_cross")

elif sort_mode == "Status":
    custom_order = [
        "Pups Ready to Wean",
        "Has Unweaned Litter",
        "No Concerns",
        "Parents Getting Old",
        "No Recent Litter",
        "No Longer Active",
    ]
    filtered_df["status"] = pd.Categorical(
        filtered_df["status"],
        categories=custom_order,
        ordered=True,
    )
    filtered_df = filtered_df.sort_values(["status", "breeding_cage"])

elif sort_mode == "Days Since Last Litter":
    filtered_df = filtered_df.sort_values(
        "days_since_last_litter",
        ascending=False,
        na_position="last",
    )

elif sort_mode == "Current Wean Date":
    filtered_df["_current_wean_date_parsed"] = filtered_df["current_wean_date"].apply(redcap_utils.parse_mdy)
    filtered_df = filtered_df.sort_values(
        "_current_wean_date_parsed",
        ascending=True,
        na_position="last",
    )

elif sort_mode == "Sire Age":
    filtered_df = filtered_df.sort_values(
        "sire_age_days",
        ascending=False,
        na_position="last",
    )

elif sort_mode == "Dame Age":
    filtered_df = filtered_df.sort_values(
        "dame_age_days",
        ascending=False,
        na_position="last",
    )

# Display cards
st.subheader("Breeding Cages")
st.markdown("")
litter_info = []
sac_info = []
st.session_state["sac"] = pd.DataFrame([]) 

for _, row in filtered_df.iterrows():
    color = row["status_color"]

    col1, col2, col3 = st.columns([1.1,1,4])

    with col1:
        st.markdown(
            f"""
            <div style="
                background-color: {color};
                padding-left: 40px;
                padding-bottom: 35px;
                padding-top: 35px;
                border-radius: 10px;
                border: 1px solid #cccccc;
                margin-bottom: 16px;
            ">
                <b>{row['breeding_cage']}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if row["dame_sac_date"]=="" and row["sire_sac_date"]=="":
            new_litter = st.button("New Litter", icon=":material/pest_control_rodent:", key=f"details_{row['breeding_cage']}_1",width="stretch", type="tertiary")
        else:
            new_litter = st.button("New Litter", icon=":material/pest_control_rodent:", key=f"details_{row['breeding_cage']}_1",width="stretch", type="tertiary", disabled=True)
        if row["dame_sac_date"]=="" and row["sire_sac_date"]=="":
            sac_cage = st.button("Sac Cage", icon=":material/deceased:", key=f"details_{row['breeding_cage']}_3",width="stretch", type="tertiary")
        else:
            sac_cage = st.button("Sac Cage", icon=":material/deceased:", key=f"details_{row['breeding_cage']}_3",width="stretch", type="tertiary", disabled=True)

    if new_litter:
        litter_info.append(
            {
                "sire_id": row["sire_id"],
                "dame_id": row["dame_id"],
                "litter_index": len(row["previous_litters"])+len(row["current_litters"])+1,
                "breeding_cage": row["breeding_cage"],
            }
        )
        st.session_state["litter"] = pd.DataFrame(litter_info)
        st.switch_page("pages/new_litter.py")

    if sac_cage:
        sac_info.append(
            {
                "sac_type": "Breeding Cage",
                "sire_id": row["sire_id"],
                "dame_id": row["dame_id"],
                "breeding_cage": row["breeding_cage"],
            }
        )
        st.session_state["sac"] = pd.DataFrame(sac_info)
        st.switch_page("pages/sac.py")

    with col3:
        with st.expander("Details", expanded=False):
            st.subheader("Parent Information")
            st.write(f"Parental Cross: {row['parental_cross']}")
            if row['current_litters'] != [] or row['previous_litters'] != []:
                st.write(f"Days Since Last Litter: {row['days_since_last_litter']}")

            parent_list = []
            parent_list.append({
                "": "Sire",
                "Mouse ID": row['sire_id'],
                "Genotype": row['sire_genotype'],
                "Age (Weeks)": row['sire_age_weeks'],
                })
            parent_list.append({
                "": "Dame",
                "Mouse ID": row['dame_id'],
                "Genotype": row['dame_genotype'],
                "Age (Weeks)": row['dame_age_weeks'],
                })
            parent_table = pd.DataFrame(parent_list)
            st.dataframe(parent_table, width = "stretch", hide_index=True)

            if row['current_litters'] != [] or row['previous_litters'] != []:
                st.subheader("Litter Information")
        
            result = row['current_litters']

            if result != []:
                st.markdown("Current Litters")
                litter_rows = []

                for item in result:
                    item = item.strip().replace("[", "").replace("]", "")
                    parts = item.split(",")

                    litter_rows.append(
                        {
                            "Litter ID": parts[0].strip(),
                            "Litter DOB": parts[1].strip(),
                            "Scheduled Weaning Date": parts[2].strip(),
                        }
                    )
                unweaned_litter_table = pd.DataFrame(litter_rows)
                litter_request = st.dataframe(unweaned_litter_table, width = "stretch", hide_index=True, on_select="rerun", selection_mode = "single-row")

                wean = False
                if litter_request.selection.rows:
                    col1, col2, col3 = st.columns([1,1.2,1.8])
                    with col1:
                        wean = st.button("Wean Litter",icon=":material/move_down:",width = "stretch", type = "tertiary")
                    with col2:
                        reserve = st.button("Reserve Litter",icon=":material/bookmark:",width = "stretch",type = "tertiary")

                    if wean:
                        litter_ids = unweaned_litter_table["Litter ID"]
                        litter_id = litter_ids[litter_request.selection.rows[0]]
                        litter_dobs = unweaned_litter_table["Litter DOB"]
                        litter_dob = litter_dobs[litter_request.selection.rows[0]]
                        litter_info.append(
                            {
                                "sire_id": row["sire_id"],
                                "dame_id": row["dame_id"],
                                "litter_id": litter_id,
                                "litter_index": int(litter_id.split("_")[-1]),
                                "breeding_cage": row["breeding_cage"],
                                "parental_cross": row["parental_cross"],
                                "dob":litter_dob,
                            }
                        )
                        st.session_state["litter"] = pd.DataFrame(litter_info)
                        st.switch_page("pages/wean_litter.py")

                    if reserve:
                        litter_ids = unweaned_litter_table["Litter ID"]
                        litter_id = litter_ids[litter_request.selection.rows[0]]
                        litter_info.append(
                            {
                                "sire_id": row["sire_id"],
                                "dame_id": row["dame_id"],
                                "litter_index": int(litter_id.split("_")[-1]),
                                "breeding_cage": row["breeding_cage"],
                            }
                        )
                        st.session_state["litter"] = pd.DataFrame(litter_info)
                        st.switch_page("pages/request_unweaned_litter.py")


            result = row['previous_litters']
            
            if result != []:
                st.markdown("Previous Litters")
                litter_rows = []

                for item in result:
                    item = item.strip().replace("[", "").replace("]", "")
                    parts = item.split(",")

                    litter_rows.append(
                        {
                            "Litter ID": parts[0].strip(),
                            "Litter DOB": parts[1].strip(),
                            "Litter Wean Date": parts[2].strip(),
                        }
                    )

                litter_table = pd.DataFrame(litter_rows)
                st.dataframe(litter_table, width = "stretch", hide_index=True)

    st.divider()

with st.sidebar:
    st.divider()