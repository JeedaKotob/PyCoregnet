"""To Best Understand this module, start with SpecificMutation class"""

import math

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from plotly.subplots import make_subplots


def _prepare_coregs(GRN: dict):
    "Prepare the coregs for later use"

    testing = False

    if testing:
        print("NOTE: coregs are hardcoded")
        coregs = pd.read_json("src/analysis/x.json")
    else:
        from analysis.coregs import get_coregs

        coregs, _ = get_coregs(GRN)

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

        # Above is preprocessing
        # Jump to get_graph() to understand better

    @staticmethod
    def _create_stepped_colorscale(
        breaks: list, colors: list, zmin: float, zmax: float
    ) -> list:
        """Create a stepped colorscale from breaks and colors."""
        span = zmax - zmin
        stepped_colorscale = []
        for i, color in enumerate(colors):
            left = (breaks[i] - zmin) / span
            right = (breaks[i + 1] - zmin) / span
            stepped_colorscale.append([left, color])
            stepped_colorscale.append([right, color])
        return stepped_colorscale

    def _create_expression_trace(
        self,
        selected: list,
        selected_activity: pd.DataFrame,
        x_vals,
        y: list,
        transpose: bool = False,
    ) -> go.Heatmap:
        """Create expression heatmap trace."""
        selected_exp = self.n_exp.loc[selected, selected_activity.columns]

        global_mean = self.n_exp.values.mean()
        z_scores = selected_exp - global_mean
        zmin = float(z_scores.to_numpy().min())
        zmax = float(z_scores.to_numpy().max())

        z_values = z_scores.to_numpy(dtype=float)
        if transpose:
            z_values = z_values.T

        return go.Heatmap(
            z=z_values,
            x=x_vals,
            y=y,
            zmin=zmin,
            zmax=zmax,
            colorscale=[[0, "red"], [0.5, "black"], [1, "green"]],
            showscale=False,
            xgap=0,
            ygap=0,
            hoverongaps=False,
        )

    def _create_samples_class_trace(self, x_vals, y: list) -> go.Heatmap:
        """Create samples class heatmap trace."""
        samples_class = self.samples_class.loc[x_vals]
        return go.Heatmap(
            z=np.atleast_2d(samples_class.to_numpy(dtype=float)),
            showscale=False,
            x=x_vals,
            y=y,
            xgap=0,
            ygap=0,
            hoverongaps=False,
        )

    def _create_alteration_trace(
        self,
        selected_activity: pd.DataFrame,
        x_vals,
        y: list,
        transpose: bool = False,
    ) -> go.Heatmap:
        """Create alteration data heatmap trace."""
        tf_cna = self.alteration_data.loc[
            selected_activity.index, selected_activity.columns
        ]

        z_values = tf_cna.to_numpy(dtype=float)
        if transpose:
            z_values = z_values.T

        return go.Heatmap(
            z=z_values,
            showscale=False,
            x=x_vals,
            y=y,
            xgap=0,
            ygap=0,
            hoverongaps=False,
        )

    def _create_tf_activity_trace(
        self, selected: list, selected_activity: pd.DataFrame, x_vals, y: list
    ) -> go.Heatmap:
        """Create TF activity heatmap trace with stepped colorscale."""
        tf_a = selected_activity.loc[selected, selected_activity.columns].astype(float)

        tf_min = float(tf_a.min().min())
        tf_max = float(tf_a.max().max())
        if tf_min == tf_max:
            tf_min -= 0.5
            tf_max += 0.5

        # Create 20 breaks and corresponding colors
        breaks = np.linspace(tf_min, tf_max, 21)
        br20 = [
            mcolors.to_hex(plt.get_cmap("RdBu_r")(i)) for i in np.linspace(0, 1, 20)
        ]

        stepped_colorscale = self._create_stepped_colorscale(
            breaks, br20, tf_min, tf_max
        )

        return go.Heatmap(
            z=np.atleast_2d(tf_a.to_numpy(dtype=float)),
            colorscale=stepped_colorscale,
            zmin=tf_min,
            zmax=tf_max,
            showscale=False,
            x=x_vals,
            y=y,
            xgap=0,
            ygap=0,
            hoverongaps=False,
        )

    def _filter_and_prepare_data(self, selected: list) -> tuple:
        """Filter, validate, and prepare data for plotting. Returns selected TFs and common samples."""
        # Check if any of the selected are in the tf_activity.index / tfs
        selected = [sel for sel in selected if sel in list(self.tf_activity.index)]

        if not selected:
            return None, None

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

        return selected, cmn_samples

    def get_single_tf_figure(
        self,
        selected: list,
        selected_activity: pd.DataFrame,
    ) -> go.Figure:
        """Create traces for a single selected TF."""
        fig = go.Figure()

        # Add traces for expression data
        if self.n_exp is not None:
            fig.add_trace(
                self._create_expression_trace(
                    selected=selected,
                    selected_activity=selected_activity,
                    x_vals=selected_activity.columns,
                    y=[3],
                )
            )

        # Add traces for samples class
        if self.samples_class is not None:
            fig.add_trace(
                self._create_samples_class_trace(
                    x_vals=selected_activity.columns,
                    y=[2],
                )
            )

        # Add traces for alteration data
        if self.alteration_data is not None:
            fig.add_trace(
                self._create_alteration_trace(
                    selected_activity=selected_activity,
                    x_vals=selected_activity.columns,
                    y=[1],
                )
            )

        # Add traces for TF activity
        if self.tf_activity is not None:
            fig.add_trace(
                self._create_tf_activity_trace(
                    selected=selected,
                    selected_activity=selected_activity,
                    x_vals=selected_activity.columns,
                    y=[0],
                )
            )

        return fig

    def get_graph(self, selected: list):
        """Create and return heatmap traces for the selected transcription factors."""
        # Prepare and validate data
        # Filter/Find the common selected nodes and the common samples
        selected, cmn_samples = self._filter_and_prepare_data(selected)
        if selected is None:
            return None

        # Get tf activity of the selected and sort
        selected_activity = self.tf_activity.loc[selected, cmn_samples]
        selected_activity = selected_activity.sort_values(
            by=selected, axis=1, ascending=True
        )

        # Handle single TF selection
        if len(selected) == 1:
            fig = self.get_single_tf_figure(
                selected=selected,
                selected_activity=selected_activity,
            )
            fig.update_layout(
                dragmode="pan",
                margin={"t": 0, "b": 0, "l": 0, "r": 0},
                yaxis={
                    "type": "linear",
                    "range": [-0.5, 3.5],
                    "tickmode": "array",
                    "tickvals": [3, 2, 1, 0],
                    "ticktext": ["Expression", "Clinical", "Copy Number", "Influence"],
                },
            )
            fig.update_xaxes(showgrid=False, zeroline=False)
            fig.update_yaxes(showgrid=False, zeroline=False)

        else:
            fig = make_subplots(
                rows=1,
                cols=2,
                shared_yaxes=True,
                horizontal_spacing=0.08,
                column_widths=[0.5, 0.5],
            )

            fig.add_trace(
                self._create_alteration_trace(
                    selected_activity=selected_activity,
                    x_vals=selected,
                    y=selected_activity.columns,
                    transpose=True,
                ),
                row=1,
                col=1,
            )

            fig.add_trace(
                self._create_expression_trace(
                    selected=selected,
                    selected_activity=selected_activity,
                    x_vals=selected,
                    y=selected_activity.columns,
                    transpose=True,
                ),
                row=1,
                col=2,
            )

            fig.update_layout(
                height=max(600, 30 * len(selected_activity.columns)),
                margin={"t": 60, "b": 65, "l": 90, "r": 20},
                showlegend=False,
            )

        return fig


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
        load_alterationData,
        load_clinicalData,
        load_expression_matrix,
        load_grn,
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

    figure = sm.get_graph(selected=["SOX9", "FOXQ1"])
    if figure is not None:
        app = Dash(__name__)
        app.layout = html.Div(
            dcc.Graph(
                id="mutation-figure",
                figure=figure,
                style={"height": "95vh"},
                config={"displayModeBar": True},
            ),
            style={"width": "100%", "height": "100vh"},
        )
        app.run(debug=True, port=8051)
