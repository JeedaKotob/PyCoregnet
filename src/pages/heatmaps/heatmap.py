"""
Heatmap for the Entire Expression

? - Z - score ()
? - Bi Clustering
? - ggplot2/dendrogram
? - Clustergram
? - Hierarchical clustering
? - MinMaxScaler


1)Standerize the data
2)


    mu = raw.mean()
    std = raw.std() 
    z = ( (raw - mu) / std )
    
    data_ordered = (raw - raw.mean(axis=1, keepdims=True)) / (raw.std(axis=1, keepdims=True) + 1e-10)

    z_score = zscore(raw)
    


"""

import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import Dash, Input, Output, State, callback, callback_context, ctx, dcc, html, MATCH, ALL, no_update

from assets import stylesheet
from functools import partial
from graph import fullbipartite

import utils

import plotly.graph_objects as go
import pandas as pd
import numpy as np

dash.register_page(__name__, path='/heatmaps/Heatmap')

"""
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
"""


def example_layout(content):
    
    split = True
    split = False
    
    return dbc.Container(
            fluid=True,
            className="p-0 m-0 h-100",
            children=[
            dbc.Row(
                className="g-0 h-100",  # g-0 removes gutters, h-100 for full height
                children=[
                # Main content area - 75% (width 9) nneds to be on the left
                dbc.Col(
                    id={"type" : "main-content"},
                    width=9,
                    className="d-flex flex-column overflow-hidden p-2",
                    children=content
                ),
                # Sidebar area - 25% (width 3)
                # dbc.Col(
                #     width=3,
                #     className="bg-secondary text-white p-3 h-100 overflow-auto bg-danger",
                #     children=[html.Div("")]
                    
                # )
                ] if split else content
            )
            ]
        )
    
    
# layout = example_layout(get_heat_map())



##########################################################################################
filepath = "./CIT_BLCA_EXP.csv"
df = pd.read_csv(filepath,index_col=0)


"""
import plotly.figure_factory as ff


df_z = (df - df.mean()) / df.std()

from sklearn.cluster import AgglomerativeClustering

clustering = AgglomerativeClustering(
    n_clusters=None,
    metric='euclidean',
    memory=None,
    connectivity=None,
    compute_full_tree='auto',
    linkage='ward',
    distance_threshold=0,
    compute_distances=True
)
clustering = clustering.fit(df_z.values)


from scipy.cluster.hierarchy import linkage

xrows = linkage(
    df.values,
    method='single',
    metric='euclidean',
    optimal_ordering=False
)

ycols = linkage(
    df.values.T,
    method='single',
    metric='euclidean',
    optimal_ordering=False
)

for row in xrows:
    print(f"0:{row[0]} - 1:{row[1]} = {row[2]}, index?{row[3]}")


"""
##########################################################################################
filepath = "./CIT_BLCA_EXP.csv"
df = pd.read_csv(filepath,index_col=0)

"""
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import pdist
from scipy.stats import zscore


# Shuffle the indices of the dataframe
df = df.sample(frac=1, random_state=42)

data = df.values
genes = df.index.values
samples = df.columns.values

data = zscore(data)

# Col
tmp = np.transpose(data)
dcol = pdist(tmp,metric=("euclidean"))
zcol = linkage(
    dcol,
    optimal_ordering=False
)
y_order = leaves_list(zcol)
samples = samples[y_order]

# Row
drow = pdist(data,metric=("euclidean"))
zrow = linkage(
    drow,
    optimal_ordering=False
)
x_order = leaves_list(zrow)
genes = genes[x_order]

data = data[x_order].T[y_order].T

heatmap=go.Figure(
    layout=dict(
        autosize=True,
        width=None,
        height=None
    ),
    data=go.Heatmap(
    z=data.T,
    x=genes,
    y=samples,
    # zmin=zmin,
    # zmax=zmax,
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

layout = example_layout(dcc.Graph(
    figure=heatmap,
    style={"flex": "1"}
))
"""

##########################################################################################
from scipy.stats import zscore


filepath = "./CIT_BLCA_EXP.csv"
df = pd.read_csv(filepath,index_col=0).T

