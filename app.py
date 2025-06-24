from dash import Dash, dcc, html
import dash_cytoscape as cyto
from callbacks import register_callbacks

app = Dash(__name__, suppress_callback_exceptions=True)

cyto.load_extra_layouts()


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='main-content')
])

register_callbacks(app)

if __name__=='__main__':
    app.run(debug=True)