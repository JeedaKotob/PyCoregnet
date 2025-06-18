import json
from itertools import combinations
import random

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

def identify_transcription_factors(grn_data):
    tfs=list(grn_data.get('adjlist').get('bytf').keys())
    return tfs

def get_tf_targets(grn_data):
    tf_targets = {}
    bytf = grn_data.get('adjlist', {}).get('bytf', {})

    for tf, targets in bytf.items():
        tf_targets[tf] = set(targets.get('act') + targets.get('rep'))

    return tf_targets

def create_tf_interaction_network(tf_targets, threshold=1):
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
  
    nodes_to_include = tf_nodes_in_graph if edges_data else tfs

    for tf in tfs:
         if tf in nodes_to_include:
            target_count = len(tf_targets[tf])
            nodes_data.append({'data': {'id': tf, 'target_count': target_count, 'type': 'tf'}})

    return {'nodes': nodes_data, 'edges': edges_data}

def create_full_network(grn_data):
    edges=[]
    nodes=[]
    tfs=sorted(tfs)
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


grn= load_grn_data("../data/grn.json")
tfs=identify_transcription_factors(grn)
tf_targets=get_tf_targets(grn)
create_tf_interaction_network(tf_targets)
create_full_network(grn,tfs)
