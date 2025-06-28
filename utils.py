import json
from itertools import combinations
import random
import pandas as pd

# --- KInd of our backend codes here ---

def load_grn_data(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file '{filepath}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'.")
        return None

def get_tf_targets(grn_data):
    tf_targets = {}
    bytf = grn_data.get('adjlist', {}).get('bytf', {})

    for tf, targets in bytf.items():
        tf_targets[tf] = set(targets.get('act') + targets.get('rep'))

    return tf_targets

def create_tf_interaction_network(tf_targets, threshold=5):
    tfs = list(tf_targets.keys())
    nodes_data = []
    edges_data = []
    edge_ids = set()

    tf_nodes_in_graph = set()
   
    for tf1, tf2 in combinations(tfs, 2):
        targets1 = tf_targets.get(tf1)
        targets2 = tf_targets.get(tf2)
        shared_targets = targets1.intersection(targets2)
        shared_count = len(shared_targets)

        if shared_count >= threshold:
            edge_id = tuple(sorted((tf1, tf2)))
            if edge_id not in edge_ids:
                edges_data.append({
                    'data': {
                        'id': f"{tf1}-{tf2}_shared", 
                        'source': tf1,
                        'target': tf2,
                        'shared_count': shared_count,
                        'shared_targets': list(shared_targets)
                    }
                })
                edge_ids.add(edge_id)
                tf_nodes_in_graph.add(tf1)
                tf_nodes_in_graph.add(tf2)

    # Add nodes that are part of the graph OR all TFs if graph is empty
  
    nodes_to_include = tf_nodes_in_graph if edges_data else None

    if edges_data: 
        for tf in tfs:
            if tf in nodes_to_include:
                target_count = len(tf_targets[tf])
                nodes_data.append({'data': {'id': tf, 'target_count': target_count, 'type': 'tf'}})

    return {'nodes': nodes_data, 'edges': edges_data}

def create_full_network(grn_data):
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

def get_target_tfs(grn_data):
    target_tfs={}
    bygene = grn_data.get('adjlist').get('bygene')

    for target, tfs in bygene.items():
        target_tfs[target] = set(tfs.get('act')+ tfs.get('rep'))

    return target_tfs

def create_coregulated_network(target_tfs,threshold=10):
    # targets=grn_data.get('adjlist').get('bygene').keys()
    targets=list(target_tfs.keys())
    nodes_data=[]
    edges_data=[]
    edge_ids=set()

    target_nodes_in_graph=set()

    for tgt1,tgt2 in combinations(targets,2):
        tfs1= target_tfs.get(tgt1)
        tfs2= target_tfs.get(tgt2)
        shared_tfs=tfs1.intersection(tfs2)
        shared_count = len(shared_tfs)

        if shared_count >= threshold:
            edge_id = tuple(sorted((tgt1,tgt2))) ###CHECKKK ()()
            if edge_id not in edge_ids:
                edges_data.append({
                    'data':{
                        'id':f"{tgt1}-{tgt2}_shared",
                        'source': tgt1,
                        'target': tgt2,
                        'shared_count':shared_count,
                        'shared_tfs':list(shared_tfs)
                    }
                })
                edge_ids.add(edge_id)
                target_nodes_in_graph.add(tgt1)
                target_nodes_in_graph.add(tgt2)

    nodes_to_include=target_nodes_in_graph if edges_data else targets

    for target in targets:
        if target in nodes_to_include:
            tf_count=len(target_tfs[target])
            if tf_count>=threshold:
                nodes_data.append({'data':{'id':target,'tf_count':tf_count,'type':'tf'}})

    return {'nodes':nodes_data,'edges':edges_data}

def get_expression_data(filepath,gene):
    ne=pd.read_csv(filepath, index_col=0)
    gene_exp=ne.loc[gene].to_list()
    return gene_exp


grn = load_grn_data("data/grn.json")
target_thresh=10 # used for reset target (coregulated) graph
coreg_thresh=5 # used for reset coreg graph
target_tfs = get_target_tfs(grn)
tf_targets=get_tf_targets(grn)
