
from typing import Literal
import dash
from dash import (
    html, Input, Output, State, callback, dcc, 
    no_update, callback_context, ctx, MATCH, ALL, Patch, get_app
)
import dash_bootstrap_components as dbc
from layout import CytoGraph, UIControls
# NOTE NEEDS TO BE REPLACED
import utils

def get_first(val):
    if isinstance(val, list) and val:
        assert len(val) == 1
        return val[0]
    return val


app = get_app()

# All UI Input goes to the store
@app.callback(
    [
        Output({"type": "store", "uid": MATCH}, "data"),
        Output({"type": "options_dropdown", "uid": MATCH}, "value"),
    ],
    
    [
        Input({"type": "network-graph", "uid": MATCH}, "tapNodeData"),
        Input({"type": "options_dropdown", "uid": MATCH}, "value"),
        Input({"type": "selection_mode", "uid": ALL}, "value"),
        Input({"type": "filter_mode", "uid": ALL}, "value"),
        Input({"type": "backtracking_mode", "uid": ALL}, "value"),
        Input({"type": "threshold_input_btn", "uid": ALL}, "n_clicks"),
    ],
    State({"type": "threshold_input", "uid": ALL}, "value"),
    State({"type": "store", "uid": MATCH}, "data"),
    prevent_initial_call=True,
)
def sync(
    tapNodeData, dropdown_value, selection_mode, filter_mode, backtracking_mode, threshold_btn, threshold_value, store
):
    trigger = ctx.triggered_id

    assert isinstance(store, dict) # Catch problems from ALL pattern-matched inputs

    # Helper to get first value from ALL pattern-matched inputs
    def get_first(val):
        if isinstance(val, list) and val:
            assert len(val) == 1
            return val[0]
        return val

    # Update store based on which control triggered the app.callback
    if trigger:
        t_type = trigger.get('type') if isinstance(trigger, dict) else trigger

        if t_type == "selection_mode":
            val = get_first(selection_mode)
            if val:
                store['selection_mode'] = val

        elif t_type == "filter_mode":
            val = get_first(filter_mode)
            if val:
                store['filter_mode'] = val

        elif t_type == "backtracking_mode":
            val = get_first(backtracking_mode)
            if val:
                store['backtracking_mode'] = val

        elif t_type == "threshold_input_btn":
            val = get_first(threshold_value)
            if val is not None:
                store['threshold'] = val
        elif t_type == "network-graph" and tapNodeData:
            sel_mode = store.get('selection_mode', 'single')
            
            if sel_mode=="off":
                return no_update,no_update
            
            node_id = tapNodeData.get('id')
            node_type = tapNodeData.get('type')
            if not node_id:
                return store, no_update
            
            # Check if node matches the current filter mode
            filt_mode = store.get('filter_mode')
            if node_type is not None:
                if filt_mode == 'target' and node_type != 'target':
                    return store, no_update
                elif filt_mode == 'tf' and node_type != 'tf':
                    return store, no_update
            # 'both' allows all node types, and None type passes through
            
            if sel_mode == 'single':
                store["selected"] = [node_id]
                return store, node_id
            elif sel_mode == 'multiple':
                
                selected = store.get("selected", [])
                if isinstance(selected,str):
                    selected = [selected]                
                temp = set(selected)
                temp.add(node_id)
                store["selected"] = list(temp)
                return store, store["selected"]

    
        elif t_type == "options_dropdown":
            val = dropdown_value
            sel_mode = store.get('selection_mode', 'single')
            if not val:
                store['selected'] = []
                return store, no_update
            if sel_mode == 'single':
                store["selected"] = [val]
                return store, no_update
            elif sel_mode == 'multiple':
                                
                temp = set(store.get('selected', []))
                # val could be a list or a single value
                if isinstance(val, list):
                    temp.update(val)
                    # If user deselected, keep only current dropdown values
                    if len(temp) > len(val):
                        temp = set(val)
                    store['selected'] = list(temp)
                    return store, no_update
                else:
                    temp.add(val)
                    store['selected'] = list(temp)
                    return store, no_update

    return store, no_update 



