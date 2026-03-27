from flask import Flask
import dash
from dash import (
    callback,
    Input,
    Output,
    no_update,
    State,
    callback_context,
)
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from flask_caching import Cache
from components.navbar import get_navbar
from config.app_config import CACHE_CONFIG
from config.ui_config import APP_STYLE

cyto.load_extra_layouts()

server = Flask(__name__)

# tell Flask to use the above defined config
server.config.from_mapping(CACHE_CONFIG)
cache = Cache(server)
server.config["SERVER_CACHE"] = cache

app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    url_base_pathname="/",
)


navbar = get_navbar(dash.page_registry.values())

#  Main layout
app.layout = dbc.Container(
    fluid=True,
    style=APP_STYLE,
    children=[
        navbar,
        dbc.Container(dash.page_container, fluid=True, className="dash-page-container"),
    ],
)


@callback(
    Output("navbar", "children"),
    Input("navbar-title", "n_clicks"),
    Input("navbar-title-sm", "n_clicks"),
    State("navbar", "children"),
    prevent_initial_call=True,
)
def toggle_navbar_dropdowns(title, title_sm, children):
    ctx = callback_context

    if not ctx.triggered:
        return no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "navbar-title":
        children[0]["props"]["className"] = children[0]["props"]["className"].replace(
            "d-none", ""
        )
        for e in children[1:]:
            e["props"]["className"] = e["props"]["className"] + " d-none"
        return children
    elif triggered_id == "navbar-title-sm":
        children[0]["props"]["className"] = (
            children[0]["props"]["className"] + " d-none"
        )
        for e in children[1:]:
            e["props"]["className"] = e["props"]["className"].replace("d-none", "")
        return children

    return no_update


if __name__ == "__main__":
    app.run(debug=True, port=8050)
