from redcap_connect import redCapProject
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import date, datetime

# --------------------------------------------------
# Redcap Record Uploads
# --------------------------------------------------

def create_new_mouse_record(mouse_id, fields):

    data = [
        {
            "mouse_id": mouse_id,
            **fields,
        }
    ]

    return redCapProject.import_records(data)

def update_variable(mouse_id, variable_name, new_value):

    data = [
        {
            "mouse_id": mouse_id,
            variable_name: new_value,
        }
    ]

    return redCapProject.import_records(data)

def add_repeating_instance(mouse_id,repeat_instrument,repeat_instance,fields):

    data = [
        {
            "mouse_id": mouse_id,
            "redcap_repeat_instrument": repeat_instrument,
            "redcap_repeat_instance": repeat_instance,
            **fields,
        }
    ]

    return redCapProject.import_records(data)

def update_repeating_variable(mouse_id,repeat_instrument,repeat_instance,variable_name,new_value):
    
    data = [
        {
            "mouse_id": mouse_id,
            "redcap_repeat_instrument": repeat_instrument,
            "redcap_repeat_instance": repeat_instance,
            variable_name: new_value,
        }
    ]

    return redCapProject.import_records(data)

# --------------------------------------------------
# Redcap Record Downloads
# --------------------------------------------------

def parse_redcap_choices(choice_string):
    """
    Parse REDCap choice string into a list of dictionaries.

    REDCap choice string example:
    'male, Male | female, Female'
    """
    choices = []

    for item in choice_string.split("|"):
        item = item.strip()

        if not item:
            continue

        # Split only on the first comma
        parts = item.split(",", 1)

        if len(parts) != 2:
            continue

        value = parts[0].strip()
        label = parts[1].strip()

        choices.append(
            {
                "value": value,
                "label": label,
            }
        )

    return choices

def load_records():

    records = redCapProject.export_records(
        format_type="json",
        export_data_access_groups=False,
        export_survey_fields=False)

    df = recalculate_dates(pd.DataFrame(records))
    
    return df

# --------------------------------------------------
# Data Restructuring
# --------------------------------------------------

def dob_to_yymm(dob):

    # Convert DOB from YYYY-MM-DD into YYMM format.
    return dob[2:4] + dob[5:7]

def parse_mdy(date_string):

    if pd.isna(date_string):
        return None

    date_string = str(date_string).strip()

    if date_string == "":
        return None

    try:
        return datetime.strptime(date_string, "%Y/%m/%d").date()
    except ValueError:
        return None
    
def genotype_variable_to_label(variable):
    genotype_df = get_genotypes()
    get_label = dict(
        zip(genotype_df["variable"], genotype_df["label"])
    )
    return get_label.get(variable)

def genotype_label_to_variable(label):
    genotype_df = get_genotypes()
    get_variable = dict(
        zip(genotype_df["label"], genotype_df["variable"])
    )
    return get_variable.get(label)

def column_name_to_id(name):
    columns_df = get_columns()
    get_id = dict(
        zip(columns_df["name"], columns_df["id"])
    )
    return get_id.get(name)

def column_id_to_name(id):
    columns_df = get_columns()
    get_name = dict(
        zip(columns_df["id"], columns_df["name"])
    )
    return get_name.get(id)

def find_id_from_sample(sample_name, return_all = False):
    sample_name = str(sample_name).strip()

    mouse_df = st.session_state["redcap_df"].copy()
    mouse_df = mouse_df[mouse_df["mouse_id"] != ""]

    if ":" in sample_name:
        matches = mouse_df[mouse_df["mouse_id"] == sample_name]
    
    else:
        mouse_df["sample_part"] = (
            mouse_df["mouse_id"]
            .str.split(":")
            .str[-1]
            .str.strip()
        )
        matches = mouse_df[mouse_df["sample_part"] == sample_name]
        
    if matches.empty:
        return None
    
    matches["date_prefix"] = (
        matches["mouse_id"]
        .str.split(":")
        .str[0]
        .str.extract(r"(\d{4})")[0]
    )
    matches["date_prefix_num"] = pd.to_numeric(matches["date_prefix"],errors="coerce")
    matches = matches.sort_values(
        "date_prefix_num",
        ascending=False
    )
    if return_all:
        matches = matches[matches["redcap_repeat_instrument"]==""]
        matches = matches["mouse_id"]
        return matches
    else:
        return matches.iloc[0]["mouse_id"]

def resolve_sex_specific_genotype(genotype_result, mouse_id):

    if ":" not in genotype_result:
        return genotype_result

    male_result, female_result = genotype_result.split(":", 1)

    mouse_df = st.session_state["redcap_df"].copy()
    mouse_df = mouse_df[mouse_df["mouse_id"] == mouse_id]
    mouse_sex = mouse_df.iloc[0]["mouse_sex"]

    if mouse_sex == "male":
        return male_result.strip()

    if mouse_sex == "female":
        return female_result.strip()

    return genotype_result

def get_parental_cross(mouse_id):

    mouse_df = st.session_state["redcap_df"].copy()
    mouse_df = mouse_df[(mouse_df["redcap_repeat_instrument"].astype(str).str.strip() == "")]

    offspring = mouse_df[mouse_df["mouse_id"] == mouse_id]
    parental_cage = offspring.iloc[0]["mouse_parental_cage"]
    sex = offspring.iloc[0]["mouse_sex"]

    parent_cage_df = mouse_df[mouse_df["breeding_cage"] == parental_cage]
    sire_df = parent_cage_df[parent_cage_df["mouse_sex"] == "male"]
    dame_df = parent_cage_df[parent_cage_df["mouse_sex"] == "female"]

    sire_genotype = sire_df.iloc[0]["mouse_genotype"]
    dame_genotype = dame_df.iloc[0]["mouse_genotype"]

    sire_genotype = genotype_variable_to_label(sire_genotype)
    dame_genotype = genotype_variable_to_label(dame_genotype)

    parental_cross = f"{sire_genotype} x {dame_genotype}"
    
    return sex, parental_cross

def count_breeding(cross):

    df = st.session_state["redcap_df"].copy()
    df = df[(df["redcap_repeat_instrument"].astype(str).str.strip() == "")]

    genotype_choices = get_genotypes()
    genotype_rename_map = dict(zip(genotype_choices["variable"], genotype_choices["label"]))
    df["genotype_label"] = (df["mouse_genotype"].map(genotype_rename_map))

    current_df = df[df["mouse_sac_date"].astype(str).str.strip() == ""]
    current_breeding = current_df[current_df["breeding_cage"].astype(str).str.strip() != ""]

    if "breeding_separated_date" in current_breeding.columns:
        current_breeding_df = current_breeding[
            current_breeding["breeding_separated_date"].isna()
            | (current_breeding["breeding_separated_date"].astype(str).str.strip() == "")
        ].copy()

    breeding_cages = sorted(current_breeding_df["breeding_cage"].dropna().unique().tolist())
    breeding_records = []

    for cage in breeding_cages:
        cage_mice = current_breeding[current_breeding["breeding_cage"] == cage].copy()

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

    counts_df = (
        breeding_summary_df
        .groupby("parental_cross")
        .size()
        .reset_index(name="breeding_cage_count")
        .sort_values("parental_cross")
    )

    counts_df = counts_df[(counts_df["parental_cross"].astype(str).str.strip() == cross)]

    if counts_df.empty:
        return 0
    else:
        return counts_df.iloc[0]["breeding_cage_count"]

