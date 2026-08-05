import streamlit as st
import matplotlib.pyplot as plt
import redcap_utils

# --------------------------------------------------
# Create Cages Dashboard Tab
# --------------------------------------------------
def plot_genotype_group_bar(
    df,
    genotype_list,
    genotype_col="mouse_genotype",
):

    plot_df = df.copy()
    plot_df["genotype_label"] = (plot_df[genotype_col])

    # Keep only genotypes in this group
    plot_df = plot_df[plot_df["genotype_label"].isin(genotype_list)]

    counts_df = (
        plot_df
        .groupby("genotype_label")
        .size()
        .reset_index(name="count")
    )
    y_label = "Number of Mice"

    # Preserve the genotype order from genotype_list
    ordered_counts_df = (
        counts_df
        .set_index("genotype_label")
        .reindex(genotype_list, fill_value=0)
        .reset_index()
    )

    if ordered_counts_df.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 3))

    ax.bar(
        ordered_counts_df["genotype_label"],
        ordered_counts_df["count"],
        color="#BDB2B2",
        edgecolor="white",
        linewidth=0.8,
    )

    ax.set_ylabel(y_label)

    # This is the key part: x-axis labels are the genotype labels
    ax.set_xticks(range(len(ordered_counts_df["genotype_label"])))
    ax.set_xticklabels(
        ordered_counts_df["genotype_label"],
        rotation=45,
        ha="right",
        fontsize=9,
    )

    ax.tick_params(axis="y", labelsize=8)

    # Add count labels above bars
    for i, value in enumerate(ordered_counts_df["count"]):
        ax.text(
            i,
            value,
            str(value),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()

    return fig

def create_mice(genotype_groups, current_experimental):
    st.subheader("Dashboard")

    mouse_counts_male = (len(current_experimental[current_experimental["mouse_sex"] == "male"]))
    mouse_counts_female = (len(current_experimental[current_experimental["mouse_sex"] == "female"]))
    mouse_counts_available = (len(current_experimental[current_experimental["flag"] == "available"]))

    col1, col2, col3, col4 = st.columns(4)
    st.divider()

    with col1:
        st.metric("Current Experimental Mice", len(current_experimental))

    with col2:
        st.metric("Male Mice", mouse_counts_male)

    with col3:
        st.metric("Female Mice", mouse_counts_female)

    with col4:
            st.metric("Available Mice", mouse_counts_available)


    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Sex Distribution")

        labels = ["Male Mice", "Female Mice"]
        values = [mouse_counts_male, mouse_counts_female]
        colors = ["#BCC9B7", "#ABA5B6"]

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

    with col2:
        st.subheader("Source Distribution")

        # Change this column name if needed
        source_col = "mouse_source"

        if source_col in current_experimental.columns:
            source_df = current_experimental.copy()

            source_df[source_col] = (
                source_df[source_col]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .str.lower()
            )

            source_counts_df = (
                source_df
                .groupby(source_col)
                .size()
                .reset_index(name="mouse_count")
                .sort_values("mouse_count", ascending=False)
            )

            # Optional: standardize source labels
            source_label_map = {
                "bred": "Bred",
                "cryrecovered": "Cryrecovered",
                "cryo recovered": "Cryrecovered",
                "cryo-recovered": "Cryrecovered",
                "hyde lab": "Hyde Lab",
                "jackson lab": "Jackson Lab",
                "jax": "Jackson Lab",
                "rederivation": "Rederivation",
                "unknown": "Unknown",
            }

            source_counts_df["source_label"] = source_counts_df[source_col].map(
                source_label_map
            ).fillna(source_counts_df[source_col].str.title())

            # Re-group after label cleanup in case multiple raw values map to same label
            source_counts_df = (
                source_counts_df
                .groupby("source_label")["mouse_count"]
                .sum()
                .reset_index()
                .sort_values("mouse_count", ascending=False)
            )

            source_labels = source_counts_df["source_label"].tolist()
            source_values = source_counts_df["mouse_count"].tolist()

            if sum(source_values) > 0:
                source_colors = [
                    "#BCC9B7",
                    "#ABA5B6",
                    "#BDB2B2",
                    "#595365",
                    "#5A755F",
                ]

                fig, ax = plt.subplots(figsize=(5, 5))

                wedges, texts, autotexts = ax.pie(
                    source_values,
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=source_colors[:len(source_values)],
                    wedgeprops={
                        "linewidth": 1,
                        "edgecolor": "white",
                    },
                )

                legend_labels = [
                    f"{label}: {value}"
                    for label, value in zip(source_labels, source_values)
                ]

                ax.legend(
                    wedges,
                    legend_labels,
                    title="Sources",
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
            else:
                st.info("No source data available.")
        else:
            st.warning(f"Column `{source_col}` was not found in the dataframe.")
    

    st.divider()
    st.subheader("Genotype Distribution")
    st.markdown("")

    genotype_choices = redcap_utils.get_genotypes()
    genotype_variable_to_label = dict(
        zip(
            genotype_choices["variable"],
            genotype_choices["label"],
        )
    )

    current_experimental["genotype_label"] = (
        current_experimental["mouse_genotype"]
        .map(genotype_variable_to_label)
        .fillna(current_experimental["mouse_genotype"])
    )

    genotype_col = "genotype_label"
    cage_col = "mouse_cage_number"

    for i, (group_name, genotype_list) in enumerate(genotype_groups.items()):
        group_expander = st.expander(
            f"**{group_name}**"
        )
        with group_expander:
            st.markdown(f"**{group_name}**")
            fig = plot_genotype_group_bar(
                current_experimental,
                genotype_list=genotype_list,
                genotype_col=genotype_col,
            )

            st.pyplot(fig)
            plt.close(fig)