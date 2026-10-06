import streamlit as st
import redcap_utils
import pandas as pd

if "password" not in st.session_state:
    st.session_state["password"] = ""

st.set_page_config(
    page_title="Vlasits Colony Manager",
    layout="wide",
)

st.title("Vlasits Colony Manager")

if "redcap_df" not in st.session_state:
    st.session_state["redcap_df"] = redcap_utils.load_records()
if "mouse_info" not in st.session_state:
    st.session_state["mouse_info"] = pd.DataFrame(columns=st.session_state["redcap_df"].columns.tolist())
if "copy_button" not in st.session_state:
    st.session_state["copy_button"] = False
# --------------------------------------------------
# Define Pages
# --------------------------------------------------

dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True)
search = st.Page("pages/search_mice.py", title="Search Mice", icon=":material/search:")

# Mice
genotype = st.Page("pages/update_genotype.py", title="Genotype", icon=":material/genetics:")
sac = st.Page("pages/sac.py", title="Sac Mice", icon=":material/deceased:")
# separate = st.Page("pages/separate_cage.py", title="Separate Mice", icon=":material/move_down:")

# Breeding
breeding_dashboard = st.Page("pages/breeding_cages.py", title="Breeding Cages", icon=":material/widget_small:")
breeding_schemes = st.Page("pages/breeding_schemes.py", title="Breeding Schemes", icon=":material/genetics:")

# Ordering
create_cage = st.Page("pages/new_cage.py", title="Create New Cage", icon=":material/add_box:")

# Fully Hidden Pages
request = st.Page("pages/request_mice.py", visibility = "hidden")
request_unweaned = st.Page("pages/request_unweaned_litter.py", visibility = "hidden")
wean = st.Page("pages/wean_litter.py", visibility = "hidden")
new_litter = st.Page("pages/new_litter.py", visibility = "hidden")
visualize = st.Page("pages/mouse_visualization.py", visibility = "hidden")
experiment = st.Page("pages/perform_experiment.py", visibility = "hidden")
new_breeding_cage = st.Page("pages/new_breeding_cage.py", visibility = "hidden")
download_records = st.Page("pages/download_records.py", visibility = "hidden")

# --------------------------------------------------
# Create Menu
# --------------------------------------------------

nav_structure = {
    "": [dashboard, search, request],
    "Mice": [genotype, sac, visualize, experiment,download_records],
    "Breeding": [breeding_dashboard,new_breeding_cage,new_litter, breeding_schemes,wean, request_unweaned],
    "Cages": [create_cage],
}

pg = st.navigation(nav_structure,expanded=2)

password = ""
if st.session_state["password"] == "":
    password = st.text_input(
        "Access Password",
        type="password",
        width = 300,
    )
    if password == st.secrets["PASSWORD"]:
        st.session_state["password"] = password
        st.rerun()
    else:
        st.stop()

pg.run()

with st.sidebar:

    reload = st.button(
        "Reload Data from Redcap",
        width = "stretch")

    st.markdown(
        ":material/data_table: [Visit RedCap Database](https://www.redcap.ihrp.uic.edu/redcap_v16.0.30/DataEntry/record_status_dashboard.php?pid=18590)"
    )

    import streamlit as st

    caption_style = """
        <p style="
            font-size: 14px; 
            color: #808080; 
            line-height: 1.4;
        ">
            Vlasits Laboratory <br>
            Department of Ophthalmology <br>
            University of Illinois Chicago
        </p>
    """

    st.markdown(caption_style,unsafe_allow_html=True)

if reload:
    st.session_state["redcap_df"] = redcap_utils.load_records()