def get_mouse_info_df():
    mouse_info = pd.DataFrame(columns=[
        "mouse_protocol",
        "mouse_ear_id_type",
        "mouse_ear_id",
        "mouse_ear_id_location",
        "mouse_sex",
        "mouse_dob",
        "mouse_genotype",
        "mouse_cage_number",
        "mouse_source",
        "mouse_parental_cage",
        "mouse_parental_cross",
        "mouse_litter_id",
        "mouse_arrival_date",
        "mouse_genotyping",
        "mouse_genotyping_date",
        "mouse_wellplate_number",
        "mouse_transfer",
        "mouse_sac_date",
        "mouse_notes",
        "mouse_genotype_notes",
        "mouse_transfer_notes",
        "mouse_sac_notes",
        "mouse_info_complete",
        "breeding_cage",
        "breeding_partner",
        "breeding_date_created",
        "breeding_separated_date",
        "breeding_notes",
        "breeding_information_complete",
        "request_flag",
        "request_person",
        "request_date",
        "request_experiment",
        "request_experiment_date",
        "request_notes",
        "request_experiment_notes",
        "request_complete",
        "status",
    ])

    return mouse_info

def assign_session_data(mouse_id, i):
    df = st.session_state["redcap_df"].copy()
    mouse_df = df[df["mouse_id"] == mouse_id]
    info_df = mouse_df[mouse_df["redcap_repeat_instrument"] == ""]
    litters_df = mouse_df[mouse_df["redcap_repeat_instrument"] == "litter_information"]
    experiments_df = mouse_df[mouse_df["redcap_repeat_instrument"] == "experiment_information"]

    info = info_df.iloc[0]
    genotype_label = genotype_variable_to_label(info["mouse_genotype"]) if info["mouse_genotype"] else ""

    st.session_state[f"mouse_sex{i}"] = info["mouse_sex"].title()
    st.session_state[f"mouse_cage_number{i}"] = info["mouse_cage_number"]
    st.session_state[f"mouse_protocol{i}"] = info["mouse_protocol"]
    st.session_state[f"mouse_ear_id{i}"] = info["mouse_ear_id"]
    st.session_state[f"mouse_ear_id_type{i}"] = info["mouse_ear_id_type"].title()
    st.session_state[f"mouse_ear_id_location{i}"] = info["mouse_ear_id_location"]
    st.session_state[f"mouse_dob{i}"] = datetime.strptime(info["mouse_dob"], "%Y-%m-%d").date()
    st.session_state[f"mouse_notes{i}"] = info["mouse_notes"]
    st.session_state[f"mouse_genotype{i}"] = genotype_label
    st.session_state[f"mouse_source{i}"] = info["mouse_source"].title()
    st.session_state[f"mouse_arrival_date{i}"] = datetime.strptime(info["mouse_arrival_date"], "%Y-%m-%d").date()
    st.session_state[f"mouse_parental_cage{i}"] = info["mouse_parental_cage"]
    st.session_state[f"mouse_parental_cross{i}"] = info["mouse_parental_cross"]
    st.session_state[f"mouse_litter_id{i}"] = info["mouse_litter_id"]
    st.session_state[f"mouse_genotyping{i}"] = "No" if info["mouse_genotyping"] == "0" else "Yes"
    st.session_state[f"mouse_genotyping_date{i}"] = datetime.strptime(info["mouse_genotyping_date"], "%Y-%m-%d").date() if info["mouse_genotyping"] == "1" else None
    st.session_state[f"mouse_wellplate_number{i}"] = info["mouse_wellplate_number"]
    st.session_state[f"mouse_genotype_notes{i}"] = info["mouse_genotype_notes"]
    st.session_state[f"mouse_transfer{i}"] = info["mouse_transfer"] if info["mouse_sac_date"] != "" else "No"
    st.session_state[f"mouse_transfer_notes{i}"] = info["mouse_transfer_notes"]
    st.session_state[f"mouse_sacced{i}"] = "Yes" if info["mouse_sac_date"] != "" else "No"
    st.session_state[f"mouse_sac_date{i}"] = datetime.strptime(info["mouse_sac_date"], "%Y-%m-%d").date() if info["mouse_sac_date"] != "" else None
    st.session_state[f"mouse_sac_notes{i}"] = info["mouse_sac_notes"]

    if info["breeding_cage"] != "":
        st.session_state[f"breeding_cage{i}"] = info["breeding_cage"]
        st.session_state[f"breeding_partner{i}"] = info["breeding_partner"]
        st.session_state[f"breeding_date_created{i}"] = datetime.strptime(info["breeding_date_created"], "%Y-%m-%d").date() if info["breeding_date_created"] != "" else None
        st.session_state[f"breeding_separated_date{i}"] = datetime.strptime(info["breeding_separated_date"], "%Y-%m-%d").date() if info["breeding_separated_date"] != "" else None
        st.session_state[f"breeding_notes{i}"] = info["breeding_notes"]

        for j in range(len(litters_df)):
            litter = litters_df.iloc[j]
            st.session_state[f"litter_dob{i}{j}"] = datetime.strptime(litter["litter_dob"], "%Y-%m-%d").date()
            st.session_state[f"litter_wean_date{i}{j}"] = None if litter["litter_wean_date"] == "" else datetime.strptime(litter["litter_wean_date"], "%Y-%m-%d").date()
            st.session_state[f"litter_notes_new{i}{j}"] = litter["litter_notes_new"]
            st.session_state[f"litter_wean_num_m{i}{j}"] = litter["litter_wean_num_m"]
            st.session_state[f"litter_sac_num_m{i}{j}"] = litter["litter_sac_num_m"]
            st.session_state[f"litter_wean_num_f{i}{j}"] = litter["litter_wean_num_f"]
            st.session_state[f"litter_sac_num_f{i}{j}"] = litter["litter_sac_num_f"]
            st.session_state[f"litter_notes_wean{i}{j}"] = litter["litter_notes_wean"]
            st.session_state[f"litter_reserver{i}{j}"] = litter["litter_reserver"]
            st.session_state[f"litter_reservation{i}{j}"] = litter["litter_reservation"]
            st.session_state[f"litter_notes_reserve{i}{j}"] = litter["litter_notes_reserve"]

    for j in range(len(experiments_df)):
        experiment = experiments_df.iloc[j]
        st.session_state[f"experiment_type{i}{j}"] = experiment["experiment_type"].replace("_"," ").title()
        st.session_state[f"experiment_date{i}{j}"] = datetime.strptime(experiment["experiment_date"], "%Y-%m-%d").date()
        st.session_state[f"experiment_experimentor{i}{j}"] = experiment["experiment_experimentor"].title()
        st.session_state[f"experiment_notes{i}{j}"] = experiment["experiment_notes"]

    if info["request_flag"] != "":
        st.session_state[f"request_flag{i}"] = info["request_flag"].replace("_"," ").title()
        st.session_state[f"request_person{i}"] = info["request_person"]
        st.session_state[f"request_date{i}"] = datetime.strptime(info["request_date"], "%Y-%m-%d").date() if info["request_date"] != "" else None
        st.session_state[f"request_experiment{i}"] = info["request_experiment"].replace("_","").title()
        st.session_state[f"request_experiment_date{i}"] = datetime.strptime(info["request_experiment_date"], "%Y-%m-%d").date() if info["request_experiment_date"] != "" else None
        st.session_state[f"request_notes{i}"] = info["request_notes"]
        st.session_state[f"request_experiment_notes{i}"] = info["request_experiment_notes"]

