import dash
from dash import dcc, html, Input, Output, State, callback, no_update, callback_context,ctx,MATCH
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__, path='/')

layout = dbc.Container(className="p-0 m-0 h-100",children=[
    

    
])