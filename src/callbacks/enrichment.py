import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import MATCH, Input, Output, State, ctx, get_app, html, no_update

app = get_app()


@app.callback(
    Output(
        {"type": "goe-dropdown-gene-sets", "uid": MATCH},
        "disabled",
        allow_duplicate=True,
    ),
    Input({"type": "goe-dropdown-organism", "uid": MATCH}, "value"),
    prevent_initial_call=True,
)
def disable_gene_sets_while_loading(_organism):
    """Disable the gene-set dropdown as soon as the organism changes, until its libraries load."""
    return True


@app.callback(
    Output({"type": "goe-dropdown-gene-sets", "uid": MATCH}, "options"),
    Output({"type": "goe-dropdown-gene-sets", "uid": MATCH}, "disabled"),
    Input({"type": "goe-dropdown-organism", "uid": MATCH}, "value"),
)
def update_gene_sets_by_organism(organism):
    """Fill the gene-set dropdown with the Enrichr libraries available for the chosen organism."""
    if not organism:
        return [], True

    try:
        import gseapy as gp

        names = gp.get_library_name(organism=organism)
    except Exception:
        return [], True

    options = [{"label": name, "value": name} for name in names]
    return options, False


@app.callback(
    Output(
        {"type": "goe-run-analysis", "uid": MATCH},
        "disabled",
        allow_duplicate=True,
    ),
    Input({"type": "goe-run-analysis", "uid": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def disable_run_button_while_loading(_n_clicks):
    """Disable the Run button immediately on click so the analysis can't be started twice."""
    return True


@app.callback(
    Output({"type": "goe-results-grid", "uid": MATCH}, "exportDataAsCsv"),
    Input({"type": "goe-export-csv", "uid": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def export_enrichment_results(n_clicks):
    """Trigger the export of the enrichment results AgGrid to CSV."""
    return bool(n_clicks)


@app.callback(
    Output(
        {"type": "goe-run-analysis", "uid": MATCH},
        "disabled",
        allow_duplicate=True,
    ),
    Output(
        {"type": "goe-input-section", "uid": MATCH},
        "className",
        allow_duplicate=True,
    ),
    Output(
        {"type": "goe-results", "uid": MATCH},
        "children",
        allow_duplicate=True,
    ),
    Input({"type": "goe-reset", "uid": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def reset_enrichment_inputs(n_clicks):
    """Show the input section again and re-enable Run after the user clicks Reset."""
    # Fires when the Reset button is first rendered (n_clicks=None) since the
    # input section already exists; ignore that so the inputs stay hidden.
    if not n_clicks:
        return no_update, no_update, no_update
    return False, "p-3", []


@app.callback(
    Output({"type": "goe-results", "uid": MATCH}, "children"),
    Output({"type": "goe-run-analysis", "uid": MATCH}, "disabled"),
    Output({"type": "goe-input-section", "uid": MATCH}, "className"),
    Input({"type": "goe-run-analysis", "uid": MATCH}, "n_clicks"),
    State({"type": "goe-dropdown-organism", "uid": MATCH}, "value"),
    State({"type": "goe-dropdown-gene-sets", "uid": MATCH}, "value"),
    State({"type": "store", "uid": MATCH}, "data"),
    prevent_initial_call=True,
)
def run_enrichment_analysis(_n_clicks, organism, gene_set, store):
    """Run Enrichr on the selected genes, render the results grid, re-enable Run and hide the inputs."""
    uid = ctx.triggered_id["uid"]
    selected = store.get("selected", []) if isinstance(store, dict) else []

    if not selected:
        return (
            html.Div(
                "Please select at least one gene.", className="text-center text-muted"
            ),
            False,
            no_update,
        )
    if not organism:
        return (
            html.Div(
                "Please choose a specific organism.", className="text-center text-muted"
            ),
            False,
            no_update,
        )
    if not gene_set:
        return (
            html.Div("Please choose a gene set library.", className="text-center"),
            False,
            no_update,
        )
    gene_sets = [gene_set] if isinstance(gene_set, str) else gene_set

    try:
        import gseapy as gp

        enr = gp.enrichr(
            gene_list=selected,
            gene_sets=gene_sets,
            organism=organism.lower(),
            outdir=None,
        )
        if enr.results.empty:
            return html.Div("No enrichment results found."), False, no_update

        table = enr.results.drop(
            columns=["Old P-value", "Old Adjusted P-value"], errors="ignore"
        )

        column_min_widths = {
            "Gene_set": 140,
            "Term": 220,
            "Overlap": 90,
            "P-value": 110,
            "Adjusted P-value": 130,
            "Odds Ratio": 110,
            "Combined Score": 130,
            "Genes": 220,
        }

        return (
            [
                html.Div(
                    className="d-flex justify-content-between align-items-center px-3 m-2",
                    children=[
                        html.Label(
                            "Results",
                            className="small fw-semibold mb-0",
                        ),
                        html.Div(
                            className="d-flex gap-2",
                            children=[
                                dbc.Button(
                                    "Export",
                                    id={"type": "goe-export-csv", "uid": uid},
                                    size="sm",
                                ),
                                dbc.Button(
                                    "Reset",
                                    id={"type": "goe-reset", "uid": uid},
                                    size="sm",
                                ),
                            ],
                        ),
                    ],
                ),
                dag.AgGrid(
                    id={"type": "goe-results-grid", "uid": uid},
                    rowData=table.to_dict("records"),
                    columnDefs=[
                        {"field": col, "minWidth": column_min_widths.get(col, 120)}
                        for col in table.columns
                    ],
                    style={"height": "100%", "width": "100%"},
                    className="compact-pagination",
                    dashGridOptions={
                        "domLayout": "normal",
                        "pagination": True,
                        "paginationPageSize": 10,
                        "paginationPageSizeSelector": False,
                        "localeText": {"page": "", "to": "-", "of": "/"},
                    },
                    defaultColDef={
                        "resizable": True,
                        "sortable": True,
                        "filter": True,
                        "flex": 1,
                    },
                ),
            ],
            False,
            "d-none",
        )
    except Exception as e:
        return html.Div(f"Enrichment failed: {e}"), False, no_update