def submit_session_data(mouse_id, i, breeding, litters, experiments):

    litters = litters.reset_index(drop=True)
    experiments = experiments.reset_index(drop=True)

    fields = {
        "mouse_sex": st.session_state[f"mouse_sex{i}"].lower(),
        "mouse_cage_number": st.session_state[f"mouse_cage_number{i}"],
        "mouse_protocol": st.session_state[f"mouse_protocol{i}"],
        "mouse_ear_id": st.session_state[f"mouse_ear_id{i}"],
        "mouse_ear_id_type": st.session_state[f"mouse_ear_id_type{i}"].lower(),
        "mouse_ear_id_location": st.session_state[f"mouse_ear_id_location{i}"].lower(),
        "mouse_dob": st.session_state[f"mouse_dob{i}"].strftime("%Y-%m-%d"),
        "mouse_notes": st.session_state[f"mouse_notes{i}"],
        "mouse_genotype": genotype_label_to_variable(st.session_state[f"mouse_genotype{i}"]),
        "mouse_source": st.session_state[f"mouse_source{i}"].lower(),
        "mouse_arrival_date": st.session_state[f"mouse_arrival_date{i}"].strftime("%Y-%m-%d"),
        "mouse_parental_cage": st.session_state[f"mouse_parental_cage{i}"],
        "mouse_parental_cross": st.session_state[f"mouse_parental_cross{i}"],
        "mouse_litter_id": st.session_state[f"mouse_litter_id{i}"],
        "mouse_genotyping": "0" if st.session_state[f"mouse_genotyping{i}"] == "No" else "1",
        "mouse_genotyping_date": st.session_state[f"mouse_genotyping_date{i}"].strftime("%Y-%m-%d") if st.session_state[f"mouse_genotyping{i}"] == "Yes" else "",
        "mouse_wellplate_number": st.session_state[f"mouse_wellplate_number{i}"],
        "mouse_genotype_notes": st.session_state[f"mouse_genotype_notes{i}"],
        "mouse_transfer": "0" if st.session_state[f"mouse_transfer{i}"] == "No" else "1",
        "mouse_transfer_notes": st.session_state[f"mouse_transfer_notes{i}"],
        "mouse_sac_date": "" if st.session_state[f"mouse_sacced{i}"] == "No" else st.session_state[f"mouse_sac_date{i}"].strftime("%Y-%m-%d"),
        "mouse_sac_notes": st.session_state[f"mouse_sac_notes{i}"],
        # "mouse_info_complete": "0" if st.session_state[f"mouse_sacced{i}"] == "No" else "2"
    }
    create_new_mouse_record(mouse_id, fields)

    if breeding == True:
        fields = {
            "breeding_cage": st.session_state[f"breeding_cage{i}"],
            "breeding_partner": st.session_state[f"breeding_partner{i}"],
            "breeding_date_created": st.session_state[f"breeding_date_created{i}"].strftime("%Y-%m-%d"),
            "breeding_date_separated": "" if st.session_state[f"breeding_separated_date{i}"] == None else st.session_state[f"breeding_separated_date{i}"].strftime("%Y-%m-%d"), 
            "breeding_notes": st.session_state[f"breeding_notes{i}"],
            "breeding_information_complete": "2"
        }
        create_new_mouse_record(mouse_id, fields)

    for j in range(len(litters)):
        fields = {
            "redcap_repeat_instrument": "litter_information",
            "redcap_repeat_instance": str(j+1),
            "litter_id": litters["litter_id"].iloc[j],
            "litter_dob": st.session_state[f"litter_dob{i}{j}"].strftime("%Y-%m-%d"),
            "litter_wean_date": "" if st.session_state[f"litter_wean_date{i}{j}"] == None else st.session_state[f"litter_wean_date{i}{j}"].strftime("%Y-%m-%d"),
            "litter_notes_new": st.session_state[f"litter_notes_new{i}{j}"],
            "litter_wean_num_m": st.session_state[f"litter_wean_num_m{i}{j}"],
            "litter_sac_num_m": st.session_state[f"litter_sac_num_m{i}{j}"],
            "litter_wean_num_f": st.session_state[f"litter_wean_num_f{i}{j}"],
            "litter_sac_num_f": st.session_state[f"litter_sac_num_f{i}{j}"],
            "litter_notes_wean": st.session_state[f"litter_notes_wean{i}{j}"],
            "litter_reserver": st.session_state[f"litter_reserver{i}{j}"],
            "litter_reservation": st.session_state[f"litter_reservation{i}{j}"],
            "litter_notes_reserve": st.session_state[f"litter_notes_reserve{i}{j}"],
            "litter_information_complete": "0" if st.session_state[f"litter_wean_date{i}{j}"] == None else "2",
        }
        create_new_mouse_record(mouse_id, fields)

    for j in range(len(experiments)):
        fields = {
            "redcap_repeat_instrument": "experiment_information",
            "redcap_repeat_instance": str(j+1),
            "experiment_type": st.session_state[f"experiment_type{i}{j}"].replace(" ","_").lower(),
            "experiment_date": st.session_state[f"experiment_date{i}{j}"].strftime("%Y-%m-%d"),
            "experiment_experimentor": st.session_state[f"experiment_experimentor{i}{j}"],
            "experiment_notes": " " if st.session_state[f"experiment_notes{i}{j}"] == "" else st.session_state[f"experiment_notes{i}{j}"],
            "experiment_information_complete": "2"
        }
        create_new_mouse_record(mouse_id,fields)

    #if st.session_state[f"request_flag{i}"]

    with st.sidebar:
        st.success(f"Mouse {mouse_id} updated successfully")
        st.divider()

    """
        if info["request_flag"] != "":
            st.session_state[f"request_flag{i}"] = info["request_flag"].replace("_"," ").title()
            st.session_state[f"request_person{i}"] = info["request_person"]
            st.session_state[f"request_date{i}"] = datetime.strptime(info["request_date"], "%Y-%m-%d").date() if info["request_date"] != "" else None
            st.session_state[f"request_experiment{i}"] = info["request_experiment"].replace("_","").title()
            st.session_state[f"request_experiment_date{i}"] = datetime.strptime(info["request_experiment_date"], "%Y-%m-%d").date() if info["request_experiment_date"] != "" else None
            st.session_state[f"request_notes{i}"] = info["request_notes"]
            st.session_state[f"request_experiment_notes{i}"] = info["request_experiment_notes"]
    """

