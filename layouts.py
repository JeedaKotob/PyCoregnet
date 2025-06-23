from dash import html, dcc
import dash_cytoscape as cyto
from utils import load_grn_data, create_full_network, identify_transcription_factors,get_tf_targets,create_tf_interaction_network
from stylesheet import full_network_stylesheet, coreg_network_stylesheet

cyto.load_extra_layouts() 

def navbar(active_path=""):
    return html.Nav(className="navbar", children=[
        html.Div("PyCoregnet", className="nav-logo"),
        html.Div(className="nav-links", children=[
            dcc.Link("Home", href="/", className=f"nav-item {'nav-active' if active_path == '/' else ''}"),
            dcc.Link("Dashboard", href="/dashboard", className=f"nav-item {'nav-active' if active_path == '/dashboard' else ''}")
        ])
    ])

def page_shell(content, active_path=""):
    return html.Div([
        navbar(active_path),
        html.Div(content)
    ])

def welcome():
    return html.Div(className='welcome-container', children=[
        html.H1("PyCoregnet"),
        html.P("...")
    ])

def dashboard_layout():
    return html.Div(id='dashboard-tab-wrapper', className='tab-container', children=[
        dcc.Tabs(id='tabs', value='full', className='dash-tabs', children=[
            dcc.Tab(label='Full Network', value='full', className='dash-tab', selected_className='dash-tab--selected'),
            dcc.Tab(label='Coregulators', value='coregs', className='dash-tab', selected_className='dash-tab--selected'),
            dcc.Tab(label='Coregulated', value='targets', className='dash-tab', selected_className='dash-tab--selected'),
            dcc.Tab(label='Patients', value='samples', className='dash-tab', selected_className='dash-tab--selected'),
        ]),
        html.Div(id='dashboard-tab-content', className='tab-content')
    ])

def tab_content(tab_name):
    if tab_name == 'full':
        grn=load_grn_data("data/grn.json")
        if grn:
            full_net=create_full_network(grn)
            all_elements = full_net['nodes'] + full_net['edges']
            return html.Div([
                html.H3("Full Bipartite Network"),
                dcc.Store(id='full-network-store',data=all_elements),
                html.Div(className="full-network-layout", children=[

                    html.Div(className="cyto-graph-wrapper", children=[
                        cyto.Cytoscape(
                            id='full-network-graph',
                            layout={'name': 'preset', 'fit': True, 'padding': 5},
                            style={'width': '100%', 'height': '800px'},
                            elements=all_elements,
                            stylesheet=full_network_stylesheet
                        )
                    ]),

                    html.Div(className="network-controls", children=[
                        html.Label("Highlight Node:"),
                        dcc.Dropdown(
                            id='full-node-selector',
                            options=[
                                {
                                    'label': f"{node['data']['id']}   ({node['data']['type']})",
                                    'value': node['data']['id']
                                }
                                for node in full_net['nodes']
                            ],
                            placeholder='Select a node...',
                            style={'fontFamily': 'monospace'}  
                        ),

                        html.Div([
                            dcc.Tabs(
                                id='full-info-tabs',
                                value='regulation',
                                className='node-tabs',
                                children=[
                                    dcc.Tab(label='Regulation', value='regulation', className='node-tab', selected_className='node-tab--selected'),
                                    dcc.Tab(label='Gene Expression', value='expression', className='node-tab', selected_className='node-tab--selected'),
                                ]
                            ),
                            html.Div(id='full-info-content', className='node-info-content') 
                        ], className='node-info-panel'),

                        html.Button("Reset Graph", id="full-reset-button", n_clicks=0, className="reset-btn") 


                    ])
                ])
            ])
        else:
            return html.Div("Error loading GRN data.")
        

    elif tab_name == 'coregs':
        grn=load_grn_data("data/grn.json")
        if grn:
            tf_targets=get_tf_targets(grn)
            coreg_net=create_tf_interaction_network(tf_targets,1)
            all_elements=coreg_net['nodes']+coreg_net['edges']
            return html.Div([
                html.H3("Coregulators Network"),
                dcc.Store(id='coreg-network-store',data=all_elements),
                html.Div(className='coreg-network-layout',children=[
                    html.Div(className="cyto-graph-wrapper", children=[
                        cyto.Cytoscape(
                            id='coreg-network-graph',
                            layout={
                                'name': 'cose',
                                'quality': 'default',
                                'fit': True,
                                'padding': 40,
                                'animate': False,
                                'nodeRepulsion': 1000000,
                                'edgeElasticity': 100,
                                'gravity': 50,
                                'numIter': 1000
                            },
                            style={'width': '100%', 'height': '800px'},
                            elements=all_elements,
                            stylesheet=coreg_network_stylesheet
                        )
                    ]),

                    html.Div(className="network-controls",children=[
                        html.Label("Highlight TF:"),
                        dcc.Dropdown(
                            id='coreg-node-selector',
                            options=[
                                {
                                    'label': f"{node['data']['id']}",
                                    'value': node['data']['id']
                                } for node in coreg_net['nodes']
                            ],
                            placeholder='Select a node...',
                            style={'fontFamily': 'monospace'} 
                        ),
                        html.Div([
                            dcc.Tabs(
                                id='coreg-info-tabs',
                                value='regulation',
                                className='node-tabs',
                                children=[
                                    dcc.Tab(label='Regulation', value='regulation', className='node-tab', selected_className='node-tab--selected'),
                                    dcc.Tab(label='Gene Expression', value='expression', className='node-tab', selected_className='node-tab--selected'),
                                ]
                            ),
                            html.Div(id='coreg-info-content', className='node-info-content') 
                        ], className='node-info-panel'),

                        html.Button("Reset Graph", id="coreg-reset-button", n_clicks=0, className="reset-btn") 

                    ])
                ])
            ])
                
        else:
            return html.Div([
                html.H3('Coregulators Graph'),
                html.P("Here is coregs graph connected with shared targets")
            ])
    elif tab_name == 'targets':
        return html.Div([
            html.H3("Coregulated Graphs"),
            html.P("Here is coregulated graph connected with shared regulators ")
        ])
    elif tab_name == 'samples':
        return html.Div([
            html.H3("Patients Graph"),
            html.P("Here we will put samples/patients graph")
        ])
    else:
        return html.Div("Select a tab please")
