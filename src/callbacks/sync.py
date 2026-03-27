"""
Dash callbacks for graph interaction synchronization.

Included callbacks:
- sync: propagates UI events to the per-graph store.
- dropdown_selection_mode: updates dropdown `multi`/`disabled` from store state.
- highlightor: applies node/edge highlight classes from current selection.

Key concept:
- Store: canonical state container for each graph's metadata and user selections.
"""

from dash import (
    Input,
    Output,
    State,
    no_update,
    ctx,
    MATCH,
    ALL,
    Patch,
    get_app,
)

app = get_app()


def _get_first(val):
    if isinstance(val, list) and val:
        assert len(val) == 1
        return val[0]
    return val


# All UI Input goes to the store
@app.callback(
    [
        Output({"type": "store", "uid": MATCH}, "data"),
        Output({"type": "options_dropdown", "uid": MATCH}, "value"),
    ],
    [
        Input({"type": "network-graph", "uid": MATCH}, "tapNodeData"),
        Input({"type": "options_dropdown", "uid": MATCH}, "value"),
        Input({"type": "selection_mode", "uid": ALL}, "value"),
        Input({"type": "filter_mode", "uid": ALL}, "value"),
        Input({"type": "backtracking_mode", "uid": ALL}, "value"),
        Input({"type": "threshold_input_btn", "uid": ALL}, "n_clicks"),
    ],
    State({"type": "threshold_input", "uid": ALL}, "value"),
    State({"type": "store", "uid": MATCH}, "data"),
)
def sync(
    tapNodeData,
    dropdown_value,
    selection_mode,
    filter_mode,
    backtracking_mode,
    threshold_btn,
    threshold_value,
    store,
):
    trigger = ctx.triggered_id

    assert isinstance(store, dict)  # Catch problems from ALL pattern-matched inputs

    # Update store based on which control triggered the app.callback
    if trigger:
        t_type = trigger.get("type") if isinstance(trigger, dict) else trigger

        if t_type == "selection_mode":
            val = _get_first(selection_mode)
            if val:
                store["selection_mode"] = val

        elif t_type == "filter_mode":
            val = _get_first(filter_mode)
            if val:
                store["filter_mode"] = val

        elif t_type == "backtracking_mode":
            val = _get_first(backtracking_mode)
            if val:
                store["backtracking_mode"] = val

        elif t_type == "threshold_input_btn":
            val = _get_first(threshold_value)
            if val is not None:
                store["threshold"] = val
        elif t_type == "network-graph" and tapNodeData:
            sel_mode = store.get("selection_mode", "single")

            if sel_mode == "off":
                return no_update, no_update

            node_id = tapNodeData.get("id")
            node_type = tapNodeData.get("type")
            if not node_id:
                return store, no_update

            # Check if node matches the current filter mode
            filt_mode = store.get("filter_mode")
            if node_type is not None:
                if filt_mode == "target" and node_type != "target":
                    return store, no_update
                elif filt_mode == "tf" and node_type != "tf":
                    return store, no_update
            # 'both' allows all node types, and None type passes through

            if sel_mode == "single":
                store["selected"] = [node_id]
                return store, node_id
            elif sel_mode == "multiple":
                selected = store.get("selected", [])
                if isinstance(selected, str):
                    selected = [selected]
                temp = set(selected)
                temp.add(node_id)
                store["selected"] = list(temp)
                return store, store["selected"]

        elif t_type == "options_dropdown":
            val = dropdown_value
            sel_mode = store.get("selection_mode", "single")
            if not val:
                store["selected"] = []
                return store, no_update
            if sel_mode == "single":
                store["selected"] = [val]
                return store, no_update
            elif sel_mode == "multiple":
                temp = set(store.get("selected", []))
                # val could be a list or a single value
                if isinstance(val, list):
                    temp.update(val)
                    # If user deselected, keep only current dropdown values
                    if len(temp) > len(val):
                        temp = set(val)
                    store["selected"] = list(temp)
                    return store, no_update
                else:
                    temp.add(val)
                    store["selected"] = list(temp)
                    return store, no_update

    return store, no_update


@app.callback(
    Output({"type": "threshold_input", "uid": ALL}, "value"),
    Input({"type": "main-content", "uid": ALL}, "children"),
    State({"type": "store", "uid": ALL}, "data"),
)
def update_thresh(children, store):
    store = _get_first(store)
    threshold = store.get("threshold", []) if store else []
    if threshold:
        return [threshold]
    return [no_update]


@app.callback(
    [
        Output({"type": "options_dropdown", "uid": MATCH}, "multi"),
        Output({"type": "options_dropdown", "uid": MATCH}, "disabled"),
    ],
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "options_dropdown", "uid": MATCH}, "multi"),
    State({"type": "options_dropdown", "uid": MATCH}, "disabled"),
    prevent_initial_call=True,
)
def dropdown_selection_mode(store, multi, disabled):
    selection_mode = store.get("selection_mode")

    if selection_mode == "single":
        if multi is False and disabled is False:
            return no_update, no_update
        return False, False

    elif selection_mode == "multiple":
        if multi is True and disabled is False:
            return no_update, no_update
        return True, False

    elif selection_mode == "off":
        if disabled is True:
            return no_update, no_update
        return no_update, True

    return no_update, no_update


@app.callback(
    Output({"type": "network-graph", "uid": MATCH}, "elements"),
    Input({"type": "store", "uid": MATCH}, "data"),
    State({"type": "network-graph", "uid": MATCH}, "elements"),
    prevent_initial_call=True,
)
def highlightor(store, elements):

    selected_val = store["selected"]
    if isinstance(selected_val, str):
        selected = {selected_val}
    else:
        selected = set(selected_val) if selected_val else set()

    if not selected:
        patch = Patch()
        for i in range(len(elements)):
            patch[i] = elements[i].copy()
            patch[i]["classes"] = ""
        return patch

    connected_nodes = set()
    patch = Patch()

    # First pass: identify connected nodes
    for i, e in enumerate(elements):
        if "source" in e["data"]:
            src = e["data"]["source"]
            tgt = e["data"]["target"]
            if selected & {src, tgt}:
                connected_nodes.update([src, tgt])

    # Second pass: apply classes using patch
    for i, e in enumerate(elements):
        elem_copy = e.copy()

        if "source" in e["data"]:  # Edge
            src = e["data"]["source"]
            tgt = e["data"]["target"]
            if selected & {src, tgt}:
                elem_copy["classes"] = "highlighted-edge"
            else:
                elem_copy["classes"] = "faded"
        else:  # Node
            nid = e["data"]["id"]
            if nid in selected:
                elem_copy["classes"] = "highlighted"
            elif nid in connected_nodes:
                elem_copy["classes"] = ""
            else:
                elem_copy["classes"] = "faded"

        patch[i] = elem_copy

    return patch