@app.callback(
    [
        Output({"type": "options_dropdown", "uid": MATCH},"multi"),
        Output({"type": "options_dropdown", "uid": MATCH}, 'disabled'),
    ],
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "options_dropdown", "uid": MATCH}, "multi"),
    State({"type": "options_dropdown", "uid": MATCH}, "disabled"),
    prevent_initial_call=True,
)
def dropdown_selection_mode(store, multi, disabled):
    selection_mode = store.get('selection_mode')
    
    if selection_mode == "single":
        if multi is False and disabled is False:
            return no_update, no_update
        return False, False
    
    elif selection_mode == "multiple":
        if multi is True and disabled is False:
            return no_update, no_update
        return True, False
    
    elif selection_mode == "off":
        if disabled is True:
            return no_update, no_update
        return no_update, True
    
    return no_update, no_update
    
            
@app.callback(
    Output({"type": "network-graph", "uid": MATCH}, "elements"),
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "network-graph", "uid": MATCH}, "elements"),
    prevent_initial_call=True
)
def highlightor(store, elements):
    
    selected_val = store['selected']
    if isinstance(selected_val, str):
        selected = {selected_val}
    else:
        selected = set(selected_val) if selected_val else set()

    if not selected:
        patch = Patch()
        for i in range(len(elements)):
            patch[i] = elements[i].copy()
            patch[i]['classes'] = ''
        return patch
        
    connected_nodes = set()
    patch = Patch()
    
    # First pass: identify connected nodes
    for i, e in enumerate(elements):
        if 'source' in e['data']:
            src = e['data']['source']
            tgt = e['data']['target']        
            if selected & {src, tgt}:
                connected_nodes.update([src, tgt])
    
    # Second pass: apply classes using patch
    for i, e in enumerate(elements):
        elem_copy = e.copy()
        
        if 'source' in e['data']:  # Edge
            src = e['data']['source']
            tgt = e['data']['target']        
            if selected & {src, tgt}:
                elem_copy['classes'] = "highlighted-edge"
            else:
                elem_copy['classes'] = "faded"
        else:  # Node
            nid = e['data']['id']
            if nid in selected:
                elem_copy['classes'] = 'highlighted'
            elif nid in connected_nodes:
                elem_copy['classes'] = ''
            else:
                elem_copy['classes'] = 'faded'
        
        patch[i] = elem_copy
    
    return patch



@app.callback(
    Output({"type": "options_dropdown", "uid": MATCH}, "options"),
    Input({"type": "network-graph", "uid": MATCH}, "elements"),
    Input({"type": "filter_mode", "uid": ALL}, "value"),
    State({"type": "options_dropdown", "uid": MATCH}, "options"),
)
def create_dropdown_options(elements, filter_mode, current_options):
        
    # Extract filter_mode from ALL pattern-matched list
    if isinstance(filter_mode, list) and filter_mode:
        filter_mode = filter_mode[0]
    
    # Get nodes using GENERATOR better for memory 
    nodes = (ele['data'] for ele in elements if 'source' not in ele['data'])
    
    # Get the first node to check data type
    first_node = next(nodes, None)
    
    # Handle empty nodes case
    if first_node is None:
        return []
    
    # Is a bool True if full graph
    byreg = first_node.get('type') in ['tf', 'target']
    
    options = []
    
    # Add the first node since we consumed it using next()
    label = first_node.get('label', first_node.get('id'))
    if byreg:
        if first_node['type']==filter_mode or filter_mode =="both":
            label = f"{label} ({first_node['type']})"
            options.append({'label': label, 'value': first_node['id']})
    else:
        options.append({'label': label, 'value': first_node['id']})
        

    # Process the REST of the nodes
    for node in nodes:
        label = node.get('label', node.get('id'))
    
        if byreg:
            if node['type']==filter_mode or filter_mode =="both":
                label = f"{label} ({node['type']})"        
                options.append({
                    'label': label, 
                    'value': node['id']
                })
        else:
            options.append({
                'label': label, 
                'value': node['id']
            })
            
        
    options = sorted(options, key=lambda x: x['label'])
    
    return options


