from dash import Input, Output, State, get_app, html
import dash_ag_grid as dag
import gseapy as gp
from graph.adj import get_byregulation_data
from graph.common import GOEWrapper

app = get_app()


@app.callback(
    Output({"type": "inspector_tabs_content", "uid": "coregs"}, "children"),
    Input({"type": "inspector_tabs", "uid": "coregs"}, "active_tab"),
    Input({"type": "store", "uid": "coregs"}, "data"),
    State({"type": "network-graph", "uid": "coregs"}, "elements"),
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
                    "headerName": "TF (C) ⓘ",
                    "headerTooltip": "Transcription Factor (Count)",
                },
                {
                    "field": "column2",
                    "headerName": "Coreg ⓘ",
                    "headerTooltip": "Coregulator",
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
                    "headerName": "STC ⓘ",
                    "headerTooltip": "Shared Target Count",
                },
            ],
        )

    elif active_tab == "GO":
        return GOEWrapper(uid=store["uid"]).unpack()


@app.callback(
    Output(
        {"type": "goe-dropdown-gene-sets", "uid": "coregs"},
        "disabled",
        allow_duplicate=True,
    ),
    Input({"type": "goe-dropdown-organism", "uid": "coregs"}, "value"),
    prevent_initial_call=True,
)
def disable_gene_sets_while_loading(_organism):
    return True


@app.callback(
    Output({"type": "goe-dropdown-gene-sets", "uid": "coregs"}, "options"),
    Output({"type": "goe-dropdown-gene-sets", "uid": "coregs"}, "disabled"),
    Input({"type": "goe-dropdown-organism", "uid": "coregs"}, "value"),
)
def update_gene_sets_by_organism(organism):
    if not organism:
        return [], True

    try:
        if organism == "All":
            names = gp.get_library_name()
        else:
            names = gp.get_library_name(organism=organism)
    except Exception:
        return [], True

    options = [{"label": name, "value": name} for name in names]
    return options, False


@app.callback(
    Output(
        {"type": "goe-run-analysis", "uid": "coregs"},
        "disabled",
        allow_duplicate=True,
    ),
    Input({"type": "goe-run-analysis", "uid": "coregs"}, "n_clicks"),
    prevent_initial_call=True,
)
def disable_run_button_while_loading(_n_clicks):
    return True


@app.callback(
    Output({"type": "goe-results", "uid": "coregs"}, "children"),
    Output({"type": "goe-run-analysis", "uid": "coregs"}, "disabled"),
    Input({"type": "goe-run-analysis", "uid": "coregs"}, "n_clicks"),
    State({"type": "goe-dropdown-organism", "uid": "coregs"}, "value"),
    State({"type": "goe-dropdown-gene-sets", "uid": "coregs"}, "value"),
    State({"type": "store", "uid": "coregs"}, "data"),
    prevent_initial_call=True,
)
def run_enrichment_analysis(n_clicks, organism, gene_set, store):
    selected = store.get("selected", [])

    if not selected:
        return html.Div("Please select at least one gene."), False
    if not organism or organism == "All":
        return html.Div("Please choose a specific organism."), False
    if not gene_set:
        return html.Div("Please choose a gene set library."), False

    gene_sets = [gene_set] if isinstance(gene_set, str) else gene_set

    try:
        # enr = gp.enrichr(
        #     gene_list=selected,
        #     gene_sets=gene_sets,
        #     organism=organism.lower(),
        #     outdir=None,
        # )
        enr = gp.enrichr(
            gene_list=["TGFB1I1"],
            gene_sets=["GO_Biological_Process_2023"],
            organism="human",
            outdir=None,
        )
        if enr.results.empty:
            return html.Div("No enrichment results found."), False

        print(enr.results)

        top = enr.results[["Term", "Adjusted P-value"]].head(10)
        return (
            html.Ul(
                [
                    html.Li(f"{row['Term']} (adj p={row['Adjusted P-value']:.3g})")
                    for _, row in top.iterrows()
                ]
            ),
            False,
        )
    except Exception as e:
        return html.Div(f"Enrichment failed: {e}"), False
