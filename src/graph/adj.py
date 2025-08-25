from itertools import combinations

def get_entity_partners(grn_data : dict, key:str):
    entity_partners = {}
    adjlist = grn_data.get('adjlist', {})
    entity_dict = adjlist.get(key, {})

    for entity, partner_info in entity_dict.items():
        partners = set(partner_info.get('act', []) + partner_info.get('rep', []))
        entity_partners[entity] = partners

    return entity_partners


def default_threshold(connections : dict, threshold : float):
    max_targets = max((len(targets) for targets in connections.values()), default=1)
    coreg_threshold = int(threshold * max_targets)
    return coreg_threshold


def create_network(entity_to_partners, threshold=None):
    entities = list(entity_to_partners.keys())
    nodes_data = []
    edges_data = []
    edge_ids = set()

    # if threshold is None:
    #     max_partners = max((len(partners) for partners in entity_to_partners.values()), default=1)
    #     threshold = 0.50 * max_partners

    entities_in_graph = set()

    for entity1, entity2 in combinations(entities, 2):
        partners1 = entity_to_partners.get(entity1, set())
        partners2 = entity_to_partners.get(entity2, set())
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

    nodes_to_include = entities_in_graph if edges_data else entities

    for entity in nodes_to_include:
        partner_count = len(entity_to_partners.get(entity, []))
        nodes_data.append({
            'data': {
                'id': entity,
                'partner_count': partner_count,
                'type': 'entity'
            }
        })

    return {'nodes': nodes_data, 'edges': edges_data}

def options(entity_to_partners):
    return [{'label': n['data']['id'], 'value': n['data']['id']} for n in entity_to_partners]