@app.callback(
    Output({"type": "threshold_input", "uid": ALL}, "value"),
    Input({"type": "main-content", "uid": ALL}, "children"),
    State({"type": "store", "uid": ALL}, "data"),
)
def update_thresh(children,store):
    store = get_first(store)
    threshold = store.get("threshold",[])
    if threshold:
        return [threshold]
    else:
        return [no_update]


@app.callback(
    Output({"type": "network-graph", "uid": MATCH}, "elements",allow_duplicate=True),
    Input({"type": "threshold_input_btn", "uid": ALL}, "n_clicks"),
    State({"type": "threshold_input", "uid": ALL}, "value"),
    State({"type": "store", "uid": ALL}, "data"),
    prevent_initial_call=True    
)
def update_graph_thresh(n_clicks,value,store):
    value = get_first(value)
    store = get_first(store)

    from graph import adj
    
    data = adj.create_network(
        adj.get_genes(data.grn,store['preprocess_role']),
        value
    )
    
    
    return data['nodes'] + data['edges']

    
    
@app.callback(
    [
    Output({"type": "total_nodes", "uid": MATCH}, "children"),
    Output({"type": "total_edges", "uid": MATCH}, "children"),
    Output({"type": "selected_nodes", "uid": MATCH}, "children"),
    Output({"type": "selected_edges", "uid": MATCH}, "children"),
    ],
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "network-graph", "uid": MATCH}, "elements"),
)
def update_network_stats(store,elements):
    selected = store['selected']
    metadata = store['metadata']
    t=0
    tf = 0
    
    for e in elements:
        data = e['data']
        source = data.get("source",None)
        if not source:
            pass
        target = data.get("target",None)
        if source in selected:
            t=t+1
        elif target in selected:
            tf=tf+1
            
    total = t+tf        
        
    
    return metadata['total_nodes'],metadata['total_edges'],len(selected),total

    

@app.callback(
    Output({"type": "inspector_tabs_content", "uid": MATCH}, "children"),
    Input({"type": "inspector_tabs", "uid": MATCH}, "active_tab"),
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "network-graph", "uid": MATCH}, "elements"),
    prevent_initial_call=True
)
def update_inspector_tabs(active_tab, store,___):
    """Update inspector tabs based on active tab and store data"""

    if not active_tab:
        return no_update
    
    selected = store.get("selected",None)
    
    if not selected:
        return html.Div(
            "Please select a node",
            className="d-flex align-items-center justify-content-center h-100"
        )

    
    if active_tab == "table":
        from graph.fullbipartite import regulation
        return regulation(selected,"./grn.json")
    elif active_tab == "heatmap":
        from graph.fullbipartite import get_heat_map
        return get_heat_map(selected,"./CIT_BLCA_EXP.csv")
    elif active_tab == "adj_table":
        from dash import get_app
        app = get_app()
        cache = app.server.config["SERVER_CACHE"]
        pre_data = cache.get(store['uid'])
        
        if not pre_data:
            raise NameError("Getting cache has failed")
        
        edges = [e.copy() for e in ___ if 'source' in e['data']]
        columns=[
            {"name": "TF", "id": "Node"},
            {"name": "CO", "id": "shared"},
            {"name": "STC", "id": "count"},
        ]

        from graph.adj import by_update_info_panel
        
        # NOTE FULL CONNECTIONS OR CURRENT ?
        return by_update_info_panel(pre_data,selected,edges,store['threshold'],columns)
    



    return no_update
    
    