def recalculate_dates(df):
    today = date.today()
    for i in range(len(df)):
        if df.loc[i,"redcap_repeat_instrument"] == "":
            dob = datetime.strptime(df["mouse_dob"].iloc[i], "%Y-%m-%d").date()
            if df.loc[i,"mouse_sac_date"] != "":
                sac_date = datetime.strptime(df["mouse_sac_date"].iloc[i], "%Y-%m-%d").date()
                days = days = (sac_date - dob).days
                df.loc[i,"mouse_age_days"] = f"{days}"
                df.loc[i,"mouse_age_weeks"] = f"{days/7:.1f}"
                df.loc[i,"mouse_age_months"] = f"{days/30.4375:.1f}"
            else:
                days = (today - dob).days
                df.loc[i,"mouse_age_days"] = f"{days}"
                df.loc[i,"mouse_age_weeks"] = f"{days/7:.1f}"
                df.loc[i,"mouse_age_months"] = f"{days/30.4375:.1f}"
    return df
# --------------------------------------------------
# Layout and Design
# --------------------------------------------------

def get_field_choices(field_name):

    metadata = redCapProject.export_metadata(format_type="json")

    for field in metadata:
        if field["field_name"] == field_name:
            choice_string = field.get("select_choices_or_calculations", "")
            return parse_redcap_choices(choice_string)

    raise ValueError(f"Field not found in REDCap metadata: {field_name}")

def selected():
    with st.sidebar:
        alert = st.info("Mouse Added to Request")
    return alert
           
def group_records(df,group):

    group_column_map = {
        "Cage Number": "mouse_cage_number",
        "Litter ID": "mouse_litter_id",
        "Genotype": "mouse_genotype",
        "Flag": "flag",
    }

    group_column = group_column_map[group]

    df = df[df[group_column] != ""]

    if group_column == "mouse_cage_number":
        df = df[df["mouse_transfer"] != "1"]
    
    grouped = df.groupby(group_column, dropna=True)

    return grouped

def get_columns():
    columns_df = pd.DataFrame(
        [
            {"name": "Mouse ID", "id": "mouse_id"},
            {"name": "Protocol Number", "id": "mouse_protocol"},
            {"name": "Ear ID Type", "id": "mouse_ear_id_type"},
            {"name": "Ear ID Location", "id": "mouse_ear_id_location"},
            {"name": "Ear ID Number", "id": "mouse_ear_id"},
            {"name": "Sex", "id": "mouse_sex"},
            {"name": "Date of Birth", "id": "mouse_dob"},
            {"name": "Age (Days)", "id": "mouse_age_days"},
            {"name": "Age (Weeks)", "id": "mouse_age_weeks"},
            {"name": "Age (Months)", "id": "mouse_age_months"},
            {"name": "Genotype", "id": "mouse_genotype"},
            {"name": "Cage Number", "id": "mouse_cage_number"},
            {"name": "Mouse Source", "id": "mouse_source"},
            {"name": "Parental Cage", "id": "mouse_parental_cage"},
            {"name": "Parental Cross", "id": "mouse_parental_cross"},
            {"name": "Litter ID", "id": "mouse_litter_id"},
            {"name": "Wean/Arrival Date", "id": "mouse_arrival_date"},
            {"name": "Genotyping Performed", "id": "mouse_genotyping"},
            {"name": "Genotyping Date", "id": "mouse_genotyping_date"},
            {"name": "Wellplate Number", "id": "mouse_wellplate_number"},
            {"name": "Mouse Transferred to New Cage", "id": "mouse_transfer"},
            {"name": "Sac Date", "id": "mouse_sac_date"},
            {"name": "Mouse Notes", "id": "mouse_notes"},
            {"name": "Genotyping Notes", "id": "mouse_genotype_notes"},
            {"name": "Transfer Notes", "id": "mouse_transfer_notes"},
            {"name": "Sac Notes", "id": "mouse_sac_notes"},
            #{"name": "Experiment", "id": "experiment_type"},
            #{"name": "Experimentor", "id": "experiment_experimentor"},
            #{"name": "Experiment Date", "id": "experiment_date"},
            {"name": "Request Flag", "id": "request_flag"},
            {"name": "Requestor", "id": "request_person"},
            {"name": "Request Date", "id": "request_date"},
            {"name": "Requested Experiment", "id": "request_experiment"},
            {"name": "Requested Experiment Date", "id": "request_experiment_date"},
            {"name": "Request Notes", "id": "request_notes"},
            {"name": "Requested Experiment Notes", "id": "request_experiment_notes"},
        ]
    )
    return columns_df

def display_wellplate(selected_well):
    rows = list("ABCDEFGH")
    cols = list(range(1, 13))

    selected_well = selected_well.upper().strip()

    html = """
    <style>
    .plate-grid {
        display: grid;
        grid-template-columns: 30px repeat(12, 14px);
        gap: 3px;
        align-items: right;
        font-family: sans-serif;
    }

    .plate-label {
        text-align: center;
        font-size: 8px;
        color: #555;
    }

    .well-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #E8E6EC;
        border: 1px solid #999;
        display: inline-block;
    }

    .well-dot.selected {
        background-color: #787088;
        border: 2px solid #787088;
        box-shadow: 0 0 6px rgba(150, 76, 255, 0.8);
    }
    </style>

    <div class="plate-grid">
        <div></div>
    """

    # Column headers
    for col in cols:
        html += f'<div class="plate-label">{col}</div>'

    # Rows and wells
    for row in rows:
        html += f'<div class="plate-label">{row}</div>'

        for col in cols:
            well = f"{row}{col}"
            selected_class = "selected" if well == selected_well else ""
            html += f'<div title="{well}" class="well-dot {selected_class}"></div>'

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

# --------------------------------------------------
# Genotyping
# -------------------------------------------------- 

