from dash import html


def legend_item(color, label, text_color="#212529"):
    """A colored swatch paired with a label, for a cell rule that fills a background."""
    return html.Span(
        className="d-inline-flex align-items-center",
        children=[
            html.Span(
                style={
                    "display": "inline-block",
                    "width": "10px",
                    "height": "10px",
                    "borderRadius": "2px",
                    "backgroundColor": color,
                    "border": "1px solid rgba(0,0,0,0.15)",
                    "marginRight": "5px",
                }
            ),
            html.Span(label, style={"color": text_color}),
        ],
    )


def legend_text(label, text_color):
    """A text-only entry, for a cell rule that recolors text rather than filling a background."""
    return html.Span(label, className="fw-bold", style={"color": text_color})


def table_legend(*items):
    """A centered, wrapping legend bar to place above an AG Grid table."""
    return html.Div(
        className="d-flex flex-wrap justify-content-center align-items-center px-2 py-1 border-bottom bg-white",
        style={
            "fontSize": "0.75rem",
            "flexShrink": "0",
            "rowGap": "4px",
            "columnGap": "1rem",
        },
        children=list(items),
    )