"""
clustergram = dashbio.Clustergram(
    data=df.values,
    row_labels=df.index.tolist(),        # Labels from dataframe index
    column_labels=df.columns.tolist(),   # Labels from dataframe columns
    standardize='zscore',                # Z-score normalization (preprocessing)
    color_map=[
        [0, "red"],   
        [0.5, "black"], 
        [1, "green"]   
    ]
)

clustergram.update_layout(
    autosize=True,
    height=None,
    width=None
)



layout = example_layout(dcc.Graph(
    figure=clustergram,
    style={"flex": "1"}
))

from plotly.figure_factory._dendrogram import _Dendrogram

from plotly.figure_factory import create_dendrogram
from scipy.cluster.hierarchy import dendrogram


dfig = create_dendrogram(
    
)

"""







##########################################################################################

"""

def bicluster_data(df : pd.DataFrame):
    
    from scipy.cluster import hierarchy as sch

    #  Standarize
    raw = df.values.copy()    
    z_score = (raw - raw.mean(axis=1, keepdims=True)) / (raw.std(axis=1, keepdims=True) + 1e-10)

    def per(axis):
        # Find the distance
        dist = sch.distance.pdist(axis, metric='euclidean')
        distfun = lambda X : sch.distance.pdist(X,metric='euclidean')
        
        # Get the linkage matriz
        linkage = sch.linkage(dist, metric='euclidean')
                
        # Dendro
        if True:
            dendro = sch.dendrogram(linkage, no_plot=True)
            order = dendro['leaves']
        else:
            order = sch.leaves_list(linkage)
        
        return order
    
            
        
    
    xorder = per(z_score)
    yorder = per(np.transpose(z_score))
    
    bicluster = z_score[xorder][:,yorder]
    
    return bicluster

"""

##########################################################################################
from scipy.stats import zscore
import numpy as np
from scipy import spatial as scs
from scipy.cluster import hierarchy as sch
from copy import copy
        
"""
def get_ordered_matrix(
    data,
    row_dist="euclidean",
    col_dist="euclidean",
    dist_fun=scs.distance.pdist,
    link_fun=None,
    link_method="complete",
    cluster="all",
    standardize="none"
):

    # Create shallow copy of data
    data_ordered = copy(np.array(data, dtype=float))
    
    # Standardization
    if standardize.lower() == 'row':
        data_ordered = (data_ordered - data_ordered.mean(axis=1, keepdims=True)) / (data_ordered.std(axis=1, keepdims=True) + 1e-10)
    elif standardize.lower() == 'column':
        data_ordered = (data_ordered - data_ordered.mean(axis=0, keepdims=True)) / (data_ordered.std(axis=0, keepdims=True) + 1e-10)
    
    # Handle NaN values
    data_ordered = np.nan_to_num(data_ordered, nan=0.0)
    
    # Set up linkage function
    if link_fun is None:
        def link_fun(x, **kwargs):
            return sch.linkage(x, link_method, **kwargs)
    
    # Cluster rows
    if cluster.lower() in ['row', 'all']:
        row_dist_array = dist_fun(data_ordered, metric=row_dist)
        row_linkage = link_fun(row_dist_array, metric=row_dist)
        
        # Get dendrogram leaf order
        dendro_row = sch.dendrogram(row_linkage, no_plot=True)
        row_order = dendro_row['leaves']
        
        # Reorder rows
        data_ordered = data_ordered[row_order, :]
    
    # Cluster columns
    if cluster.lower() in ['col', 'all']:
        # Transpose for column clustering
        data_t = data_ordered.T
        col_dist_array = dist_fun(data_t, metric=col_dist)
        col_linkage = link_fun(col_dist_array, metric=col_dist)
        
        # Get dendrogram leaf order
        dendro_col = sch.dendrogram(col_linkage, no_plot=True)
        col_order = dendro_col['leaves']
        
        # Reorder columns
        data_ordered = data_ordered[:, col_order]
    
    return data_ordered
"""



