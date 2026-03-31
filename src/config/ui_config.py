# Responsible to make a desktop-app like structure
APP_STYLE = {
    "backgroundColor": "#f8f9fa",
    "display": "flex",
    "flexDirection": "column",
    "height": "100vh",
    "padding": "0",
}

# UI controls cards
_DEFAULT_CARD_CLASS = "d-flex flex-column"

_CARD_CLASS_NAME = "mb-2"
_CARD_HEADER_CLASS_NAME = None

_CARD_BODY_CLASS_NAME = {
    "Graph Controls": _DEFAULT_CARD_CLASS,
    "Insights": f"{_DEFAULT_CARD_CLASS} p-0",
    "Network Stats": _DEFAULT_CARD_CLASS,
    "Node Inspector": _DEFAULT_CARD_CLASS,
}

_CARD_STYLE = {
    "Insights": {
        "height": "400px",
    }
}

# Cytograph
_CYTOGRAPH_CLASS_NAME = "bg-light"
_CYTOGRAPH_STYLE = {
    "border-radius": "8px",
    "box-sizing": "border-box",
    "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "flex-grow": "1",
}

# Page layout
_UILAYOUT_CONTAINER_CLASS_NAME = "p-0 m-0 h-100"
_UILAYOUT_MAIN_CONTENT_CLASS_NAME = (
    "d-flex flex-column overflow-hidden p-2 bg-secondary"
)
_UILAYOUT_ROW_CLASS_NAME = "g-0 h-100"
_UILAYOUT_SIDEBAR_CLASS_NAME = "bg-secondary text-white p-3 h-100 overflow-auto"
