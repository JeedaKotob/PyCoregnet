""" 
columns=[
    {"name": partner_label, "id": "Partner"},
    {"name": "Regulation", "id": "Regulation"},
    {"name": "Selected Node", "id": "Source"},
]
"""

from dash import html, dcc, dash_table



def table(id,data,columns):
    return dash_table.DataTable(
            data=data,
            columns=columns,
            page_size=10,
            style_cell={
                'textAlign': 'center',
                'fontFamily': "'Inter', sans-serif",
                'fontSize': '14px',
                'borderBottom': '1px solid #ccc',
                'borderLeft': 'none',
                'borderRight': 'none',
                'borderTop': 'none'
            },
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': 'white',
                'borderBottom': '1px solid #ccc',
                'borderLeft': 'none',
                'borderRight': 'none',
                'borderTop': 'none'
            },
        )