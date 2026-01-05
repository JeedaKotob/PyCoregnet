from typing import Literal
from itertools import combinations
from components.backend import table
import dash_ag_grid as dag
import dash
from dash import html
import numpy as np


def get_genes(grn_data : dict, role: str = Literal['bygene','bytf'],):
    genes = {}
    adjlist = grn_data.get('adjlist', {})
    entity_dict = adjlist.get(role, {})

    for entity, partner_info in entity_dict.items():
        partners = set(partner_info.get('act', []) + partner_info.get('rep', []))
        genes[entity] = partners

    return genes


def default_threshold(genes : dict, threshold_ratio : float = None):
    max_targets = max((len(targets) for targets in genes.values()), default=1)
    threshold = int(threshold_ratio * max_targets)
    return threshold


def create_network(genes : dict, threshold : float = None):
    entities = list(genes.keys())
    nodes_data = []
    edges_data = []
    edge_ids = set()

    entities_in_graph = set()

    for entity1, entity2 in combinations(entities, 2):
        partners1 = genes.get(entity1, set())
        partners2 = genes.get(entity2, set())
        shared_partners = partners1.intersection(partners2)
        shared_count = len(shared_partners)

        if shared_count >= threshold:

            edge_id = tuple(sorted((entity1, entity2)))
            if edge_id not in edge_ids:
                edges_data.append({
                    'data': {
                        'id': f"{entity1}-{entity2}_shared",
                        'source': entity1,
                        'target': entity2,
                        'shared_count': shared_count,
                        'shared_partners': list(shared_partners)
                    }
                })
                edge_ids.add(edge_id)
                entities_in_graph.update([entity1, entity2])

    nodes_to_include = entities

    for entity in nodes_to_include:
        partner_count = len(genes.get(entity, []))
        nodes_data.append({
            'data': {
                'id': entity,
                'partner_count': partner_count,
                'type': 'entity'
            }
        })

    return {'nodes': nodes_data, 'edges': edges_data}

def options(genes):
    return [{'label': n['data']['id'], 'value': n['data']['id']} for n in genes]


def by_update_info_panel(connections, selected_nodes, edges, threshold, columns):

    data = []
    partners = []
    for by in selected_nodes:

        target_count = len(connections[by])
        results = []
        for edge in edges:
            if edge['data']['shared_count'] >= threshold:
                src = edge['data']['source']
                tgt = edge['data']['target']
                if by == src or by == tgt:
                    results.append(edge['data'])
        results = sorted(results, key=lambda x: x['shared_count'], reverse=True)
        
        for i, co in enumerate(results):
            coreg = co['target'] if by == co['source'] else co['source']
            partners.append(coreg)
            row = {"column1" : f"{by} ({(target_count)})", "column2" : coreg, "column3" : co['shared_count']}
    
            if i == 0:
                row['rowSpan'] = len(results)
            else:
                row['rowSpan'] = 1
            data.append(row)
            
    unique, counts = np.unique(partners, return_counts=True)
    common_partners = list(set(unique[counts > 1].tolist()))

    for row in data:
        if row['column2'] in common_partners:
            row['is_common'] = True
            row['partner_tooltip'] = 'Shared'
        else:
            row['is_common'] = False
            row['partner_tooltip'] = None

    

    columnDefs = [
        {
            'field': 'column1',
            **columns['column1'],
            'rowSpan': {'function': 'params.data.rowSpan'},
            'cellStyle': {'backgroundColor': 'white', 'display': 'flex', 'alignItems': 'center', 'border': '1px solid #ddd'}
        },
        {
            'field': 'column2',
            **columns['column2'],
            'tooltipField': 'partner_tooltip',
            'cellStyle': {
                'styleConditions': [
                    {'condition': 'params.data.is_common', 'style': {'backgroundColor': '#add8e6', 'textAlign': 'left'}}
                ],
                'defaultStyle': {'textAlign': 'left'}
            }
        },
        {'field': 'column3',**columns['column3'], 'cellStyle': {'textAlign': 'right'}, 'width': 80, 'maxWidth': 80, 'suppressSizeToFit': True},
    ]
    
    # return 
    return dag.AgGrid(
        id='',
        columnDefs=columnDefs,
        rowData=data,
        columnSize='responsiveSizeToFit',
        dashGridOptions = {'suppressRowTransform': True, 'tooltipShowDelay': 0}
    )

    