def get_genotypes():
    genotype_df = pd.DataFrame(
        [     
            {"label": "Ai14(+/+)", "variable": "ai14_pp"},

            {"label": "Ai148(+)", "variable": "ai148_p"},
            {"label": "Ai148(-)", "variable": "ai148_-"},

            {"label": "Ai14(+/-); Gad2-cre(-/-)", "variable": "ai14_p-_gad2-cre_--"},
            {"label": "Ai14(+/-); Gad2-cre(+/-)", "variable": "ai14_p-_gad2-cre_p-"},
            {"label": "Ai14(+/-); Pvalb-cre(-/-)", "variable": "ai14_p-_pvalb-cre_--"},
            {"label": "Ai14(+/-); Pvalb-cre(+/-)", "variable": "ai14_p-_pvalb-cre_p-"},
            {"label": "Ai14(+/-); Six3-cre(-)", "variable": "ai14_p-_six3-cre_-"},
            {"label": "Ai14(+/-); Six3-cre(+)", "variable": "ai14_p-_six3-cre_p"},
            
            {"label": "C57BL/6J", "variable": "c57bl6j"},

            {"label": "Fmr1(+/y)", "variable": "fmr1_py"},
            {"label": "Fmr1(-/y)", "variable": "fmr1_-y"},
            {"label": "Fmr1(+/+)", "variable": "fmr1_pp"},
            {"label": "Fmr1(+/-)", "variable": "fmr1_p-"},
            {"label": "Fmr1(-/-)", "variable": "fmr1_--"},

            {"label": "Fmr1(+/y); Pvalb-tdTomato(+)", "variable": "fmr1_py_pvalb-tdtomato_p"},
            {"label": "Fmr1(+/y); Pvalb-tdTomato(-)", "variable": "fmr1_py_pvalb-tdtomato_-"},
            {"label": "Fmr1(-/y); Pvalb-tdTomato(+)", "variable": "fmr1_-y_pvalb-tdtomato_p"},
            {"label": "Fmr1(-/y); Pvalb-tdTomato(-)", "variable": "fmr1_-y_pvalb-tdtomato_-"},
            {"label": "Fmr1(+/+); Pvalb-tdTomato(+)", "variable": "fmr1_pp_pvalb-tdtomato_p"},
            {"label": "Fmr1(+/+); Pvalb-tdTomato(-)", "variable": "fmr1_pp_pvalb-tdtomato_-"},
            {"label": "Fmr1(+/-); Pvalb-tdTomato(+)", "variable": "fmr1_p-_pvalb-tdtomato_p"},
            {"label": "Fmr1(+/-); Pvalb-tdTomato(-)", "variable": "fmr1_p-_pvalb-tdtomato_-"},
            
            {"label": "Fmr1(flox/y)", "variable": "fmr1_floxy"},
            {"label": "Fmr1(flox/+)", "variable": "fmr1_floxp"},
            {"label": "Fmr1(flox/flox)", "variable": "fmr1_floxflox"},

            {"label": "Fmr1(flox/y); Gad2-cre(+/-)", "variable": "fmr1_floxy_gad2-cre_p-"},
            {"label": "Fmr1(flox/y); Gad2-cre(-/-)", "variable": "fmr1_floxy_gad2-cre_--"},
            {"label": "Fmr1(flox/y); Pvalb-cre(+/-)", "variable": "fmr1_floxy_pvalb-cre_p-"},
            {"label": "Fmr1(flox/y); Pvalb-cre(-/-)", "variable": "fmr1_floxy_pvalb-cre_--"},
            {"label": "Fmr1(flox/y); Six3-cre(+)", "variable": "fmr1_floxy_six3-cre_p"},
            {"label": "Fmr1(flox/y); Six3-cre(-)", "variable": "fmr1_floxy_six3-cre_-"},

            {"label": "Fmr1(flox/+); Gad2-cre(+/-)", "variable": "fmr1_floxp_gad2-cre_p-"},
            {"label": "Fmr1(flox/+); Gad2-cre(-/-)", "variable": "fmr1_floxp_gad2-cre_--"},
            {"label": "Fmr1(flox/+); Pvalb-cre(+/-)", "variable": "fmr1_floxp_pvalb-cre_p-"},
            {"label": "Fmr1(flox/+); Pvalb-cre(-/-)", "variable": "fmr1_floxp_pvalb-cre_--"},
            {"label": "Fmr1(flox/+); Six3-cre(+)", "variable": "fmr1_floxp_six3-cre_p"},
            {"label": "Fmr1(flox/+); Six3-cre(-)", "variable": "fmr1_floxp_six3-cre_-"},

            {"label": "Gad2-cre(+/+)", "variable": "gad2-cre_pp"},
            {"label": "Gad2-cre(+/-)", "variable": "gad2-cre_p-"},
            {"label": "Gad2-cre(-/-)", "variable": "gad2-cre_--"},

            {"label": "Gad2-cre(+/-); Ai148(-)", "variable": "gad2-cre_p-_ai148_-"},

            {"label": "OPN1(+/+)", "variable": "opn1_pp"},
            {"label": "OPN1(LW/y)", "variable": "opn1_lwy"},
            {"label": "OPN1(LW/+)", "variable": "opn1_lwp"},
            {"label": "OPN1(LW/MW)", "variable": "opn1_lwmw"},
            {"label": "OPN1(MW/y)", "variable": "opn1_mwy"},
            {"label": "OPN1(MW/MW)", "variable": "opn1_mwmw"},

            {"label": "OPN1(SW/+)", "variable": "opn1_swp"},
            {"label": "OPN1(SW/SW)", "variable": "opn1_swsw"},

            {"label": "Pvalb-cre(+/+)", "variable": "pvalb-cre_pp"},
            {"label": "Pvalb-cre(+/-)", "variable": "pvalb-cre_p-"},
            {"label": "Pvalb-cre(-/-)", "variable": "pvalb-cre_--"},
            {"label": "Pvalb-cre(?/-)", "variable": "pvalb-cre_u-"},

            {"label": "Pvalb-tdTomato(+/-)", "variable": "pvalb-tdtomato_p-"},

            {"label": "RD10(+/-)", "variable": "rd10_p-"},
            {"label": "RD10(-/-)", "variable": "rd10_--"},

            {"label": "RhoP23H", "variable": "rhop23h"},

            {"label": "Six3-cre(+)", "variable": "six3-cre_p"},
            {"label": "Six3-cre(-)", "variable": "six3-cre_-"},
            {"label": "Six3-cre(?/-)", "variable": "six3-cre_u-"},

            {"label": "Waiting on Results", "variable": "waiting"},
            {"label": "Not Genotyped", "variable": "not_genotyped"},
        ]
    )
    return genotype_df
 
