"""
Stats callbacks.

Contains callbacks that compute and display graph summary metrics.

Callbacks:
- update_network_stats: updates total and selected node/edge counters.
"""

from dash import Input, Output, State, MATCH, get_app


app = get_app()


@app.callback(
    [
        Output({"type": "total_nodes", "uid": MATCH}, "children"),
        Output({"type": "total_edges", "uid": MATCH}, "children"),
        Output({"type": "selected_nodes", "uid": MATCH}, "children"),
        Output({"type": "selected_edges", "uid": MATCH}, "children"),
    ],
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "network-graph", "uid": MATCH}, "elements"),
)
def update_network_stats(store, elements):
    selected = store["selected"]
    metadata = store["metadata"]
    t = 0
    tf = 0

    for e in elements:
        data = e["data"]
        source = data.get("source", None)
        target = data.get("target", None)
        if source in selected:
            t = t + 1
        elif target in selected:
            tf = tf + 1

    total = t + tf

    return metadata["total_nodes"], metadata["total_edges"], len(selected), total
