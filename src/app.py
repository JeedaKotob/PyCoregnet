import uuid
from flask import Flask
import dash
from dash import Dash, dcc, html, callback, Input, Output, no_update
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from flask_caching import Cache
cyto.load_extra_layouts()

server = Flask(__name__)

# Local-friendly cache (persists between runs). For Redis, swap config.
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 3600
}
# tell Flask to use the above defined config
server.config.from_mapping(config)
cache = Cache(server)
server.config['SERVER_CACHE']=cache

app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    url_base_pathname="/"
)

""" 
#  Common element in every page
navbar = dbc.Navbar(
    children=[
        dbc.NavbarBrand("PyCoregnet", href="/", className="ms-3"),
        dbc.Nav(
            [
                dbc.NavLink(
                    html.Div(page["name"], className="ms-2"),
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            className="ms-auto me-3",
            navbar=True,
        ),
    ],
    color="dark",
    dark=True,
    className="px-0 w-100",
)
"""






"""
#  Common element in every page
# Group pages by parent directory
pages_by_parent = {}
for page in dash.page_registry.values():
    path = page["path"]
    if path == "/":  # Skip homepage
        continue
    parent = path.split("/")[1] if "/" in path else "other"
    if parent not in pages_by_parent:
        pages_by_parent[parent] = []
    pages_by_parent[parent].append(page)

# Create navigation items with dropdowns
nav_items = []
for parent, pages in sorted(pages_by_parent.items()):
    if len(pages) > 1:
        # Create dropdown for multiple pages with same parent
        nav_items.append(
            dbc.DropdownMenu(
                label=parent.capitalize(),
                children=[
                    dbc.DropdownMenuItem(
                        page["name"],
                        href=page["path"],
                    )
                    for page in sorted(pages, key=lambda p: p["name"])
                ],
                nav=True,
                in_navbar=True,
            )
        )
    else:
        # Single page, no dropdown needed
        nav_items.append(
            dbc.NavLink(
                pages[0]["name"],
                href=pages[0]["path"],
                active="exact",
            )
        )

navbar = dbc.Navbar(
    children=[
        dbc.NavbarBrand("PyCoregnet", href="/", className="ms-3"),
        dbc.Nav(
            nav_items,
            className="ms-auto me-3",
            navbar=True,
        ),
    ],
    color="dark",
    dark=True,
    className="px-0 w-100",
)
"""

dropdowns = {}
for page in dash.page_registry.values():
    path = page["path"]
    pc = path.split("/")[1:]
    if len(pc) > 1:
        parent,child = pc
        if parent not in dropdowns:
            dropdowns[parent] = []
        dropdowns[parent].append(child)


ddowns = [    
    dbc.DropdownMenu(
        label=parent.capitalize(),
        children=[
            dbc.DropdownMenuItem(
                c,
                href=f"/{parent}/{c}"
            ) for c in child
        ],
        nav=True,
        in_navbar=True,
        className="text-white me-3"
    ) for parent, child in dropdowns.items()
]

navbar = dbc.Navbar(
    children=[
        dbc.NavbarBrand("PyCoregnet", href="/", className="ms-3"),
        dbc.Nav(
            [
                dbc.NavLink(
                    html.Div(page["name"], className="ms-2"),
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values() if page["path"].count("/") < 2
            ],
            className="ms-auto me-3",
            navbar=True,
        ),
    ],
    color="dark",
    dark=True,
    className="px-0 w-100",
)

navbar.children.extend(ddowns)
navbar.children.append(html.Div(className="mx-5"))



# Responsible to make a desktop-app like structure
APP_STYLE = {
    "height": "100vh",
    "display": "flex",
    "flexDirection": "column",
    "padding": "0",
    "backgroundColor": "#f8f9fa"
}

#  Main layout
app.layout = dbc.Container(
    fluid=True,
    style=APP_STYLE,
    children=[
        navbar,
        dbc.Container(
            dash.page_container,
            fluid=True,
            className="dash-page-container"
        )
    ],
)

if __name__ == '__main__':
    app.run(debug=True,port=8050)