def get_cross_genotypes():
    genotype_cross_df = pd.DataFrame(
        [
            {"cross": "C57BL/6J x Ai148(+)", "sex": "", "offspring_genotype": "Ai148(-)"},
            {"cross": "C57BL/6J x Ai148(+)", "sex": "", "offspring_genotype": "Ai148(+)"},
            {"cross": "C57BL/6J x C57BL/6J", "sex": "", "offspring_genotype": "C57BL/6J"},

            {"cross": "C57BL/6J x Fmr1(-/-)", "sex": "male", "offspring_genotype": "Fmr1(-/y)"},
            {"cross": "C57BL/6J x Fmr1(-/-)", "sex": "female", "offspring_genotype": "Fmr1(+/-)"},

            {"cross": "C57BL/6J x Fmr1(+/-); Pvalb-tdTomato(+/-)", "sex": "male", "offspring_genotype": "Fmr1(-/y); Pvalb-tdTomato(-)"},
            {"cross": "C57BL/6J x Fmr1(+/-); Pvalb-tdTomato(+/-)", "sex": "male", "offspring_genotype": "Fmr1(-/y); Pvalb-tdTomato(+)"},
            {"cross": "C57BL/6J x Fmr1(+/-); Pvalb-tdTomato(+/-)", "sex": "female", "offspring_genotype": "Fmr1(+/-); Pvalb-tdTomato(-)"},
            {"cross": "C57BL/6J x Fmr1(+/-); Pvalb-tdTomato(+/-)", "sex": "female", "offspring_genotype": "Fmr1(+/-); Pvalb-tdTomato(+)"},
            {"cross": "C57BL/6J x Fmr1(+/-); Pvalb-tdTomato(+/-)", "sex": "female", "offspring_genotype": "Fmr1(+/+); Pvalb-tdTomato(-)"},
            {"cross": "C57BL/6J x Fmr1(+/-); Pvalb-tdTomato(+/-)", "sex": "female", "offspring_genotype": "Fmr1(+/+); Pvalb-tdTomato(+)"},
            {"cross": "C57BL/6J x Fmr1(+/-); Pvalb-tdTomato(+/-)", "sex": "male", "offspring_genotype": "Fmr1(+/y); Pvalb-tdTomato(-)"},
            {"cross": "C57BL/6J x Fmr1(+/-); Pvalb-tdTomato(+/-)", "sex": "male", "offspring_genotype": "Fmr1(+/y); Pvalb-tdTomato(+)"},

            {"cross": "C57BL/6J x Fmr1(+/-)", "sex": "male", "offspring_genotype": "Fmr1(-/y)"},
            {"cross": "C57BL/6J x Fmr1(+/-)", "sex": "female", "offspring_genotype": "Fmr1(+/-)"},
            {"cross": "C57BL/6J x Fmr1(+/-)", "sex": "female", "offspring_genotype": "Fmr1(+/+)"},
            {"cross": "C57BL/6J x Fmr1(+/-)", "sex": "male", "offspring_genotype": "Fmr1(+/y)"},

            {"cross": "C57BL/6J x Fmr1(flox/flox)", "sex": "female", "offspring_genotype": "Fmr1(flox/+)"},
            {"cross": "C57BL/6J x Fmr1(flox/flox)", "sex": "male", "offspring_genotype": "Fmr1(flox/y)"},

            {"cross": "Fmr1(-/y); Pvalb-tdTomato(+) x C57BL/6J", "sex": "female", "offspring_genotype": "Fmr1(+/-); Pvalb-tdTomato(-)"},
            {"cross": "Fmr1(-/y); Pvalb-tdTomato(+) x C57BL/6J", "sex": "female", "offspring_genotype": "Fmr1(+/-); Pvalb-tdTomato(+)"},
            {"cross": "Fmr1(-/y); Pvalb-tdTomato(+) x C57BL/6J", "sex": "male", "offspring_genotype": "Fmr1(+/y); Pvalb-tdTomato(-)"},
            {"cross": "Fmr1(-/y); Pvalb-tdTomato(+) x C57BL/6J", "sex": "male", "offspring_genotype": "Fmr1(+/y); Pvalb-tdTomato(+)"},

            {"cross": "Fmr1(-/y) x Fmr1(+/+); Pvalb-tdTomato(+)", "sex": "female", "offspring_genotype": "Fmr1(+/-); Pvalb-tdTomato(-)"},
            {"cross": "Fmr1(-/y) x Fmr1(+/+); Pvalb-tdTomato(+)", "sex": "female", "offspring_genotype": "Fmr1(+/-); Pvalb-tdTomato(+)"},
            {"cross": "Fmr1(-/y) x Fmr1(+/+); Pvalb-tdTomato(+)", "sex": "male", "offspring_genotype": "Fmr1(+/y); Pvalb-tdTomato(-)"},
            {"cross": "Fmr1(-/y) x Fmr1(+/+); Pvalb-tdTomato(+)", "sex": "male", "offspring_genotype": "Fmr1(+/y); Pvalb-tdTomato(+)"},

            {"cross": "Fmr1(-/y) x Pvalb-tdTomato(+)", "sex": "female", "offspring_genotype": "Fmr1(+/-); Pvalb-tdTomato(-)"},
            {"cross": "Fmr1(-/y) x Pvalb-tdTomato(+)", "sex": "female", "offspring_genotype": "Fmr1(+/-); Pvalb-tdTomato(+)"},
            {"cross": "Fmr1(-/y) x Pvalb-tdTomato(+)", "sex": "male", "offspring_genotype": "Fmr1(+/y); Pvalb-tdTomato(-)"},
            {"cross": "Fmr1(-/y) x Pvalb-tdTomato(+)", "sex": "male", "offspring_genotype": "Fmr1(+/y); Pvalb-tdTomato(+)"},

            {"cross": "Fmr1(flox/y) x Fmr1(flox/flox)", "sex": "female", "offspring_genotype": "Fmr1(flox/flox)"},
            {"cross": "Fmr1(flox/y) x Fmr1(flox/flox)", "sex": "male", "offspring_genotype": "Fmr1(flox/y)"},

            {"cross": "Gad2-cre(+/-) x Ai14(+/+)", "sex": "", "offspring_genotype": "Ai14(+/-); Gad2-cre(-/-)"},
            {"cross": "Gad2-cre(+/-) x Ai14(+/+)", "sex": "", "offspring_genotype": "Ai14(+/-); Gad2-cre(+/-)"},
            {"cross": "Gad2-cre(+/-) x C57BL/6J", "sex": "", "offspring_genotype": "Gad2-cre(-/-)"},
            {"cross": "Gad2-cre(+/-) x C57BL/6J", "sex": "", "offspring_genotype": "Gad2-cre(+/-)"},

            {"cross": "Gad2-cre(+/-) x Fmr1(flox/flox)", "sex": "female", "offspring_genotype": "Fmr1(flox/+); Gad2-cre(-/-)"},
            {"cross": "Gad2-cre(+/-) x Fmr1(flox/flox)", "sex": "female", "offspring_genotype": "Fmr1(flox/+); Gad2-cre(+/-)"},
            {"cross": "Gad2-cre(+/-) x Fmr1(flox/flox)", "sex": "male", "offspring_genotype": "Fmr1(flox/y); Gad2-cre(-/-)"},
            {"cross": "Gad2-cre(+/-) x Fmr1(flox/flox)", "sex": "male", "offspring_genotype": "Fmr1(flox/y); Gad2-cre(+/-)"},

            {"cross": "Gad2-cre(+/+) x Ai148(+)", "sex": "", "offspring_genotype": "Gad2-cre(+/-); Ai148(-)"},
            {"cross": "Gad2-cre(+/+) x C57BL/6J", "sex": "", "offspring_genotype": "Gad2-cre(+/-)"},

            {"cross": "OPN1(MW/y) x OPN1(LW/MW)", "sex": "female", "offspring_genotype": "OPN1(LW/MW)"},
            {"cross": "OPN1(MW/y) x OPN1(LW/MW)", "sex": "male", "offspring_genotype": "OPN1(LW/y)"},
            {"cross": "OPN1(MW/y) x OPN1(LW/MW)", "sex": "female", "offspring_genotype": "OPN1(MW/MW)"},
            {"cross": "OPN1(MW/y) x OPN1(LW/MW)", "sex": "male", "offspring_genotype": "OPN1(MW/y)"},

            {"cross": "OPN1(SW/+) x OPN1(SW/+)", "sex": "", "offspring_genotype": "OPN1(+/+)"},
            {"cross": "OPN1(SW/+) x OPN1(SW/+)", "sex": "", "offspring_genotype": "OPN1(SW/+)"},
            {"cross": "OPN1(SW/+) x OPN1(SW/+)", "sex": "", "offspring_genotype": "OPN1(SW/SW)"},

            {"cross": "Pvalb-cre(+/-) x Ai14(+/+)", "sex": "", "offspring_genotype": "Ai14(+/-); Pvalb-cre(-/-)"},
            {"cross": "Pvalb-cre(+/-) x Ai14(+/+)", "sex": "", "offspring_genotype": "Ai14(+/-); Pvalb-cre(+/-)"},

            {"cross": "Pvalb-cre(+/-) x C57BL/6J", "sex": "", "offspring_genotype": "Pvalb-cre(-/-)"},
            {"cross": "Pvalb-cre(+/-) x C57BL/6J", "sex": "", "offspring_genotype": "Pvalb-cre(?/-)"},
            {"cross": "Pvalb-cre(+/-) x C57BL/6J", "sex": "", "offspring_genotype": "Pvalb-cre(+/-)"},

            {"cross": "Pvalb-cre(+/-) x Fmr1(flox/flox)", "sex": "female", "offspring_genotype": "Fmr1(flox/+); Pvalb-cre(-/-)"},
            {"cross": "Pvalb-cre(+/-) x Fmr1(flox/flox)", "sex": "female", "offspring_genotype": "Fmr1(flox/+); Pvalb-cre(+/-)"},
            {"cross": "Pvalb-cre(+/-) x Fmr1(flox/flox)", "sex": "male", "offspring_genotype": "Fmr1(flox/y); Pvalb-cre(-/-)"},
            {"cross": "Pvalb-cre(+/-) x Fmr1(flox/flox)", "sex": "male", "offspring_genotype": "Fmr1(flox/y); Pvalb-cre(+/-)"},

            {"cross": "Pvalb-cre(+/+) x C57BL/6J", "sex": "", "offspring_genotype": "Pvalb-cre(+/-)"},

            {"cross": "Six3-cre(+) x Ai14(+/+)", "sex": "", "offspring_genotype": "Ai14(+/-); Six3-cre(-)"},
            {"cross": "Six3-cre(+) x Ai14(+/+)", "sex": "", "offspring_genotype": "Ai14(+/-); Six3-cre(+)"},
            {"cross": "Six3-cre(+) x C57BL/6J", "sex": "", "offspring_genotype": "Six3-cre(-)"},
            {"cross": "Six3-cre(+) x C57BL/6J", "sex": "", "offspring_genotype": "Six3-cre(+)"},
            {"cross": "Six3-cre(+) x C57BL/6J", "sex": "", "offspring_genotype": "Six3-cre(?/-)"},

            {"cross": "Six3-cre(+) x Fmr1(flox/flox)", "sex": "female", "offspring_genotype": "Fmr1(flox/+); Six3-cre(-)"},
            {"cross": "Six3-cre(+) x Fmr1(flox/flox)", "sex": "female", "offspring_genotype": "Fmr1(flox/+); Six3-cre(+)"},
            {"cross": "Six3-cre(+) x Fmr1(flox/flox)", "sex": "male", "offspring_genotype": "Fmr1(flox/y); Six3-cre(-)"},
            {"cross": "Six3-cre(+) x Fmr1(flox/flox)", "sex": "male", "offspring_genotype": "Fmr1(flox/y); Six3-cre(+)"},
        ]
    )

    return genotype_cross_df

