import uuid
import dash
from dash import Dash, dcc, html, callback, Input, Output, no_update
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from flask_caching import Cache
cyto.load_extra_layouts()

app = dash.Dash(__name__, suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)
server = app.server

# Local-friendly cache (persists between runs). For Redis, swap config.
cache = Cache(server, config={
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": ".cache",
    "CACHE_DEFAULT_TIMEOUT": 3600
})
app.server.config["APP_CACHE"] = cache


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
