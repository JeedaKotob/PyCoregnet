import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc

def btn_grp(id: str, label: str, options: list, value: str):
    """Custome Button Group """
    return dbc.Row(
        [
            dbc.Col(
                dbc.Label(label, className="small text-center "),width="auto"
            ),
            dbc.Col(
                dbc.RadioItems(
                    id=id,
                    className="btn-group btn-group-sm",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary btn-sm text-center",
                    labelCheckedClassName="active btn-sm",
                    options=options,
                    value=value,
                ),
                width="auto"
            ),
        ],
        justify="between",
        align="center",
        className="mb-3" 
    )













if __name__ == "__main__":

    app = dash.Dash(__name__)

    app.layout = html.Div([
        
    ])

    app.run(debug=True)