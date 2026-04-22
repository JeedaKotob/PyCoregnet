import json
import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from analysis.coregs import get_coregs
from joblib import Memory

with open("./data/grn.json", "r") as f:
    grn = json.load(f)

CIT_BLCA_EXP = pd.read_csv("data/CIT_BLCA_EXP.csv", index_col=0)
CIT_BLCA_Subgroup = pd.read_csv("data/CIT_BLCA_Subgroup.csv", index_col=0)
CIT_BLCA_CNV = pd.read_csv("data/CIT_BLCA_CNV.csv", index_col=0)
CITinf = pd.read_csv("data/CITinf.csv", index_col=0)

memory = Memory("./.cache_dir", verbose=0)


@memory.cache
def get_coregs_cached(grn):
    # This calls your original slow function
    return get_coregs(grn)


# coregs, metadata = get_coregs_cached(grn)


def heatmap_prep(
    GRN: dict,
    numerical_exp: pd.DataFrame = None,  # TODO Remove it
    tf_activity: pd.DataFrame = None,
    alteration_data: pd.DataFrame = None,
    clinical_data: pd.DataFrame = None,
    notes: list = None,  # TODO Remove it
):

    # stop tf_activity or numerical_exp is needed
    # stop if not tf_activity get tf_activity

    # NOTE, add parms? Hardcoded?
    coregs, metadata = get_coregs_cached(GRN)

    if coregs.empty:
        print(
            "No co-regulators in the provided network. If it was inferred with the hLICORN function, try a lower minCoregSupport."
        )

    max_thresh = coregs["nGRN"].max()
    init_thresh = math.ceil(0.01 * max_thresh)  # NOTE Needs Review

    coregs = coregs[coregs["nGRN"] >= init_thresh]
    coregs = coregs[["Reg1", "Reg2"]]

    # Intersection of coregs and tf from tf_activity data
    COREGS = np.intersect1d(coregs, tf_activity.index)

    if len(COREGS) < 5:  # NOTE Needs Review
        print(
            "Too few co-regulators have a measure of influence making the interactive visualization both useless and difficult"
        )

    # Filter tf_activity data with new COREGS
    tf_activity = tf_activity.loc[COREGS]

    # Filter Alteration Data if present
    if alteration_data is not None:
        # Genes ∩ tfs
        common_idx = alteration_data.index.intersection(tf_activity.index)
        # mutation samples ∩ tf samples
        common_cols = alteration_data.columns.intersection(tf_activity.columns)
        alteration_data = alteration_data.loc[common_idx, common_cols]

        nx, ny = alteration_data.shape
        if nx < 6 | ny < 10:  # NOTE Needs Review
            print(
                "Very few samples or regulators in alteration data which will not be used"
            )
            alteration_data = None

    # Filter Clinical Data if present
    if clinical_data is not None:  # (Convert into dict???)
        clinical_data.columns = [
            0
        ]  # reset col name to prevent errors TODO make input verification
        # Number of common samples
        n_common = clinical_data.index.isin(tf_activity.columns).sum()
        ncol = tf_activity.shape[1]

        # If Number of common samples > half the number of samples in tf activity
        if n_common > (0.5 * ncol):
            # If Number of common samples < number of samples in clinical data
            if n_common < len(clinical_data):
                # NOTE in clinical_data: Index is samples, Groups in col1
                given_samples = clinical_data.index
                missing_samples = tf_activity.columns.difference(given_samples)
                samples_class = pd.DataFrame(
                    [pd.NA] * len(missing_samples), index=missing_samples
                )
                samples_class = pd.concat([clinical_data, samples_class])
                samples_class = samples_class.loc[tf_activity.columns]
            else:
                common_samples = clinical_data.index.intersection(tf_activity.columns)
                samples_class = clinical_data.loc[common_samples]

            # Converts subgroups into categories
            samples_class = samples_class[0].astype("category").cat.codes
            samples_class.replace(-1, pd.NA, inplace=True)

        all_samples = pd.DataFrame(["all"] * tf_activity.shape[1]).set_index(
            tf_activity.columns
        )
        clinical_data = pd.concat([clinical_data, all_samples])
    else:
        clinical_data = pd.DataFrame(tf_activity.columns)  # TODO REVIEW
        samples_class = None

    return tf_activity, alteration_data, clinical_data, samples_class


