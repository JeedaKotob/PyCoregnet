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

import pandas as pd
import numpy as np

import plotly.graph_objects as go
from plotly.figure_factory._dendrogram import _Dendrogram
from plotly.subplots import make_subplots
from .heatmap import example_layout
# from .ps import xaxis,yaxis
dash.register_page(__name__, path='/dashboard/FixedHM')


filepath = "./CIT_BLCA_EXP.csv"
df = pd.read_csv(filepath,index_col=0)

genes = df.index.values
samples = df.columns.values
data = df.values.copy()

# For the X axis 
x_dendo = _Dendrogram(
    X=data,
    orientation="bottom",
    labels=genes,
)
x_order = x_dendo.leaves # Orders the data 
data = data[x_order,:] # Reorder the data before clustering in Y axis

# For the Y axis 
y_dendo = _Dendrogram(
    X=data.T, # Transpose the data so clustering happends for the y axis
    orientation="right",
    labels=samples,
)
y_order = y_dendo.leaves # Orders the data 
data = data[:,y_order] # Reorder the data

genes = genes[x_order]
samples = samples[y_order]

# Initialize figure for X axis, Will be main fig
# x_fig = go.Figure(data=x_dendo.data,layout=x_dendo.layout)
# x_fig.update_layout(xaxis=xaxis,yaxis=yaxis)

# Create Heatmap
heatmap = go.Heatmap(
    z=data.T,
    x=x_dendo.layout['xaxis']['tickvals'],
    y=y_dendo.layout['yaxis']['tickvals'],
    colorscale=[
        [0, "red"],   
        [0.5, "black"], 
        [1, "green"]   
    ]       
)

fig = go.Figure(layout=dict(autosize=True,width=None,height=None))
heatmap.colorbar = dict(x=1.05)  # Position the color bar to the far right
fig.add_trace(heatmap)

heatmap_height = max(y_dendo.layout['yaxis']['tickvals']) + 5
heatmap_width= max(x_dendo.layout['xaxis']['tickvals']) + 5

# Add X dendrogram traces
for trace in x_dendo.data:
    trace['y'] = trace['y']+ heatmap_height
    trace['showlegend'] = False  
    fig.add_trace(trace)


# Add Y dendrogram traces
for trace in y_dendo.data:
    trace['showlegend'] = False  
    fig.add_trace(trace)
    


layout = example_layout(dash.dcc.Graph(
    figure=fig,
    style={"flex": "1"}
))
