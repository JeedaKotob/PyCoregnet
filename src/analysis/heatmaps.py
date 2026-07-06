import json
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go


def _prepare_coregs(GRN: dict):
    "Prepare the coregs for later use"
    from analysis.coregs import get_coregs

    # coregs, _ = get_coregs(GRN)
    coregs = pd.read_json("src/analysis/x.json")

    if coregs.empty:
        print(
            "No co-regulators in the provided network. If it was inferred with the hLICORN function, try a lower minCoregSupport."
        )
        # NOTE Add a feature for minCoregSupport
        return None

    # Gets the max ngrn
    max_thresh = coregs["nGRN"].max()
    # Find the threshold by rounding up  (max ngrn * 0.01)
    init_thresh = math.ceil(0.01 * max_thresh)
    # Filter the coreges by ngrn
    coregs = coregs[coregs["nGRN"] >= init_thresh]
    coregs = coregs[["Reg1", "Reg2"]]

    return coregs


def _process_subgroups(clinical_data: pd.Series, tf_activity: pd.DataFrame):

    # Number of common cols/samples in clinical_data & tf_activity
    n_common = clinical_data.index.isin(tf_activity.columns).sum()
    ncol = tf_activity.shape[1]

    # If Number of common samples > half the number of samples in tf activity
    if n_common > (0.5 * ncol):
        # If Number of common samples < number of samples in clinical data
        if n_common < len(clinical_data):
            # Sample Class = Clinical data + (missing tf_activity cols in clincal data)
            # The missing samples has a row of pd.NA in samples_class
            samples_class = clinical_data.reindex(tf_activity.columns)
        else:
            # NOTE is it the same thing above?
            # NOTE (Any sample that's in tf_activity.columns but not in clinical_data
            # is simply dropped, not filled with NA.)
            common_samples = clinical_data.index.intersection(tf_activity.columns)
            samples_class = clinical_data.loc[common_samples]

        # Converts subgroups into categories
        samples_class = samples_class[0].astype("category").cat.codes
        samples_class.replace(-1, pd.NA, inplace=True)  # ?????

        # Add a new subgroup "all" that will have the tfs in tf activity
        all_samples = pd.DataFrame(["all"] * tf_activity.shape[1]).set_index(
            tf_activity.columns
        )
        clinical_data = pd.concat([clinical_data, all_samples])

    else:
        clinical_data = pd.DataFrame(
            tf_activity.columns, columns=["all"]
        )  # TODO REVIEW
        samples_class = None

    return clinical_data, samples_class


