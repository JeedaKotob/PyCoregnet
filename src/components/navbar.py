from dash import html
import dash_bootstrap_components as dbc


def get_navbar(page_registry):
    """page_registry = dash.page_registry.values()"""

    dropdowns = {}
    for page in page_registry:
        path = page["path"]
        pc = path.split("/")[1:]
        if len(pc) > 1:
            parent, child = pc
            if parent not in dropdowns:
                dropdowns[parent] = []
            dropdowns[parent].append(child)

    ddowns = [
        dbc.DropdownMenu(
            label=parent.capitalize(),
            children=[dbc.DropdownMenuItem(c, href=f"/{parent}/{c}") for c in child],
            nav=True,
            in_navbar=True,
            className="text-white",
        )
        for parent, child in dropdowns.items()
    ]

    return dbc.Navbar(
        children=[
            html.A(
                "PyCoregnet",
                href="#",
                className="text-white text-decoration-none m-2 d-none",
                id="navbar-title-sm",
                n_clicks=0,
            ),
            html.A(
                "PyCoregnet",
                href="#",
                className="text-white text-decoration-none m-2",
                id="navbar-title",
                n_clicks=0,
            ),
            dbc.Nav(
                children=[
                    dbc.NavLink("Home", href="/"),
                ]
                + ddowns
                + [dbc.NavLink("Heatmap", href="/heatmap")],  # TODO Update
                navbar=True,
                id="navbar-content",
                className="",
            ),
        ],
        color="dark",
        dark=True,
        className="w-10 position-absolute z-3 shadow rounded-end-pill rounded-start-0 mt-2 px-2",
        id="navbar",
    )
