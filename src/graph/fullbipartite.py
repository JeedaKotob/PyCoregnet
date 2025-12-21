import dash
from dash import dcc
import random
import plotly.graph_objects as go
import pandas as pd
from components.backend import table
from utils import load_grn_data

def create_network(grn_data):
    edges=[]
    nodes=[]
    bygene=grn_data.get('adjlist').get('bygene')
    bytf=grn_data.get('adjlist').get('bytf')
    tfs = sorted(bytf.keys())

    targets = sorted([g for g in bygene.keys() if g not in tfs])
    for tf, tf_data in bytf.items():
        for tgt in tf_data.get('act', []):
            edges.append({'data': {'id': f"{tf}->{tgt}", 'source': tf, 'target': tgt, 'interaction_type': 'Activation'}})
        for tgt in tf_data.get('rep', []):
            edges.append({'data': {'id': f"{tf}->{tgt}", 'source': tf, 'target': tgt, 'interaction_type': 'Repression'}})

    # TFs left
    for tf in tfs:
        nodes.append({
            'data': {'id': tf, 'type': 'tf'},
            'position': {'x': random.randint(50, 400), 'y': random.randint(50, 2500)}
        })

    # Target genes right
    for tgt in targets:
        nodes.append({
            'data': {'id': tgt, 'type': 'target'},
            'position': {'x': random.randint(1000, 4000), 'y': random.randint(50, 2500)}
        })

    
    
    return {'nodes': nodes, 'edges': edges}

def options(graph_net):
    return [{
        'label': f"{node['data']['id']}   ({node['data']['type']})",
        'value': node['data']['id'],
    } for node in graph_net]        

layout = {'name': 'preset', 'fit': True}

def get_heat_map(genes,filepath):

    ne=pd.read_csv(filepath,index_col=0)
    if isinstance(genes,str):
        genes=[genes]

    selected_df = ne.loc[genes].T
    global_mean=ne.values.mean()
    z_scores=selected_df-global_mean
    zmin = z_scores.min().min()
    zmax = z_scores.max().max()

    n_genes = len(z_scores.columns)
    n_samples = len(z_scores.index)
    
    heatmap_width = min(1000, max(300, 20 * n_genes))
    heatmap_height = min(900, max(300, 20 * n_samples))

    heatmap=go.Figure(data=go.Heatmap(
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
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        xaxis_title="Genes",
        yaxis_title="Samples"
    
    )
    return dcc.Graph(figure=heatmap)



def regulation(selected_nodes,grn_path):
    rows = []
    partner_label = "Partner"
    
    grn_data = load_grn_data(grn_path)
    bygene=grn_data.get('adjlist').get('bygene')
    bytf=grn_data.get('adjlist').get('bytf')
    
    for node in selected_nodes:
        if node in bytf:
            # TF perspective: list its targets
            acts = bytf.get(node, {}).get('act', []) or []
            reps = bytf.get(node, {}).get('rep', []) or []
            partner_label = "Target"
            rows.extend({"Partner": tgt, "Regulation": "Positive", "Source": node} for tgt in acts)
            rows.extend({"Partner": tgt, "Regulation": "Negative", "Source": node} for tgt in reps)
        elif node in bygene:
            # Gene perspective: list its regulators (TFs)
            acts = bygene.get(node, {}).get('act', []) or []
            reps = bygene.get(node, {}).get('rep', []) or []
            partner_label = "TF"
            rows.extend({"Partner": tf, "Regulation": "Positive", "Source": node} for tf in acts)
            rows.extend({"Partner": tf, "Regulation": "Negative", "Source": node} for tf in reps)
        else:
            # Unknown node id — ignore
            pass
        
    return table(
        id="",
        data=rows,
        columns=[
            {"name": "Selected Node", "id": "Source"},
            {"name": "Regulation", "id": "Regulation"},
            {"name": partner_label, "id": "Partner"},
            ]
    )
