from dash import (
    Input,
    Output,
    State,
    get_app,
)
import dash_ag_grid as dag
from graph.adj import get_byregulation_data

app = get_app()


@app.callback(
    Output({"type": "inspector_tabs_content", "uid": "coregulated"}, "children"),
    Input({"type": "inspector_tabs", "uid": "coregulated"}, "active_tab"),
    Input({"type": "store", "uid": "coregulated"}, "data"),
    State({"type": "network-graph", "uid": "coregulated"}, "elements"),
    prevent_initial_call=True,
)
def update_inspector_tabs(active_tab, store, ___):

    selected = store.get("selected", [])

    threshold = store["threshold"]

    # TODO UPDATE BASED ON THE FINAL PRODUCT
    # CACHE OR RELOAD?

    if active_tab == "table":
        if selected:
            from dash import get_app

            app = get_app()
            cache = app.server.config["SERVER_CACHE"]
            pre_data = cache.get(store["uid"])

            if not pre_data:
                raise NameError("Getting cache has failed")

            edges = [e.copy() for e in ___ if "source" in e["data"]]

            rowData = get_byregulation_data(pre_data, selected, edges, threshold)
        else:
            rowData = []

        return dag.AgGrid(
            rowData=rowData,
            columnSize="responsiveSizeToFit",
            dashGridOptions={
                "suppressHorizontalScroll": True,
            },
            style={"height": "100%"},
            defaultColDef={
                "resizable": True,
                "sortable": True,
                "filter": True,
                "minWidth": 120,
                "flex": 1,
            },
            columnDefs=[
                {
                    "field": "column1",
                    "headerName": "TG (C) ⓘ",
                    "headerTooltip": "Target Gene (Count)",
                },
                {
                    "field": "column2",
                    "headerName": "TF ⓘ",
                    "headerTooltip": "Transcription Factor",
                    "tooltipField": "partner_tooltip",
                    "cellStyle": {
                        "styleConditions": [
                            {
                                "condition": "params.data.is_common",
                                "style": {
                                    "color": "#0052CC",
                                    "fontWeight": "bold",
                                    "textAlign": "left",
                                },
                            }
                        ],
                    },
                },
                {
                    "field": "column3",
                    "headerName": "STFC ⓘ",
                    "headerTooltip": "Shared Transcription Factor Count",
                },
            ],
        )
