from dash import Input, Output, State, MATCH, get_app, html
import dash_ag_grid as dag

app = get_app()


@app.callback(
    Output({"type": "goe-input-section", "uid": MATCH}, "className"),
    Output({"type": "goe-collapse-toggle", "uid": MATCH}, "children"),
    Input({"type": "goe-collapse-toggle", "uid": MATCH}, "n_clicks"),
    State({"type": "goe-input-section", "uid": MATCH}, "className"),
    prevent_initial_call=True,
)
def toggle_goe_input_section(_n_clicks, className):
    if className and "d-none" in className:
        return "p-2", "Expand"
    return "d-none", "Collapse"


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
    return True


@app.callback(
    Output({"type": "goe-dropdown-gene-sets", "uid": MATCH}, "options"),
    Output({"type": "goe-dropdown-gene-sets", "uid": MATCH}, "disabled"),
    Input({"type": "goe-dropdown-organism", "uid": MATCH}, "value"),
)
def update_gene_sets_by_organism(organism):
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
    return True


@app.callback(
    Output({"type": "goe-input-section", "uid": MATCH}, "className", allow_duplicate=True),
    Output({"type": "goe-collapse-toggle", "uid": MATCH}, "children", allow_duplicate=True),
    Input({"type": "goe-run-analysis", "uid": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def collapse_input_on_run(_n_clicks):
    return "d-none", "Expand"


@app.callback(
    Output({"type": "goe-results", "uid": MATCH}, "children"),
    Output({"type": "goe-run-analysis", "uid": MATCH}, "disabled"),
    Input({"type": "goe-run-analysis", "uid": MATCH}, "n_clicks"),
    State({"type": "goe-dropdown-organism", "uid": MATCH}, "value"),
    State({"type": "goe-dropdown-gene-sets", "uid": MATCH}, "value"),
    State({"type": "store", "uid": MATCH}, "data"),
    prevent_initial_call=True,
)
def run_enrichment_analysis(_n_clicks, organism, gene_set, store):
    selected = store.get("selected", []) if isinstance(store, dict) else []

    if not selected:
        return html.Div("Please select at least one gene."), False
    if not organism:
        return html.Div("Please choose a specific organism."), False
    if not gene_set:
        return html.Div("Please choose a gene set library."), False

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
            return html.Div("No enrichment results found."), False

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
            dag.AgGrid(
                rowData=table.to_dict("records"),
                columnDefs=[
                    {"field": col, "minWidth": column_min_widths.get(col, 120)}
                    for col in table.columns
                ],
                style={"height": "100%", "width": "100%"},
                dashGridOptions={
                    "domLayout": "normal",
                    "pagination": True,
                    "paginationPageSize": 10,
                },
                defaultColDef={
                    "resizable": True,
                    "sortable": True,
                    "filter": True,
                    "flex": 1,
                },
            ),
            False,
        )
    except Exception as e:
        return html.Div(f"Enrichment failed: {e}"), False
