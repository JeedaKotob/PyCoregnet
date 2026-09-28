from dash import (
    Input,
    Output,
    State,
    ctx,
    html,
    no_update,
    get_app,
)
import dash_ag_grid as dag
from graph.adj import get_byregulation_data
from analysis.enrichment import Enrichment
from components.legend import legend_text, table_legend
import callbacks.enrichment  # noqa: F401

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

        grid = dag.AgGrid(
            rowData=rowData,
            columnSize="responsiveSizeToFit",
            className="compact-pagination",
            dashGridOptions={
                "suppressHorizontalScroll": True,
                "pagination": True,
                "paginationPageSize": 10,
                "paginationPageSizeSelector": False,
                "localeText": {"page": "", "to": "-", "of": "/"},
            },
            style={"flex": "1 1 auto", "minHeight": "0"},
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

        legend = table_legend(legend_text("Common coregulator", "#0052CC"))

        return html.Div(
            className="d-flex flex-column",
            style={"height": "100%", "minHeight": "0"},
            children=[legend, grid],
        )

    elif active_tab == "enrichment":
        # Avoid rebuilding GO UI when only the store updates (e.g., graph selection changes).
        if (
            isinstance(ctx.triggered_id, dict)
            and ctx.triggered_id.get("type") == "store"
        ):
            return no_update
        return Enrichment(uid=store["uid"]).unpack()
