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

    @app.callback(
        [Output('full-network-graph','elements', allow_duplicate=True),
        Output('full-node-selector','value', allow_duplicate=True)],
        Input('full-reset-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_full_graph_and_dropdown(n_clicks):
        if n_clicks > 0:
            grn = load_grn_data("data/grn.json")
            if grn:
                full_net = create_full_network(grn)
                all_elements = full_net['nodes'] + full_net['edges']
                for e in all_elements:
                    e['classes']=''
                return all_elements, None
    
        return no_update, None
    
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
            grn = load_grn_data("data/grn.json")
            if grn:
                tf_targets = get_tf_targets(grn)
                coreg_net = create_tf_interaction_network(tf_targets, threshold=5)  
                all_elements = coreg_net['nodes'] + coreg_net['edges']
                for e in all_elements:
                    e['classes'] = ''
                return all_elements, None, 5, all_elements 

        return no_update, None, no_update, no_update

    
    @app.callback(
            Output('full-node-selector','value',allow_duplicate=True),
            Input('full-network-graph','tapNodeData'),
            prevent_initial_call=True
    )
    def sync_dropdown_full_graph(tap_node):
        if tap_node:
            return tap_node['id']
        return None
    
    @app.callback(
            Output('coreg-node-selector','value',allow_duplicate=True),
            Input('coreg-network-graph','tapNodeData'),
            prevent_initial_call=True
    )
    def sync_dropdown_coreg_graph(tap_node):
        if tap_node:
            return tap_node['id']
        return None
    
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


        grn = load_grn_data("data/grn.json")
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
            
    @app.callback(
        Output('coreg-info-content', 'children', allow_duplicate=True),
        Input('coreg-node-selector', 'value'),
        Input('coreg-info-tabs', 'value'),
        prevent_initial_call='initial_duplicate'
    )
    def update_coreg_info_panel(selected_node, selected_tab):
        if not selected_node:
            if selected_tab == 'expression':
                return html.P("Select a node to view expression.")
            else:
                return html.P("Select a node to view regulation information.")

        grn = load_grn_data("data/grn.json")
        if not grn:
            return "Error loading GRN data."

        bytf = grn['adjlist'].get('bytf', {})

        if selected_node in bytf:
            node_type = "Transcription Factor"
            acts = bytf[selected_node].get('act', [])
            reps = bytf[selected_node].get('rep', [])
       
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
          return html.Div([
            html.H4(f"{node_type}: {selected_node}"),
            html.P([html.B("Target Count: "), str(len(acts) + len(reps))]),
            html.P([html.B("Activates: "), ', '.join(acts) if acts else "None"]),
            html.P([html.B("Represses: "), ', '.join(reps) if reps else "None"])
        ])
           
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
            grn = load_grn_data("data/grn.json")
            if grn:
                tf_targets = get_tf_targets(grn)
                coreg_net = create_tf_interaction_network(tf_targets, threshold or 1)
                all_elements = coreg_net['nodes'] + coreg_net['edges']
                for e in all_elements:
                    e['classes'] = ''
                if selected_node in tf_targets and len(tf_targets[selected_node]) < threshold:
                    selected_node = ''
                return all_elements, all_elements, selected_node  
        return no_update, no_update, no_update