class SpecificMutation:
    coregs: np.ndarray
    n_exp: pd.DataFrame
    tf_activity: pd.DataFrame
    alteration_data: pd.DataFrame | None
    clinical_data: pd.DataFrame

    def __init__(
        self,
        GRN: dict,
        numerical_exp: pd.DataFrame = None,  # TODO Remove it
        tf_activity: pd.DataFrame = None,
        alteration_data: pd.DataFrame = None,
        clinical_data: pd.DataFrame = None,
    ):

        # Either numerical_exp or tf_activity should be input as a parm
        if numerical_exp.empty and tf_activity.empty:
            raise ValueError("Add a return here")

        if not numerical_exp.empty:
            self.n_exp = numerical_exp

        # Get the coregs, also after filtering by ngrn thresh
        self.coregs = _prepare_coregs(GRN)
        # Find the intersection of the coregs and the tf actvity target genes
        self.coregs = np.intersect1d(self.coregs, tf_activity.index)

        # TODO should "if len(COREGS) < 5" be added ? ADD WARNING

        # Filter, now tf_activity.index == coregs
        self.tf_activity = tf_activity.loc[self.coregs]

        # Mutation data's idx and cols -> intersects -> tf_activity idx and cols
        if not alteration_data.empty:
            self.alteration_data, _ = alteration_data.align(tf_activity, join="inner")
            # TODO Should remove if>? #nx, ny = alteration_data.shape # if nx < 6 | ny < 10:

        if not clinical_data.empty:
            self.clinical_data, self.samples_class = _process_subgroups(
                clinical_data, self.tf_activity
            )

    def tf_plot(self, selected: str):
        
        if selected not in list(self.tf_activity.index):
            return None

        # Reprocess all the data so all have the same samples
        cmn_samples = self.tf_activity.columns
        if self.samples_class is not None:
            cmn_samples = cmn_samples.intersection(
                self.samples_class.index
            ).intersection(self.n_exp.columns)
        if self.alteration_data is not None:
            cmn_samples = cmn_samples.intersection(self.alteration_data.columns)
        if self.samples_class is not None:
            self.samples_class = self.samples_class.loc[cmn_samples]

        # Get tf activity of the selected
        selected_activity = self.tf_activity.loc[[selected], cmn_samples]

        # selected_activity = pd.DataFrame(selected_activity)

        # Sort TFA and NE

        selected_activity = selected_activity.sort_values(
            by=selected, axis=1, ascending=True
        )

        # selected_exp = self.n_exp.loc[selected, selected_activity.columns]

        # Get colors
        num_colors = max(max(self.samples_class.values), 4)  # org max(clinical,3)
        # Get the colormap
        cmap = plt.get_cmap("Set3")
        # Extract the specific number of hex colors
        hex_colors = [mcolors.to_hex(cmap(i)) for i in range(num_colors)]

        # Start with the heatmap
        maps = []

        if self.samples_class is not None:
            samples_class = self.samples_class.loc[selected_activity.columns]

            trace = go.Heatmap(
                z=np.atleast_2d(samples_class.to_numpy(dtype=float)),
                colorscale=hex_colors,
                showscale=True,
                colorbar=dict(title="Value"),
                x=selected_activity.columns,
                y=[2],
                xgap=0,
                ygap=0,
                hoverongaps=False,
            )
            maps.append(trace)

        if self.alteration_data is not None:
            if selected in self.alteration_data.index.values:
                tf_cna = self.alteration_data.loc[selected, selected_activity.columns]

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
                    y=[1],
                    xgap=0,
                    ygap=0,
                    hoverongaps=False,
                )
                maps.append(trace)

        if self.tf_activity is not None:
            # Equivalent to R:
            # image(as.matrix(data.frame("a" = tfA)), col = BR(20), main = paste(TF, "Influence"),
            # breaks = seq(min(tfA), max(tfA), by = (max(tfA) - min(tfA)) / 20), axes = FALSE)
            tf_a = selected_activity.loc[selected, selected_activity.columns].astype(
                float
            )
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
                y=[0],
                xgap=0,
                ygap=0,
                hoverongaps=False,
            )
            maps.append(trace)

        return maps





if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path

    # Allow running this file directly (e.g. `python heatmaps.py`) by putting
    # `src` on sys.path so the `analysis`/`services`/`config` packages resolve.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    # Data paths (config/paths.py) are relative to the project root, so make
    # sure that's the cwd regardless of where this script was launched from.
    os.chdir(Path(__file__).resolve().parents[2])

    from services import (
        load_grn,
        load_expression_matrix,
        load_alterationData,
        load_clinicalData,
        load_influence,
    )

    GRN = load_grn()
    CIT_BLCA_EXP = load_expression_matrix()
    CIT_BLCA_Subgroup = load_clinicalData()
    CIT_BLCA_CNV = load_alterationData()
    CITinf = load_influence()

    CIT_BLCA_Subgroup.columns = [0]  # TODO update data

    sm = SpecificMutation(
        GRN=GRN,
        numerical_exp=CIT_BLCA_EXP,
        tf_activity=CITinf,
        alteration_data=CIT_BLCA_CNV,
        clinical_data=CIT_BLCA_Subgroup,
    )

    maps = sm.tf_plot("SOX9")
    print(maps)
