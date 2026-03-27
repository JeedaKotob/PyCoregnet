"""
Controls callbacks.

Contains callbacks that derive UI control options from current graph state.

Callbacks:
- create_dropdown_options: rebuilds options list based on graph elements and filter mode.
- update_graph_thresh: rebuilds network elements when threshold is applied.
"""

from dash import Input, Output, State, no_update, ALL, MATCH, get_app

from graph import adj
from services import load_grn


app = get_app()


def _get_first(val):
    if isinstance(val, list) and val:
        assert len(val) == 1
        return val[0]
    return val


@app.callback(
    Output({"type": "options_dropdown", "uid": MATCH}, "options"),
    Input({"type": "network-graph", "uid": MATCH}, "elements"),
    Input({"type": "filter_mode", "uid": ALL}, "value"),
    State({"type": "options_dropdown", "uid": MATCH}, "options"),
)
def create_dropdown_options(elements, filter_mode, current_options):
    # Extract filter_mode from ALL pattern-matched list
    if isinstance(filter_mode, list) and filter_mode:
        filter_mode = filter_mode[0]

    # Get nodes using generator for lower overhead
    nodes = (ele["data"] for ele in elements if "source" not in ele["data"])

    # Get the first node to check data type
    first_node = next(nodes, None)

    # Handle empty nodes case
    if first_node is None:
        return []

    # True when using regulation graph types
    byreg = first_node.get("type") in ["tf", "target"]

    options = []

    # Add first node (already consumed by next)
    label = first_node.get("label", first_node.get("id"))
    if byreg:
        if first_node["type"] == filter_mode or filter_mode == "both":
            label = f"{label} ({first_node['type']})"
            options.append({"label": label, "value": first_node["id"]})
    else:
        options.append({"label": label, "value": first_node["id"]})

    # Process remaining nodes
    for node in nodes:
        label = node.get("label", node.get("id"))

        if byreg:
            if node["type"] == filter_mode or filter_mode == "both":
                label = f"{label} ({node['type']})"
                options.append({"label": label, "value": node["id"]})
        else:
            options.append({"label": label, "value": node["id"]})

    options = sorted(options, key=lambda x: x["label"])

    return options


@app.callback(
    Output({"type": "network-graph", "uid": MATCH}, "elements", allow_duplicate=True),
    Input({"type": "threshold_input_btn", "uid": ALL}, "n_clicks"),
    State({"type": "threshold_input", "uid": ALL}, "value"),
    State({"type": "store", "uid": ALL}, "data"),
    prevent_initial_call=True,
)
def update_graph_thresh(n_clicks, value, store):
    value = _get_first(value)
    store = _get_first(store)

    if not store or value is None:
        return no_update

    genes = adj.get_genes(load_grn(), store["preprocess_role"])
    data = adj.create_network(genes, value)
    return data["nodes"] + data["edges"]
