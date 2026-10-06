import streamlit as st

import pages.create_cage_tabs.separate_cage as s_c
import pages.create_cage_tabs.internal_transfer as i_t
import pages.create_cage_tabs.new_cryorecovery as n_c
import pages.create_cage_tabs.new_jax_order as n_j_o
import pages.create_cage_tabs.new_rederivation as n_r


st.subheader("New Cage Creation")
st.markdown("")

with st.sidebar:
    status_container = st.container()

separate, internal_transfer, jax_order, rederivation, cryorecovery, blank = st.tabs(
    ["Separate Mice", "Internal Transfer", "Jackson Labs Order", "Rederivation", "Cryorecovery", " "], 
    on_change="rerun",
    default = " ",)

with blank:
    st.markdown("")
    st.caption("Select type of new cage addition to open relevant form")

if internal_transfer.open:
    with internal_transfer:
        i_t.create_internal_transfer()

if jax_order.open:
    with jax_order:
        n_j_o.new_jax_order()

if rederivation.open:
    with rederivation:
        n_r.new_rederivation()