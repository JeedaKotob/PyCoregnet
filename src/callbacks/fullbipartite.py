from dash import (
    Input,
    Output,
    State,
    html,
    no_update,
    get_app,
)
import dash_ag_grid as dag

app = get_app()


@app.callback(
    Output({"type": "inspector_tabs_content", "uid": "full"}, "children"),
    Input({"type": "inspector_tabs", "uid": "full"}, "active_tab"),
    Input({"type": "store", "uid": "full"}, "data"),
    State({"type": "network-graph", "uid": "full"}, "elements"),
    prevent_initial_call=True,
)
def update_inspector_tabs(active_tab, store, ___):
    """Update inspector tabs based on active tab and store data"""

    if not active_tab:
        return no_update

    selected = store.get("selected", None)

    if active_tab == "table":
        rowData = []

        if not selected:
            return html.Div("Please Select a Node", className="m-auto text-muted")
        else:
            from graph.fullbipartite import get_regulation

            rowData = get_regulation(selected, "./grn.json")
        return dag.AgGrid(
            id={"type": "aggrid-table", "uid": "full"},
            columnDefs=[
                {"headerName": "Selected Node", "field": "Source"},
                {
                    "headerName": "Partner",
                    "field": "Partner",
                    "cellStyle": {
                        "styleConditions": [
                            {
                                "condition": "params.data.shared == 'true' && params.data.Regulation == 'Positive'",
                                "style": {
                                    "backgroundColor": "#D1E7DD",
                                    "color": "#084298",
                                    "fontWeight": "bold",
                                },
                            },
                            {
                                "condition": "params.data.shared == 'true' && params.data.Regulation == 'Negative'",
                                "style": {
                                    "backgroundColor": "#F8D7DA",
                                    "color": "#084298",
                                    "fontWeight": "bold",
                                },
                            },
                            {
                                "condition": "params.data.Regulation == 'Positive'",
                                "style": {
                                    "backgroundColor": "#D1E7DD",
                                    "color": "#0f5132",
                                    "fontWeight": "bold",
                                },
                            },
                            {
                                "condition": "params.data.Regulation == 'Negative'",
                                "style": {
                                    "backgroundColor": "#F8D7DA",
                                    "color": "#842029",
                                    "fontWeight": "bold",
                                },
                            },
                        ]
                    },
                },
            ],
            defaultColDef={"flex": 1},
            columnSize="sizeToFit",
            rowData=rowData,
        )

    elif active_tab == "heatmap":
        if selected:
            from graph.fullbipartite import get_heat_map

            return get_heat_map(selected, "./CIT_BLCA_EXP.csv")
        else:
            return html.Div("Please Select a Node", className="m-auto text-muted")
