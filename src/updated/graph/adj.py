from typing import Literal
from itertools import combinations
from components.backend import table


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



    

