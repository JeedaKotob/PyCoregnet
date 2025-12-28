"""
This way is the best way to create a bicluter-dendogram heatmap

Default way : scipy.Pdist -> scipy.linkage -> scipy.dendogram
    - Pdist: calculate the distance "euclidean"
    - linkage : Perform hierarchical/agglomerative clustering.
    - Plot the hierarchical clustering as a dendrogram.
    - was hard to intergrate scipy to ploty so Default way is scrapped

Dash_bio : Slow, Cannot handle large data, outdated code with libary issue 

The way below is using plotly._Dendrogram
    - It is a wrapper of the Default way
    - Helps us get all the data we need 
    - More flexibility and less work 
    - https://plotly.com/python/dendrogram 
    
The _Dendrogram returns alot of data
    - We want the _Dendrogram.data for creating the figure
    - We want the _Dendrogram.layout for the figure
    - We want the _Dendrogram.leaves for the heatmap
        - _Dendrogram.leaves is a list of orderd indexes
        - that are already gone through the clustering process
    
    
"""
import dash
from dash import Input, Output, State, callback, Patch, no_update, clientside_callback, ClientsideFunction, html

import pandas as pd
import numpy as np

import plotly.graph_objects as go
from plotly.figure_factory._dendrogram import _Dendrogram
from plotly.subplots import make_subplots
from .heatmap import example_layout,render_layout
# from .ps import xaxis,yaxis
dash.register_page(__name__, path='/heatmaps/dynamic')

filepath = "./CIT_BLCA_EXP.csv"
df = pd.read_csv(filepath,index_col=0)

genes = df.index.values
samples = df.columns.values
data = df.values.copy()

# For the X axis 
x_dendo = _Dendrogram(
    X=data,
    orientation="bottom", # The end branch of the dendogram points downward
    labels=genes,
)
x_order = x_dendo.leaves # Order of the clusterd data 
data = data[x_order,:] # Reorder the data before clustering in Y axis

# For the Y axis 
y_dendo = _Dendrogram(
    X=data.T, # Transpose the data so clustering happends for the y axis
    orientation="right", # The end branch of the dendogram points to the right
    labels=samples,
)
y_order = y_dendo.leaves # Order of the clusterd data 
data = data[:,y_order] # Reorder the data
# NOTE data the entire data is reordered...
#...but it needs to be transposed for the Heatmap

# tickvals is the numerical tick of the graph
# ticktext is the categorical tick of the graph
x_tickvals = x_dendo.layout['xaxis']['tickvals'] 
x_ticktext = x_dendo.layout['xaxis']['ticktext']

y_tickvals = y_dendo.layout['yaxis']['tickvals']
y_ticktext = y_dendo.layout['yaxis']['ticktext']

# For tick handling
len_x_tick = len(x_tickvals)
len_y_tick = len(y_ticktext)


#  This is done for the hover over the heatmap
#  This is manual, defualt way is causing problems
#  Ticklabels are done manually...see end of page
customdata = np.stack(np.meshgrid(x_ticktext, y_ticktext), axis=-1) # for hovertemplate

# Create Heatmap
heatmap = go.Heatmap(
    z=data.T,
    x=x_dendo.layout['xaxis']['tickvals'],
    y=y_dendo.layout['yaxis']['tickvals'],
    customdata=customdata,
    hovertemplate='Gene: %{customdata[0]}<br>Sample: %{customdata[1]}<br>Value: %{z}<extra></extra>',
    colorscale=[
        [0, "red"],   
        [0.5, "black"], 
        [1, "green"]   
    ],
    colorbar=dict( # Responsible to put the bar above the figure
        orientation='h',
        y=1,
        yanchor='bottom',
        x=0,
        xanchor='left'
    ),
)


# Create a subplot with dendrograms and heatmap
fig = make_subplots(
    rows=2, cols=2,
    shared_xaxes = True,
    shared_yaxes = True,
    vertical_spacing=0,
    horizontal_spacing=0,
    row_heights=[0.2, 0.8],  # Adjust heights for dendrogram and heatmap
    column_widths=[0.1, 0.9],  # Adjust widths for dendrogram and heatmap
)

# Add the X dendrogram to the top of the heatmap
for trace in x_dendo.data:
    trace['showlegend'] = False  
    fig.add_trace(trace, row=1, col=2)

# Add the Y dendrogram to the right of the heatmap
for trace in y_dendo.data:
    trace['showlegend'] = False  
    fig.add_trace(trace, row=2, col=1)

# Add the heatmap to the center
fig.add_trace(heatmap, row=2, col=2)

# Update layout for better appearance
fig.update_layout(
    autosize=True,
    # margin=dict(l=0, r=0, t=0, b=0),
    # margin=dict(l=20),
    xaxis=dict(showticklabels=False),
    yaxis=dict(showticklabels=False),
    xaxis2=dict(showticklabels=False),
    yaxis2=dict(showticklabels=False, fixedrange=True), # fixedrange : Fixes the dendogram with the heatmap
    xaxis3=dict(showticklabels=False, fixedrange=True), # also only works for numerical ticks --> forced to make manual adjustments 
    yaxis3=dict(showticklabels=False),
)



# Calculate step size to limit number of ticks displayed
# xstep = ystep =20

# fig.update_layout(
#     xaxis4=dict(
#         tickvals=x_tickvals[::xstep],
#         ticktext=x_ticktext[::xstep],
#         showticklabels=True
#     ),
#     yaxis4=dict(
#         tickvals=y_tickvals[::ystep],
#         ticktext=y_ticktext[::ystep],
#         showticklabels=True,
#         side="right"
#     )
# )

fig.update_layout(
    xaxis4=dict(
        tickvals=x_tickvals,
        ticktext=x_ticktext,
        showticklabels=False
    ),
    yaxis4=dict(
        tickvals=y_tickvals,
        ticktext=y_ticktext,
        showticklabels=False,
        side="right"
    )
)






layout = example_layout(dash.dcc.Graph(
    id="dynamic-heatmap-graph",
    figure=fig,
    style={"flex": "1"},
    responsive=True,
    config={
        'displayModeBar': False
    }
))


# layout = render_layout(dash.dcc.Graph(
#     id="dynamic-heatmap-graph",
#     figure=fig,
#     style={"flex": "1"},
#     responsive=True,
#     config={
#         'displayModeBar': False
#     }
# ))