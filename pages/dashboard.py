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
    "Group 3: Fmr1 Core Genotypes": [
        "Fmr1(+/y)",
        "Fmr1(-/y)",
        "Fmr1(+/+)",
        "Fmr1(+/-)",
        "Fmr1(-/-)",
        "Fmr1(flox/y)",
        "Fmr1(flox/+)",
        "Fmr1(flox/flox)",
    ],
    "Group 4: Fmr1 Pvalb-tdTomato": [
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
    "Group 5: Fmr1 flox x Cre": [
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
    "Group 6: OPN1": [
        "OPN1(+/+)",
        "OPN1(LW/+)",
        "OPN1(LW/MW)",
        "OPN1(LW/y)",
        "OPN1(MW/MW)",
        "OPN1(MW/y)",
        "OPN1(SW/+)",
        "OPN1(SW/SW)",
    ],
    "Group 7: Retina Degeneration": [
        "RD10(-/-)",
        "RD10(+/-)",
        "RhoP23H",
    ], 
}

# --------------------------------------------------
# Summary metrics
# --------------------------------------------------

overview_tab, cages_tab, mice_tab, breeding_tab = st.tabs(["Overview", "Experimental Cages", "Experimental Mice", "Breeding"], on_change="rerun")

genotype_choices = redcap_utils.get_genotypes()
genotype_rename_map = dict(
    zip(
        genotype_choices["variable"],
        genotype_choices["label"],
    )
)

if overview_tab.open:
    with overview_tab:
        overview.create_overview(df, current_df, current_experimental, current_breeding)

if cages_tab.open:
    with cages_tab:
        cages.create_cages(genotype_groups,current_experimental)

if breeding_tab.open:
    with breeding_tab:
        breeding.create_breeding(current_breeding)

if mice_tab.open: 
    with mice_tab:
        mice.create_mice(genotype_groups,current_experimental)