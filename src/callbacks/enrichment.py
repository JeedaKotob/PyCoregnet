from dash import Input, Output, State, MATCH, get_app, html
import gseapy as gp

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
        enr = gp.enrichr(
            gene_list=selected,
            gene_sets=gene_sets,
            organism=organism.lower(),
            outdir=None,
        )
        if enr.results.empty:
            return html.Div("No enrichment results found."), False

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