def get_possible_genotypes(parental_cross, pup_sex):

    cross_df = get_cross_genotypes()

    genotype_options = cross_df[
        (cross_df["cross"] == parental_cross)
        & (
            (cross_df["sex"] == pup_sex)
            | (cross_df["sex"] == "")
        )
    ]

    if genotype_options.empty:
        return cross_df

    return genotype_options

def build_breeding_dashboard_table(df):

    litter_df = df[df["redcap_repeat_instrument"] == "litter_information"]
    breeding_df = df[df["breeding_cage"] != ""]

    current_breeding_df = breeding_df

    breeding_cages = (
        current_breeding_df["breeding_cage"]
        .unique()
        .tolist()
    )

    dashboard_rows = []

    today = date.today()

    for cage in sorted(breeding_cages):
        cage = str(cage).strip()

        # Find all mice in breeding cage
        mice = breeding_df[breeding_df["breeding_cage"] == cage]

        # Find Sire Information
        sires = mice[mice["mouse_sex"] == "male"]
        if not sires.empty:
            sire = sires.iloc[0]
            sire_id = sire["mouse_id"]
            sire_age_days = int(sire["mouse_age_days"])
            sire_age_weeks = round(sire_age_days / 7,1)
            sire_genotype = sire["mouse_genotype"]
        else:
            sire_id = ""
            sire_age_days = 7
            sire_age_weeks = 1
            sire_genotype = ""
        
        # Find Dame Informantion
        dames = mice[mice["mouse_sex"] == "female"]
        if not dames.empty:
            dame = dames.iloc[0]
            dame_id = dame["mouse_id"]
            dame_age_days = int(dame["mouse_age_days"])
            dame_age_weeks = round(dame_age_days / 7,1)
            dame_genotype = dame["mouse_genotype"]
        else:
            dame_id = ""
            dame_age_days = 7
            dame_age_weeks = 1
            dame_genotype = ""

        # Find Litter Information
        sire_genotype_label = genotype_variable_to_label(sire_genotype)
        dame_genotype_label = genotype_variable_to_label(dame_genotype)
        parental_cross = f"{sire_genotype_label} x {dame_genotype_label}"

        cage_litters = litter_df[litter_df["mouse_id"] == sire_id]

        # Report on Previous Litters
        current_litters = []
        previous_litters = []
        weaning_needed = False
        days_since_last_litter = None

        if not cage_litters.empty:
            
            unweaned_litters = cage_litters[cage_litters["litter_wean_date"] == ""]
            
            if not unweaned_litters.empty:
                for _, litter in unweaned_litters.iterrows():
                    unweaned_litter_id = litter.get("litter_id", "")
                    unweaned_litter_dob = litter.get("litter_dob","")
                    unweaned_wean_date = litter.get("litter_date_to_wean", "")
                    
                    wean_date = date.fromisoformat(str(unweaned_wean_date).strip())

                    if wean_date <= today:
                        weaning_needed = True 

                    current_litters.append(
                        f"[{unweaned_litter_id}, {unweaned_litter_dob}, {unweaned_wean_date}]"
                    )

            weaned_litters = cage_litters[cage_litters["litter_wean_date"] != ""]

            for _, litter in weaned_litters.iterrows():
                litter_id = litter.get("litter_id", "")
                litter_dob = litter.get("litter_dob", "")
                litter_wean_date = litter.get("litter_wean_date", "")

                previous_litters.append(
                    f"[{litter_id}, {litter_dob}, {litter_wean_date}]"
                )

            most_recent_litter = cage_litters.iloc[len(cage_litters) - 1]
            most_recent_litter_dob = most_recent_litter.get("litter_dob","")
            most_recent_litter_dob = date.fromisoformat(str(most_recent_litter_dob).strip())

            if len(cage_litters) > 0:
                days_since_last_litter = (today - most_recent_litter_dob).days

        # Dashboard warning logic
        parent_old = False
        no_recent_litter = False

        parent_old_threshold_days = 240

        if sire_age_days >= parent_old_threshold_days:
            parent_old = True

        if dame_age_days >= parent_old_threshold_days:
            parent_old = True

        recent_litter_threshold_days = 42

        if days_since_last_litter is None:
            no_recent_litter = True
        elif days_since_last_litter >= recent_litter_threshold_days:
            no_recent_litter = True

        if dame.get("mouse_sac_date", "") == "" and sire.get("mouse_sac_date", "") == "":
            no_longer_active = False
        else:
            no_longer_active = True

        status_multi = []
        status = "No Concerns"
        status_color = "#BDB2B2" 

        if parent_old:
            status_multi.append("Parents Getting Old")
            status = "Parents Getting Old"
            status_color = "#BCC9B7"

        if no_recent_litter:
            status_multi.append("No Recent Litter")
            status = "No Recent Litter"
            status_color = "#5A755F"

        if no_longer_active:
            status_multi.append("No Longer Active")
            status = "No Longer Active"
            status_color = "#FFFFFF"

        if current_litters != []:
            status_multi.append("Has Unweaned Litter")
            status = "Has Unweaned Litter"
            status_color = "#ABA5B6" 

        if weaning_needed:
            status_multi.append("Pups Ready to Wean")
            status = "Pups Ready to Wean"
            status_color = "#595365"

        dashboard_rows.append(
            {
                "breeding_cage": cage,
                "status_multi": status_multi,
                "status": status,
                "status_color": status_color,
                "sire_id": sire_id,
                "dame_id": dame_id,
                "sire_age_days": sire_age_days,
                "dame_age_days": dame_age_days,
                "sire_age_weeks": sire_age_weeks,
                "dame_age_weeks": dame_age_weeks,
                "sire_genotype": sire_genotype_label,
                "dame_genotype": dame_genotype_label,
                "sire_sac_date": sire.get("mouse_sac_date", ""),
                "dame_sac_date": dame.get("mouse_sac_date", ""),
                "parental_cross": parental_cross,
                "current_litters": current_litters,
                "pups_ready_to_wean": weaning_needed,
                "previous_litters": previous_litters,
                "days_since_last_litter": days_since_last_litter,
                "parent_old": parent_old,
                "no_recent_litter": no_recent_litter,
            }
        )

    return pd.DataFrame(dashboard_rows)