def heatplot(
    GRN: dict,
    selected: list,
    tf_activity: pd.DataFrame,
    numerical_exp: pd.DataFrame,
    alteration_data: pd.DataFrame,
    samples_class: pd.DataFrame,
):

    # Find common samples
    cmn_samples = set(tf_activity.columns)

    if samples_class is not None:
        cmn_samples = (
            set(samples_class.index) & set(numerical_exp.columns) & cmn_samples
        )

    if (
        alteration_data is not None
    ):  # No need for and (selected in alteration_data.values):
        cmn_samples = set(alteration_data.columns) & cmn_samples

    cmn_samples = list(cmn_samples)

    #  Filter by common samples
    if samples_class is not None:
        samples_class = samples_class.loc[cmn_samples]

    # NOTE SHOULD THE COLOR BE BEFORE OR AG
    # NOTE Check
    # Your 'clinical' variable logic
    num_colors = max(max(samples_class.values), 4)  # org max(clinical,3)
    # Get the colormap
    cmap = plt.get_cmap("Set3")
    # Extract the specific number of hex colors
    hex_colors = [mcolors.to_hex(cmap(i)) for i in range(num_colors)]

    # Get selected avtivity
    selected_activity = tf_activity.loc[selected, cmn_samples]

    assert len(selected) == 1  # TODO update below to handle more than one selected

    # Sort TFA and NE
    selected_activity = selected_activity.sort_values(
        by=selected, axis=1, ascending=True
    )

    selected_exp = numerical_exp.loc[selected, selected_activity.columns]
    tf = selected[0]

    # Sort if not none
    if samples_class is not None:
        samples_class = samples_class.loc[selected_activity.columns]

        trace = go.Heatmap(
            z=np.atleast_2d(samples_class.to_numpy(dtype=float)),
            colorscale=hex_colors,
            showscale=True,
            colorbar=dict(title="Value"),
            x=selected_activity.columns,
            y=["Clinical"],
            hoverongaps=False,
        )
        # 3. Define the Figure and Layout
        fig = go.Figure(data=[trace])

        fig.update_layout(
            title=f"Clinical - {selected}",
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        )

        # fig.show(renderer="browser")

    if alteration_data is not None:
        if tf in alteration_data.index.values:
            tf_cna = alteration_data.loc[tf, selected_activity.columns]

            # Match R breaks seq(-2.5, 2.5, by=1) with stepped colors.
            breaks = [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5]
            color_bins = ["#2b83ba", "#abdda4", "#ffffbf", "#fdae61", "#d7191c"]
            zmin, zmax = breaks[0], breaks[-1]
            span = zmax - zmin
            stepped_colorscale = []
            for i, color in enumerate(color_bins):
                left = (breaks[i] - zmin) / span
                right = (breaks[i + 1] - zmin) / span
                stepped_colorscale.append([left, color])
                stepped_colorscale.append([right, color])

            trace = go.Heatmap(
                z=np.atleast_2d(tf_cna.to_numpy(dtype=float)),
                colorscale=stepped_colorscale,
                zmin=zmin,
                zmax=zmax,
                showscale=True,
                colorbar=dict(title="Value"),
                x=selected_activity.columns,
                y=["Copy Number"],
                hoverongaps=False,
            )
            fig = go.Figure(data=[trace])

            fig.update_layout(
                title=f"{tf} Copy Number",
                xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            )

            fig.show(renderer="browser")

    if tf_activity is not None:
        # Equivalent to R:
        # image(as.matrix(data.frame("a" = tfA)), col = BR(20), main = paste(TF, "Influence"),
        # breaks = seq(min(tfA), max(tfA), by = (max(tfA) - min(tfA)) / 20), axes = FALSE)
        tf_a = selected_activity.loc[tf, selected_activity.columns].astype(float)
        tf_min = float(tf_a.min())
        tf_max = float(tf_a.max())
        if tf_min == tf_max:
            tf_min -= 0.5
            tf_max += 0.5

        breaks = np.linspace(tf_min, tf_max, 21)
        br20 = [
            mcolors.to_hex(plt.get_cmap("RdBu_r")(i)) for i in np.linspace(0, 1, 20)
        ]

        span = tf_max - tf_min
        stepped_colorscale = []
        for i, color in enumerate(br20):
            left = (breaks[i] - tf_min) / span
            right = (breaks[i + 1] - tf_min) / span
            stepped_colorscale.append([left, color])
            stepped_colorscale.append([right, color])

        trace = go.Heatmap(
            z=np.atleast_2d(tf_a.to_numpy(dtype=float)),
            colorscale=stepped_colorscale,
            zmin=tf_min,
            zmax=tf_max,
            showscale=True,
            colorbar=dict(title="Value"),
            x=selected_activity.columns,
            y=["Influence"],
            hoverongaps=False,
        )
        fig = go.Figure(data=[trace])

        fig.update_layout(
            title=f"{tf} Influence",
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        )

        fig.show(renderer="browser")


if __name__ == "__main__":
    tf_activity, alteration_data, clinical_data, samples_class = heatmap_prep(
        GRN=grn,
        numerical_exp=CIT_BLCA_EXP,
        tf_activity=CITinf,
        alteration_data=CIT_BLCA_CNV,
        clinical_data=CIT_BLCA_Subgroup,
    )

    heatplot(
        GRN=grn,
        selected=["SOX9"],
        tf_activity=tf_activity,
        numerical_exp=CIT_BLCA_EXP,
        alteration_data=alteration_data,
        samples_class=samples_class,
    )
