"""
View callbacks.

Contains callbacks that swap or reorganize rendered layout sections.

Callbacks:
- switch_view: swaps main graph and insights content panes.
"""

from dash import Input, Output, State, MATCH, get_app


app = get_app()


@app.callback(
    [
        Output({"type": "main-content", "uid": MATCH}, "children"),
        Output({"type": "insights-card-body", "uid": MATCH}, "children"),
        Output({"type": "network-graph", "uid": MATCH}, "tapNodeData"),
    ],
    Input({"type": "insights_switch_view_btn", "uid": MATCH}, "n_clicks"),
    State({"type": "main-content", "uid": MATCH}, "children"),
    State({"type": "insights-card-body", "uid": MATCH}, "children"),
    prevent_initial_call=True,
)
def switch_view(btn, main_content, insights_content):
    if not isinstance(main_content, list):
        main_content = [main_content]

    if not isinstance(insights_content, list):
        insights_content = [insights_content]

    # Clear transient tap state so stale node taps are not replayed after swapping views.
    return insights_content, main_content, None
