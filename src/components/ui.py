import dash_bootstrap_components as dbc
from dash import dcc, html


def btn_grp(id: str, label: str, options: list, value: str):
    """Custome Button Group"""
    return dbc.Row(
        [
            dbc.Col(dbc.Label(label, className="small text-cxenter ")),
            dbc.Col(
                dbc.RadioItems(
                    id=id,
                    className="btn-group btn-group-sm",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary btn-sm text-center",
                    labelCheckedClassName="active btn-sm",
                    options=options,
                    value=value,
                )
            ),
        ],
        justify="between",
        align="center",
        className="mb-3",
    )


def thresh_input(id: dict, label: str):
    btn_id = id.copy()
    btn_id["type"] = btn_id["type"] + "_btn"
    return dbc.Row(
        [
            dbc.Col(
                dbc.Input(id=id, type="number", min=1, size="sm", placeholder=label)
            ),
            dbc.Col(
                dbc.Button(
                    ["Update Threshold"], id=btn_id, size="sm", color="outline-primary"
                )
            ),
        ],
        align="center",
        justify="between",
        className="mb-3",
    )


def dropdown(id: str, label: str, options=[]):
    return dbc.Row(
        [
            dbc.Row(html.Label(label), className="mb-2"),
            dbc.Row(dcc.Dropdown(id=id, className="mb-2", options=options)),
        ]
    )


def tabs(id: str, options: list):
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    dbc.Tabs(
                        id=id,
                        className="text-black border-0 justify-content-center",
                        # active_tab=None,
                        children=[
                            dbc.Tab(
                                label=option.get("label", []),
                                tab_id=option.get("tab_id", []),
                                labelClassName="text-black border-0",
                                activeLabelClassName="text-black border-0 border-bottom border-primary border-3",
                                activeTabClassName="text-black border-0",
                                # ) for option,valueId in zip(options,value)
                            )
                            for option in options
                        ],
                    )
                ],
                className="bg-white ",
            ),
            dcc.Loading(
                dbc.CardBody(
                    id={"type": f"{id['type']}_content", "uid": id["uid"]},
                    className="d-flex flex-column flex-grow-1 m-0 p-0",
                    style={"min-height": "0", "overflow": "hidden"},
                ),
                type="circle",
                color="#0d6efd",
                delay_show=300,
                parent_className="d-flex flex-column flex-grow-1",
                parent_style={"minHeight": "0", "overflow": "hidden"},
            ),
        ],
        className="d-flex flex-column flex-grow-1 bg-transparent border-0",
    )


def network_stats(id: str):
    uid = id["uid"]
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Label("Total: ", className="small text-cxenter")),
                    dbc.Col(
                        [
                            html.Span(
                                id={"type": "total_nodes", "uid": uid}, children="0"
                            ),
                            " nodes | ",
                            html.Span(
                                id={"type": "total_edges", "uid": uid}, children="0"
                            ),
                            " edges",
                        ],
                        className="small text-cxenter",
                    ),
                ],
                className="flex-nowrap text-nowrap",
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Label("Selected: ", className="small text-cxenter")),
                    dbc.Col(
                        [
                            html.Span(
                                id={"type": "selected_nodes", "uid": uid}, children="0"
                            ),
                            " nodes | ",
                            html.Span(
                                id={"type": "selected_edges", "uid": uid}, children="0"
                            ),
                            " edges",
                        ],
                        className="small text-cxenter",
                    ),
                ],
                className="flex-nowrap text-nowrap",
            ),
        ]
    )
