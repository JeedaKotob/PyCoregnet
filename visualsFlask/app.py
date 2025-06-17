import json
from flask import Flask, render_template, request, jsonify
from itertools import combinations
import random
import os

app = Flask(__name__)

# --- Data Loading and Processing ---

def load_grn_data(filepath):
    """Loads the Gene Regulatory Network data from a JSON file."""
    # filepath=os.environ["GRN_PATH"]
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file '{filepath}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'.")
        return None

def identify_transcription_factors(grn):
    """Identifies TFs. Assumes source of interaction is TF."""
    tfs=list(grn.get('adjlist',{}).get('bytf',{}).keys())
    return tfs


def get_tf_targets(grn_data, tfs):
    """Creates a dictionary mapping each TF to a set of its target genes.""" 
    tf_targets = {}
    bytf = grn_data.get('adjlist', {}).get('bytf', {})

    for tf, tf_data in bytf.items():
        tf_targets[tf] = set(tf_data.get('act', []) + tf_data.get('rep', []))

    return tf_targets

def create_tf_interaction_network(tf_targets, threshold=1):
    """Generates nodes and edges for the TF co-regulation graph."""
    tfs = list(tf_targets.keys())
    nodes_data = []
    edges_data = []
    edge_ids = set()

    tf_nodes_in_graph = set() # Track TFs actually included

    # Create edges first based on threshold
    for tf1, tf2 in combinations(tfs, 2):
        targets1 = tf_targets.get(tf1, set())
        targets2 = tf_targets.get(tf2, set())
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
         # Include node if it's connected OR if there are no connections at all
         if tf in nodes_to_include:
            target_count = len(tf_targets[tf])
            nodes_data.append({'data': {'id': tf, 'target_count': target_count, 'type': 'tf'}}) # Add type info

    return {'nodes': nodes_data, 'edges': edges_data}

# --- Flask Routes ---

@app.route('/')
def index():
    """Serves the main HTML page with tabs."""
    
    grn_data = load_grn_data("../data/grn.json") 
    if grn_data is None:
        return jsonify({"error": "Failed to load GRN data."}), 500

    tfs = identify_transcription_factors(grn_data)

    if not tfs:
        return jsonify({'nodes': [], 'edges': []})

    tf_targets = get_tf_targets(grn_data, tfs)
    thr = int((max([len(tf_targets[t]) for t in list(tf_targets.keys())]) * 0.01))

    return render_template('index.html', thresh=thr)

@app.route('/api/tf_network')
def get_tf_network_data():
    """API endpoint for the TF co-regulation network."""

    grn_data = load_grn_data("../data/grn.json") 
    if grn_data is None:
        return jsonify({"error": "Failed to load GRN data."}), 500

    tfs = identify_transcription_factors(grn_data)

    if not tfs:
        return jsonify({'nodes': [], 'edges': []})

    tf_targets = get_tf_targets(grn_data, tfs)

    try:
        threshold = int(request.args.get('threshold', 1))
        if threshold < 0:
            threshold = 0
    except ValueError:
        return jsonify({"error": "Invalid threshold value."}), 400
    
    network_elements = create_tf_interaction_network(tf_targets, threshold)

    return jsonify(network_elements)  


@app.route('/api/full_network')
def get_full_network_data():
    grn_data = load_grn_data("../data/grn.json")
    if grn_data is None:
        return jsonify({"error": "Failed to load GRN data."}), 500

    adjlist = grn_data.get('adjlist', {})
    bytf = adjlist.get('bytf', {})
    bygene = adjlist.get('bygene', {})

    edges = []
    nodes = []

    tfs = sorted(bytf.keys())
    targets = sorted([g for g in bygene.keys() if g not in bytf.keys()])

    for tf, tf_data in bytf.items():
        for tgt in tf_data.get('act', []):
            edges.append({'data': {'id': f"{tf}->{tgt}", 'source': tf, 'target': tgt, 'interaction_type': 'Activation'}})
        for tgt in tf_data.get('rep', []):
            edges.append({'data': {'id': f"{tf}->{tgt}", 'source': tf, 'target': tgt, 'interaction_type': 'Repression'}})

    # TFs lect
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

    return jsonify({'nodes': nodes, 'edges': edges})


if __name__ == '__main__':
    app.run(debug=True)