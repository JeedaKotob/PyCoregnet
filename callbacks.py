from dash import Input, Output, State, html, no_update
from layouts import tab_content, welcome, dashboard_layout, page_shell
from utils import *
def register_callbacks(app):
    
    @app.callback(
        Output('main-content', 'children'),
        Input('url', 'pathname')
    )
    def route(path):
        if path == '/dashboard':
            return page_shell(dashboard_layout(), active_path="/dashboard")
        return page_shell(welcome(), active_path="/")

    @app.callback(
        Output('dashboard-tab-content', 'children'),
        Input('tabs', 'value')
    )
    def switch_tabs(tab_value):
        return tab_content(tab_value)


    '''
    Full Network Graph Reset Button:
    - When reset button is pressed, network graph is formed again,
      and node selections is also reset

    '''
    @app.callback(
        [Output('full-network-graph','elements', allow_duplicate=True),
        Output('full-node-selector','value', allow_duplicate=True)],
        Input('full-reset-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_full_graph_and_dropdown(n_clicks):
        if n_clicks > 0:
            if grn:
                full_net = create_full_network(grn)
                all_elements = full_net['nodes'] + full_net['edges']
                for e in all_elements:
                    e['classes']=''
                return all_elements, None
    
        return no_update, None
    

    '''
    Coreg Graph Reset Button:
    - When reset button is pressed, network graph is formed again,
      and node selection is reset and def threshold is reset too.
    '''
    @app.callback(
        [Output('coreg-network-graph', 'elements', allow_duplicate=True),
        Output('coreg-node-selector', 'value', allow_duplicate=True),
        Output('coreg-threshold-input', 'value', allow_duplicate=True),
        Output('coreg-network-store', 'data', allow_duplicate=True)], 
        Input('coreg-reset-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_coreg_graph_and_dropdown(n_clicks):
        if n_clicks > 0:
            if grn:
                tf_targets = get_tf_targets(grn)
                coreg_net = create_tf_interaction_network(tf_targets,coreg_thresh)  
                all_elements = coreg_net['nodes'] + coreg_net['edges']
                for e in all_elements:
                    e['classes'] = ''
                return all_elements, None, coreg_thresh, all_elements 

        return no_update, None, no_update, no_update
    

    '''
    Target Graph Reset Button:
    - When reset button is pressed, network graph is formed again,
      and node selection is reset and def threshold is reset too.
    '''
    @app.callback(
        [Output('target-network-graph', 'elements', allow_duplicate=True),
        Output('target-node-selector', 'value', allow_duplicate=True),
        Output('target-threshold-input', 'value', allow_duplicate=True),
        Output('target-network-store', 'data', allow_duplicate=True)], 
        Input('target-reset-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_target_graph_and_dropdown(n_clicks):
        if n_clicks > 0:
            if grn:
                target_tfs = get_target_tfs(grn)
                target_net = create_coregulated_network(target_tfs, threshold=target_thresh)  
                all_elements = target_net['nodes'] + target_net['edges']
                for e in all_elements:
                    e['classes'] = ''
                return all_elements, None, target_thresh, all_elements 

        return no_update, None, no_update, no_update


    '''
    Sync Dropdown with Full Graph:
    - When a node is selected by clicking on graph, this ensures that node
    is selected from the dropdown menu
    '''
    @app.callback(
            Output('full-node-selector','value',allow_duplicate=True),
            Input('full-network-graph','tapNodeData'),
            prevent_initial_call=True
    )
    def sync_dropdown_full_graph(tap_node):
        if tap_node:
            return tap_node['id']
        return None
    

    '''
    Sync Dropdown with Coreg Grapg:
    - When a node is selected by clicking on graph, this ensures that node
    is selected from the dropdown menu
    '''
    @app.callback(
            Output('coreg-node-selector','value',allow_duplicate=True),
            Input('coreg-network-graph','tapNodeData'),
            prevent_initial_call=True
    )
    def sync_dropdown_coreg_graph(tap_node):
        if tap_node:
            return tap_node['id']
        return None

    '''
    Sync Dropdown with Target Graph:
    - When a node is selected by clicking on graph, this ensures that node
    is selected from the dropdown menu
    '''
    @app.callback(
            Output('target-node-selector','value',allow_duplicate=True),
            Input('target-network-graph','tapNodeData'),
            prevent_initial_call=True
    )
    def sync_dropdown_target_graph(tap_node):
        if tap_node:
            return tap_node['id']
        return None


    '''
    Update highlight for full network:
    - When a node is selected, that node and its connected nodes/edges are set to highlighted class
    and all other nodes/edges are given faded class (Classes have specific style in stylesheet.py)
    '''
    @app.callback(
        Output('full-network-graph', 'elements',allow_duplicate=True),
        Input('full-node-selector', 'value'),
        State('full-network-store', 'data'),
        prevent_initial_call=True
    )

    def update_full_highlights(selected_node, original_elements):

        if original_elements is None:
            return no_update
        
        if not selected_node:
            return original_elements

        nodes = [e.copy() for e in original_elements if 'source' not in e['data']]
        edges = [e.copy() for e in original_elements if 'source' in e['data']]

        connected_nodes = set()
        for edge in edges:
            src = edge['data']['source']
            tgt = edge['data']['target']
            if selected_node in (src, tgt):
                edge['classes'] = 'highlighted-edge'
                connected_nodes.update([src, tgt])
            else:
                edge['classes'] = 'faded'

        for node in nodes:
            nid = node['data']['id']
            if nid == selected_node:
                node['classes'] = 'highlighted'
            elif nid in connected_nodes:
                node['classes'] = ''
            else:
                node['classes'] = 'faded'

        return nodes + edges
    
    '''
    Update highlight for coreg network:
    - When a node is selected, that node and its connected nodes/edges are set to highlighted class
    and all other nodes/edges are given faded class (Classes have specific style in stylesheet.py)
    '''
    @app.callback(
        Output('coreg-network-graph', 'elements',allow_duplicate=True),
        Input('coreg-node-selector', 'value'),
        State('coreg-network-store', 'data'),
        prevent_initial_call=True
    )

    def update_coreg_highlights(selected_node, original_elements):

        if original_elements is None:
            return no_update
        
        if not selected_node:
            return original_elements

        nodes = [e.copy() for e in original_elements if 'source' not in e['data']]
        edges = [e.copy() for e in original_elements if 'source' in e['data']]

        connected_nodes = set()
        for edge in edges:
            src = edge['data']['source']
            tgt = edge['data']['target']
            if selected_node in (src, tgt):
                edge['classes'] = 'highlighted-edge'
                connected_nodes.update([src, tgt])
            else:
                edge['classes'] = 'faded'

        for node in nodes:
            nid = node['data']['id']
            if nid == selected_node:
                node['classes'] = 'highlighted'
            elif nid in connected_nodes:
                node['classes'] = ''
            else:
                node['classes'] = 'faded'

        return nodes + edges
    
    '''
    Update highlight for target network:
    - When a node is selected, that node and its connected nodes/edges are set to highlighted class
    and all other nodes/edges are given faded class (Classes have specific style in stylesheet.py)
    '''
    @app.callback(
        Output('target-network-graph', 'elements',allow_duplicate=True),
        Input('target-node-selector', 'value'),
        State('target-network-store', 'data'),
        prevent_initial_call=True
    )

    def update_target_highlights(selected_node, original_elements):

        if original_elements is None:
            return no_update
        
        if not selected_node:
            return original_elements

        nodes = [e.copy() for e in original_elements if 'source' not in e['data']]
        edges = [e.copy() for e in original_elements if 'source' in e['data']]

        connected_nodes = set()
        for edge in edges:
            src = edge['data']['source']
            tgt = edge['data']['target']
            if selected_node in (src, tgt):
                edge['classes'] = 'highlighted-edge'
                connected_nodes.update([src, tgt])
            else:
                edge['classes'] = 'faded'

        for node in nodes:
            nid = node['data']['id']
            if nid == selected_node:
                node['classes'] = 'highlighted'
            elif nid in connected_nodes:
                node['classes'] = ''
            else:
                node['classes'] = 'faded'

        return nodes + edges
    

    '''
    Update info panel for full network:
    - When a node is selected, corresponding info is displayed according to selected tab
    '''
    @app.callback(
        Output('full-info-content', 'children', allow_duplicate=True),
        Input('full-node-selector', 'value'),
        Input('full-info-tabs', 'value'),
        prevent_initial_call='initial_duplicate'
    )
    def update_full_info_panel(selected_node, selected_tab):
        if not selected_node:
            if selected_tab == 'expression':
                return html.P("Select a node to view expression.")
            else:
                return html.P("Select a node to view regulation information.")

        if not grn:
            return "Error loading GRN data."

        bytf = grn['adjlist'].get('bytf', {})
        bygene = grn['adjlist'].get('bygene', {})

        if selected_node in bytf:
            node_type = "Transcription Factor"
            acts = bytf[selected_node].get('act', [])
            reps = bytf[selected_node].get('rep', [])
        elif selected_node in bygene:
            node_type = "Target Gene"
            acts = bygene[selected_node].get('act', [])
            reps = bygene[selected_node].get('rep', [])
        else:
            return html.P("Node not found in GRN data.")

    
        if selected_tab == 'expression':
            expression_values = get_expression_data('data/CIT_BLCA_EXP.csv', selected_node)
            expression_text = ', '.join(f"{val:.2f}" for val in expression_values)
            return html.Div([
                html.H4(f"{node_type}: {selected_node}"),
                html.P([html.B("Expression values: "), expression_text])
            ])
        
        else: 
            if node_type == "Transcription Factor":
                return html.Div([
                    html.H4(f"{node_type}: {selected_node}"),
                    html.P([html.B("Activates: "), ', '.join(acts) if acts else "None"]),
                    html.P([html.B("Represses: "), ', '.join(reps) if reps else "None"])
                ])
            else:  
                return html.Div([
                    html.H4(f"{node_type}: {selected_node}"),
                    html.P([html.B("Activated by: "), ', '.join(acts) if acts else "None"]),
                    html.P([html.B("Repressed by: "), ', '.join(reps) if reps else "None"])
                ])

    '''
    Update info panel for coreg network:
    - When a node is selected, corresponding info is displayed according to selected tab
    '''    
    @app.callback(
        Output('coreg-info-content', 'children', allow_duplicate=True),
        Input('coreg-node-selector', 'value'),
        Input('coreg-info-tabs', 'value'),
        State('coreg-threshold-input','value'),
        prevent_initial_call='initial_duplicate'
    )
    def update_coreg_info_panel(selected_node, selected_tab,threshold):
        if not selected_node:
            if selected_tab == 'activity':
                return html.P("Select a TF to view activity level.")
            else:
                return html.P("Select a node to view regulation information.")

        else:
            if not grn:
                return "Error loading GRN data."
            tf_targets = get_tf_targets(grn)
            coreg_net=create_tf_interaction_network(tf_targets)
            edges=coreg_net['edges']
            tf=selected_node
            target_count=len(tf_targets[tf])
            coregs=[]
            for edge in edges:
                if edge['data']['shared_count']>=threshold:
                    source=edge['data']['source']
                    target=edge['data']['target']
                    if tf == source or tf==target:
                        coregs.append(edge['data'])
            coregs = sorted(coregs, key=lambda x: x['shared_count'], reverse=True)
            coregs_output = []
            for co in coregs:
                coreg = co['target'] if tf == co['source'] else co['source']
                coregs_output.append(html.P(f"{coreg} - {co['shared_count']} shared targets"))

            if selected_tab == 'activity':
                return html.Div([
                    html.H4(f"{"Transcription Factor"}: {selected_node}"),
                    html.P("Nothin here yet")
                ])
            else:
                return html.Div([
                    html.H4(f"Transcription Factor: {selected_node}"),
                    html.P([html.B(f"{tf}'s target count: {target_count}")]),
                    html.P([html.B(f"{tf}'s coregulators - shared targets count:")]),
                    *coregs_output  
                ])
           
    '''
    Update info panel for target network:
    - When a node is selected, corresponding info is displayed according to selected tab
    '''  
    @app.callback(
        Output('target-info-content', 'children', allow_duplicate=True),
        Input('target-node-selector', 'value'),
        Input('target-info-tabs', 'value'),
        State('target-threshold-input','value'),
        prevent_initial_call='initial_duplicate'
    )
    def update_target_info_panel(selected_node, selected_tab,threshold):
        if not selected_node:
            if selected_tab == 'grn':
                return html.P("Select a node to view its grn.")
            else:
                return html.P("Select a node to view regulation information.")

        if not grn:
            return "Error loading GRN data."

        target_tfs=get_target_tfs(grn)
        target_net=create_coregulated_network(target_tfs)
        edges=target_net['edges']
        tgt=selected_node
        coreg_count=len(target_tfs[tgt])
        coregulated=[]
        for edge in edges:
            if edge['data']['shared_count']>=threshold: 
                source=edge['data']['source']
                target=edge['data']['target']
                if tgt == source or tgt==target:
                    coregulated.append(edge['data'])
        coregulated = sorted(coregulated, key=lambda x:x['shared_count'],reverse=True)
        coregulated_output=[]
        for co in coregulated:
            cotgt=co['target'] if tgt == co['source'] else co['source']
            coregulated_output.append(html.P(f"{cotgt} - {co['shared_count']} shared transcription factors"))
    
        
        if selected_tab =='grn':
            return html.Div([
                    html.H4(f"{"Target Gene"}: {selected_node}"),
                    html.P("Nothin here yet")
                ])
        else:
            return html.Div([
                    html.H4(f"Transcription Factor: {selected_node}"),
                    html.P(f"{tgt}'s target count: {coreg_count}"),
                    html.P(f"{tgt}'s target - shared transcription factor count:"),
                    *coregulated_output 
                ])

    
    '''
    Update Coreg Graph:
    - After Threshold input, 'update button' should be pressed, this will update graph to only show nodes/edges
    with the newly defined threshold input. This also takes regard of the selected node, if node doesnt account
    for threshold, selection will be cleared
    '''  
    @app.callback(
        [Output('coreg-network-graph', 'elements', allow_duplicate=True),
        Output('coreg-network-store', 'data', allow_duplicate=True),
        Output('coreg-node-selector','value',allow_duplicate=True)],
        Input('coreg-update-button', 'n_clicks'),
        State('coreg-node-selector','value'),
        State('coreg-threshold-input', 'value'),
        prevent_initial_call=True
    )
    def update_coreg_graph(n_clicks, selected_node, threshold):
        if n_clicks > 0:
            if grn:
                tf_targets = get_tf_targets(grn)
                coreg_net = create_tf_interaction_network(tf_targets, threshold)
                all_elements = coreg_net['nodes'] + coreg_net['edges']
                for e in all_elements:
                    e['classes'] = ''
                # if selected_node in tf_targets and len(tf_targets[selected_node]) < threshold:
                #     selected_node = ''
                connected=any(
                    (edge['data']['source']== selected_node or edge['data']['target']==selected_node)
                    for edge in coreg_net['edges']
                )
                if not connected:
                    selected_node=''
                return all_elements, all_elements, selected_node  
        return no_update, no_update, no_update


    '''
    Update Target Graph:
    - After Threshold input, 'update button' should be pressed, this will update graph to only show nodes/edges
    with the newly defined threshold input. This also takes regard of the selected node, if node doesnt account
    for threshold, selection will be cleared.
    '''  
    @app.callback(
        [Output('target-network-graph', 'elements', allow_duplicate=True),
        Output('target-network-store', 'data', allow_duplicate=True),
        Output('target-node-selector','value',allow_duplicate=True)],
        Input('target-update-button', 'n_clicks'),
        State('target-node-selector','value'),
        State('target-threshold-input', 'value'),
        prevent_initial_call=True
    )
    def update_target_graph(n_clicks, selected_node, threshold):
        if n_clicks > 0:
            if grn:
                target_tfs = get_target_tfs(grn)
                target_net = create_tf_interaction_network(target_tfs, threshold)
                all_elements = target_net['nodes'] + target_net['edges']
                for e in all_elements:
                    e['classes'] = ''
                # if selected_node in target_tfs and len(target_tfs[selected_node]) < threshold:
                #     selected_node = ''
                connected=any(
                    (edge['data']['source']== selected_node or edge['data']['target']==selected_node)
                    for edge in target_net['edges']
                )
                if not connected:
                    selected_node=''
                return all_elements, all_elements, selected_node  
        return no_update, no_update, no_update
