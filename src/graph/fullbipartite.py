import random

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

def options(graph_net, store):
    selection_mode = store['selection_mode']
    options = [{
        'label': f"{node['data']['id']}   ({node['data']['type']})",
        'value': node['data']['id'],
    } for node in graph_net]
    
    if selection_mode == "tf":
        options =  [node for node in options if "(tf)" in node['label']]
    elif selection_mode == "target":
        options = [node for node in options if "(target)" in node['label']]
        
    return options


layout = {'name': 'preset', 'fit': True}