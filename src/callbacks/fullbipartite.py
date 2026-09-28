from dash import (
    Input,
    Output,
    State,
    html,
    no_update,
    get_app,
)
import dash_ag_grid as dag
from components.legend import legend_text, table_legend

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

    selected = store.get("selected", [])

    if active_tab == "table":
        if selected:
            from graph.fullbipartite import get_regulation

            rowData = get_regulation(selected)
        else:
            rowData = []

        grid = dag.AgGrid(
            id={"type": "aggrid-table", "uid": "full"},
            columnDefs=[
                {
                    "headerName": "Selected Node",
                    "field": "Source",
                    "cellStyle": {
                        "styleConditions": [
                            {
                                "condition": "params.data.partner_label == 'Target'",
                                "style": {
                                    "color": "#B8860B",
                                    "fontWeight": "bold",
                                },
                            },
                            {
                                "condition": "params.data.partner_label == 'TF'",
                                "style": {
                                    "color": "#2166AC",
                                    "fontWeight": "bold",
                                },
                            },
                        ]
                    },
                },
                {
                    "headerName": "Partner",
                    "field": "Partner",
                    "cellStyle": {
                        "styleConditions": [
                            {
                                "condition": "params.data.shared == 'true'",
                                "style": {
                                    "color": "#6A51A3",
                                    "fontWeight": "bold",
                                },
                            },
                            {
                                "condition": "params.data.Regulation == 'Positive'",
                                "style": {
                                    "color": "#1B7837",
                                    "fontWeight": "bold",
                                },
                            },
                            {
                                "condition": "params.data.Regulation == 'Negative'",
                                "style": {
                                    "color": "#B2182B",
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
            style={"flex": "1 1 auto", "minHeight": "0"},
            className="compact-pagination",
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 10,
                "paginationPageSizeSelector": False,
                "localeText": {"page": "", "to": "-", "of": "/"},
            },
        )

        legend = table_legend(
            legend_text("Target", "#B8860B"),
            legend_text("TF", "#2166AC"),
            legend_text("Positive", "#1B7837"),
            legend_text("Negative", "#B2182B"),
            legend_text("Shared partner", "#6A51A3"),
        )

        return html.Div(
            className="d-flex flex-column",
            style={"height": "100%", "minHeight": "0"},
            children=[legend, grid],
        )

    elif active_tab == "heatmap":
        if selected:
            from graph.fullbipartite import get_heat_map

            return get_heat_map(selected)
        else:
            return html.Div("Please Select a Node", className="m-auto text-muted")


# @app.callback(
#     [
#         Output({"type": "main-content", "uid": "full"}, "children"),
#         Output({"type": "insights-card-body", "uid": "full"}, "children"),
#         Output({"type": "network-graph", "uid": "full"}, "tapNodeData"),
#     ],
#     Input({"type": "insights_switch_view_btn", "uid": "full"}, "n_clicks"),
#     State({"type": "main-content", "uid": "full"}, "children"),
#     State({"type": "insights-card-body", "uid": "full"}, "children"),
#     prevent_initial_call=True,
# )
# def switch_view(btn, main_content, insights_content):

#     if not isinstance(main_content, list):
#         main_content = [main_content]

#     if not isinstance(insights_content, list):
#         insights_content = [insights_content]

#     # Clear transient tap state so stale node taps are not replayed after swapping views.
#     return insights_content, main_content, None