def show_breeding_status_key():
    html1 = """
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="
                width: 16px;
                height: 16px;
                background-color: #BCC9B7;
                border: 1px solid #999;
                border-radius: 2px;
            "></div>
            <span style="font-size: 14px;">
            <span>Getting Old</span>
        </div> """
    html2 = """
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="
                width: 16px;
                height: 16px;
                background-color: #5A755F;
                border: 1px solid #999;
                border-radius: 2px;
            "></div>
            <span style="font-size: 14px;">
            <span>No Recent Litter</span>
        </div>"""
    html3 = """
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="
                width: 16px;
                height: 16px;
                background-color: #FFFFFF;
                border: 1px solid #999;
                border-radius: 2px;
            "></div>
            <span style="font-size: 14px;">
            <span>No Longer Active</span>
        </div>"""
    html4 = """
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="
                width: 16px;
                height: 16px;
                background-color: #595365;
                border: 1px solid #999;
                border-radius: 2px;
            "></div>
            <span style="font-size: 14px;">
            <span>Ready to Wean</span>
        </div>"""
    html5 = """
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="
                width: 16px;
                height: 16px;
                background-color: #ABA5B6;
                border: 1px solid #999;
                border-radius: 2px;
            "></div>
            <span style="font-size: 14px;">
            <span>Current Litter</span>
        </div>"""
    html6 = """
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="
                width: 16px;
                height: 16px;
                background-color: #BDB2B2;
                border: 1px solid #999;
                border-radius: 2px;
            "></div>
            <span style="font-size: 14px;">
            <span>No Concerns</span>
        </div>"""

    col1, col2 = st.columns(2, gap = "xsmall")
    with col1:
        st.write(html4, unsafe_allow_html=True)
        st.write(html5, unsafe_allow_html=True)
        st.write(html6, unsafe_allow_html=True)
    with col2:
        st.write(html2, unsafe_allow_html=True)
        st.write(html1, unsafe_allow_html=True)
        st.write(html3, unsafe_allow_html=True)

def has_nonempty_list(x):
    if isinstance(x, list):
        return len(x) > 0

    if isinstance(x, tuple):
        return len(x) > 0

    if x is None:
        return False

    try:
        if pd.isna(x):
            return False
    except Exception:
        pass

    return False

# --------------------------------------------------
# Plotting
# -------------------------------------------------- 

def plot_bar(
    plot_df,
    x_col,
    y_col,
    x_label,
    y_label,
    color,
    figsize,
    rotate_labels,
):

    fig, ax = plt.subplots(figsize=figsize)

    bars = ax.bar(
        plot_df[x_col].astype(str),
        plot_df[y_col],
        color=color,
    )

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    max_y = plot_df[y_col].max() if len(plot_df) > 0 else 0
    ax.set_ylim(0, max(max_y + 1, 1))

    if rotate_labels:
        ax.tick_params(axis="x", labelrotation=45)
        for label in ax.get_xticklabels():
            label.set_horizontalalignment("right")

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            str(int(height)),
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return fig

def plot_pie(
    plot_df,
    label_col,
    value_col,
    title="",
    color_palette=None,
    min_label_pct=3,
    donut=True,
    show_total=True,
    figsize=(6, 5),
):
    df = plot_df.copy()

    if df.empty or label_col not in df.columns or value_col not in df.columns:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=12)
        ax.set_title(title)
        ax.axis("off")
        return fig

    df[value_col] = pd.to_numeric(df[value_col], errors="coerce").fillna(0)
    df = df[df[value_col] > 0].copy()

    if df.empty or df[value_col].sum() == 0:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No nonzero values", ha="center", va="center", fontsize=12)
        ax.set_title(title)
        ax.axis("off")
        return fig

    labels = df[label_col].astype(str).tolist()
    values = df[value_col].tolist()
    total = sum(values)

    def autopct_func(pct):
        if pct < min_label_pct:
            return ""
        return f"{pct:.1f}%"

    fig, ax = plt.subplots(figsize=figsize)

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        autopct=autopct_func,
        startangle=90,
        counterclock=False,
        colors=color_palette,
        pctdistance=0.75 if donut else 0.65,
        wedgeprops={
            "linewidth": 1,
            "edgecolor": "white",
            "width": 0.45 if donut else 1.0,
        },
    )

    legend_labels = [
        f"{label}: {value}"
        for label, value in zip(labels, values)
    ]

    ax.legend(
        wedges,
        legend_labels,
        title="Groups",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=8,
    )

    ax.set_title(title)
    ax.axis("equal")

    for autotext in autotexts:
        autotext.set_fontsize(8)
        autotext.set_color("white")
        autotext.set_weight("bold")

    if donut and show_total:
        ax.text(
            0,
            0,
            f"Total\n{int(total)}",
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
        )

    plt.tight_layout()
    return fig