def get_ordered_matrix(
    data,
    row_dist="euclidean",
    col_dist="euclidean",
    dist_fun=scs.distance.pdist,
    link_fun=None,
    link_method="complete",
    cluster="all",
    standardize="none"
):
    """
    Get the ordered matrix from clustering using scipy's low-level functions.
    
    Parameters:
    -----------
    data : array-like
        2D input data matrix
    row_dist : str
        Distance metric for rows (default: 'euclidean')
    col_dist : str
        Distance metric for columns (default: 'euclidean')
    dist_fun : callable
        Distance function (default: scipy.spatial.distance.pdist)
    link_fun : callable, optional
        Linkage function (default: None, uses link_method)
    link_method : str
        Linkage method if link_fun is None (default: 'complete')
    cluster : str
        Clustering dimension: 'row', 'col', or 'all' (default: 'all')
    standardize : str
        Standardization: 'none', 'row', or 'column' (default: 'none')
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'ordered_data': The reordered matrix
        - 'row_order': Indices of row ordering
        - 'col_order': Indices of column ordering
        - 'row_linkage': Linkage matrix for rows
        - 'col_linkage': Linkage matrix for columns
    """
    
    # Create shallow copy of data
    data_copy = copy(np.array(data, dtype=float))
    
    # Standardization
    if standardize.lower() == 'row':
        data_copy = (data_copy - data_copy.mean(axis=1, keepdims=True)) / data_copy.std(axis=1, keepdims=True)
    elif standardize.lower() == 'column':
        data_copy = (data_copy - data_copy.mean(axis=0, keepdims=True)) / data_copy.std(axis=0, keepdims=True)
    
    # Handle NaN values
    data_copy = np.nan_to_num(data_copy, nan=0.0)
    
    # Set up linkage function
    if link_fun is None:
        def link_fun(x, **kwargs):
            return sch.linkage(x, link_method, **kwargs)
    
    # Initialize result dictionary
    result = {
        'ordered_data': data_copy.copy(),
        'row_order': np.arange(data_copy.shape[0]),
        'col_order': np.arange(data_copy.shape[1]),
        'row_linkage': None,
        'col_linkage': None
    }
    
    # Cluster rows
    if cluster.lower() in ['row', 'all']:
        row_dist_array = dist_fun(data_copy, metric=row_dist)
        row_linkage = link_fun(row_dist_array, metric=row_dist)
        result['row_linkage'] = row_linkage
        
        # Get dendrogram order using scipy's low-level function
        dendro = sch.dendrogram(row_linkage, no_plot=True, link_color_func=lambda *args: 'k')
        row_order = dendro['leaves']
        result['row_order'] = np.array(row_order)
        
        # Reorder rows using shallow copy
        data_copy = data_copy[row_order, :]
    
    # Cluster columns
    if cluster.lower() in ['col', 'all']:
        # Transpose data for column clustering
        data_t = data_copy.T
        col_dist_array = dist_fun(data_t, metric=col_dist)
        col_linkage = link_fun(col_dist_array, metric=col_dist)
        result['col_linkage'] = col_linkage
        
        # Get dendrogram order
        dendro = sch.dendrogram(col_linkage, no_plot=True, link_color_func=lambda *args: 'k')
        col_order = dendro['leaves']
        result['col_order'] = np.array(col_order)
        
        # Reorder columns
        data_copy = data_copy[:, col_order]
    
    result['ordered_data'] = data_copy
    return result


filepath = "./CIT_BLCA_EXP.csv"
ne = pd.read_csv(filepath,index_col=0)


# TODO Check standardize
dendo = get_ordered_matrix(ne,standardize="none")

biclustered_data = dendo['ordered_data']
samples = ne.columns.values[dendo['col_order']]
genes = ne.index.values[dendo['row_order']]



heatmap=go.Figure(
    layout=dict(
        autosize=True,
        width=None,
        height=None
    ),
    data=go.Heatmap(
    z=biclustered_data.T,
    x=genes,
    y=samples,
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

layout = example_layout(dcc.Graph(
    figure=heatmap,
    style={"flex": "1"}
))
# https://github.com/plotly/plotly.js/blob/4ed586a6402073cc5c50a40cad5f652d7472fcce/src/plots/cartesian/axes.js#L636-L746


def render_layout(hm):
    return dbc.Container(
        fluid=True,
        className="p-0 m-0 h-100",
        children=[
        dbc.Row(
            className="g-0 h-100",  # g-0 removes gutters, h-100 for full height
            children=[
            # Main content area - 75% (width 9) nneds to be on the left
            dbc.Col(
                width=10,
                className="bg-danger d-flex flex-column overflow-hidden ",
                children=[hm]
                ),
            ]
            ),
            # Sidebar area - 25% (width 3)
            dbc.Col(
                width=3,
                className="bg-danger text-white p-3 h-100 overflow-auto",            )
            ]
        )
