import streamlit as st
import matplotlib.pyplot as plt
import redcap_utils

# --------------------------------------------------
# Create Cages Dashboard Tab
# --------------------------------------------------

def create_cages(current_experimental):
    st.subheader("Dashboard")

    cage_counts_df = (
        current_experimental
        .groupby("mouse_cage_number")
        .size()
        .reset_index(name="mouse_count")
        .sort_values(["mouse_count", "mouse_cage_number"], ascending=[False, True])
    )

    cage_counts_male = (
        current_experimental[current_experimental["mouse_sex"]=="male"]
        .groupby("mouse_cage_number")
        .size()
        .reset_index(name="mouse_count")
        .sort_values(["mouse_count", "mouse_cage_number"], ascending=[False, True])
    )

    cage_counts_female = (
        current_experimental[current_experimental["mouse_sex"]=="female"]
        .groupby("mouse_cage_number")
        .size()
        .reset_index(name="mouse_count")
        .sort_values(["mouse_count", "mouse_cage_number"], ascending=[False, True])
    )

    single_cage_numbers = cage_counts_df[
        cage_counts_df["mouse_count"] == 1
    ]["mouse_cage_number"].tolist()

    col1, col2, col3, col4, col5 = st.columns(5)
    st.divider()

    with col1:
        st.metric("Occupied Cages", len(cage_counts_df))
    with col2:
        avg_mice_per_cage = len(current_experimental) / len(cage_counts_df)
        st.metric("Avg Mice / Cage", f"{avg_mice_per_cage:.1f}")
    with col3:
        st.metric("Single-Housed Cages", len(single_cage_numbers))
    with col4:
        st.metric("Male Cages",len(cage_counts_male))
    with col5:
        st.metric("Female Cages",len(cage_counts_female))

    col1, col2 = st.columns([1.2,1])
    with col1:
        st.subheader("Occupancy Distribution")
        cage_hist_df = (
            cage_counts_df
            .groupby("mouse_count")
            .size()
            .reset_index(name="number_of_cages")
            .sort_values("mouse_count")
        )

        fig = redcap_utils.plot_bar(
            cage_hist_df,
            x_col="mouse_count",
            y_col="number_of_cages",
            x_label="Mice Per Cage",
            y_label="Number of Cages",
            color = "#527147",
            figsize = [8,4.5],
            rotate_labels=False
        )
        
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        st.subheader("Sex Distribution")

        legend_labels = [
            f"Female: {len(cage_counts_female)}",
            f"Male: {len(cage_counts_male)}",
        ]

        labels = ["Male Cages", "Female Cages"]
        values = [len(cage_counts_male), len(cage_counts_female)]
        colors = ["#B0C8A7", "#9FA1BC"]
        fig, ax = plt.subplots(figsize=(5, 5))

        wedges, texts, autotexts = ax.pie(
            values,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            wedgeprops={
                "linewidth": 1,
                "edgecolor": "white",
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

        ax.axis("equal")

        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color("white")
            autotext.set_weight("bold")

        st.pyplot(fig)
        plt.close(fig)
