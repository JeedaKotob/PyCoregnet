from dash import dcc, html
import dash_bootstrap_components as dbc


class Enrichment:
    "Gene Ontology Enrichment"

    def __init__(self, uid):
        self.uid = uid

    def unpack(self):
        return dbc.Container(
            fluid=True,
            className="p-0 d-flex flex-column flex-grow-1",
            children=[
                dbc.Card(
                    className="flex-grow-1",
                    children=dbc.CardBody(
                        className="p-0 d-flex flex-column",
                        style={"min-height": "0"},
                        children=[
                            html.Div(
                                id={"type": "goe-input-section", "uid": self.uid},
                                className="p-3",
                                children=[
                                    html.Div(
                                        "GO Input",
                                        className="text-uppercase fw-semibold small mb-1",
                                    ),
                                    html.H5(
                                        "Gene Ontology Enrichment",
                                        className="mb-1 fw-semibold",
                                    ),
                                    html.P(
                                        "Selected genes from the graph are used as input for enrichment.",
                                        className="small mb-3",
                                    ),
                                    dbc.Row(
                                        className="g-3",
                                        children=[
                                            dbc.Col(
                                                xs=12,
                                                children=[
                                                    html.Label(
                                                        "Organism",
                                                        className="small fw-semibold mb-2",
                                                    ),
                                                    dcc.Dropdown(
                                                        id={
                                                            "type": "goe-dropdown-organism",
                                                            "uid": self.uid,
                                                        },
                                                        options=[
                                                            "Human",
                                                            "Mouse",
                                                            "Yeast",
                                                            "Fly",
                                                            "Fish",
                                                            "Worm",
                                                        ],
                                                        placeholder="Choose organism",
                                                        className="mb-0",
                                                        maxHeight=220,
                                                    ),
                                                ],
                                            ),
                                            dbc.Col(
                                                xs=12,
                                                children=[
                                                    html.Label(
                                                        "Gene Sets",
                                                        className="small fw-semibold mb-2",
                                                    ),
                                                    dcc.Loading(
                                                        type="default",
                                                        color="#2f6b57",
                                                        children=dcc.Dropdown(
                                                            id={
                                                                "type": "goe-dropdown-gene-sets",
                                                                "uid": self.uid,
                                                            },
                                                            className="mb-0",
                                                            placeholder="Select an organism to load gene sets",
                                                            disabled=True,
                                                            maxHeight=220,
                                                            multi=True,
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    dbc.Button(
                                        "Run Enrichment Analysis",
                                        id={
                                            "type": "goe-run-analysis",
                                            "uid": self.uid,
                                        },
                                        color="success",
                                        className="w-100 mt-2 fw-semibold border-0",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="d-flex px-3 justify-content-between align-items-center mt-2",
                                children=[
                                    html.Div(
                                        "Results",
                                        className="text-uppercase fw-semibold small",
                                    ),
                                    dbc.Button(
                                        "Expand",
                                        id={
                                            "type": "goe-collapse-toggle",
                                            "uid": self.uid,
                                        },
                                        size="sm",
                                        color="link",
                                        className="p-0 text-decoration-none",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="border rounded p-0 mt-1 flex-grow-1 d-flex flex-column",
                                style={"min-height": "0"},
                                children=dcc.Loading(
                                    type="default",
                                    color="#2f6b57",
                                    parent_className="flex-grow-1 d-flex flex-column",
                                    parent_style={"min-height": "0"},
                                    className="flex-grow-1 d-flex flex-column",
                                    style={"min-height": "0"},
                                    children=html.Div(
                                        id={"type": "goe-results", "uid": self.uid},
                                        className="flex-grow-1 d-flex flex-column",
                                        style={"min-height": "0"},
                                        children="Results will appear here.",
                                    ),
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )
