import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import Dash, Input, Output, State, callback, callback_context, ctx, dcc, html, MATCH, ALL, no_update

from assets import stylesheet
from functools import partial
from graph import fullbipartite
from layout.baselayout import BaseNetworkGraph
from layout.base import NetworkLayout
import utils

import plotly.graph_objects as go
import pandas as pd
import numpy as np

dash.register_page(__name__, path='/dashboard/heatmap')




def get_heat_map(filepath = "./CIT_BLCA_EXP.csv"):

    ne=pd.read_csv(filepath,index_col=0)
    selected_df = ne.T
    
    global_mean=ne.values.mean()
    z_scores=selected_df-global_mean
    zmin = z_scores.min().min()
    zmax = z_scores.max().max()

    n_genes = len(z_scores.columns)
    n_samples = len(z_scores.index)
    
    heatmap_width = min(1000, max(300, 20 * n_genes))
    heatmap_height = min(900, max(300, 20 * n_samples))

    heatmap=go.Figure(
        layout=dict(
            autosize=True,
            width=None,
            height=None
        ),
        data=go.Heatmap(
        z=z_scores.values,
        x=z_scores.columns,
        y=z_scores.index,
        zmin=zmin,
        zmax=zmax,
        colorscale=[
            [0, "red"],   
            [0.5, "black"], 
            [1, "green"]   
        ]
    ))
    heatmap.update_layout(
        xaxis=dict(
            showticklabels=True,
            tickmode='array',
            # tickangle=45  # Adjust angle for better visibility
        ),
        yaxis=dict(
            showticklabels=True,
            tickmode='array',
            
            
        ),
        xaxis_title="Genes",
        yaxis_title="Samples"
    )
    
    return dcc.Graph(
        figure=heatmap,
        style={"flex": "1"}
    )


hm = get_heat_map() 

# hm = html.Div(
#     className="d-flex justify-content-center align-items-center h-100",
#     children=hm
# )


# network_layout = NetworkLayout(
    # graph=hm,
    # network_controls=html.Div()
# )

layout = html.Div()

# layout = network_layout.render_layout()