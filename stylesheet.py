full_network_stylesheet = [
    {
        "selector": "node",
        "style": {
            "label": "data(id)",
            "text-valign": "center",
            "text-halign": "center",
            "opacity":1,
            "width": "label",
            "height": 70,
            "font-size":25,
            "border-width":2,
            "border-color":"#555",
            "transition-property":"opacity, background-color, border-color",
            "padding":"12px",
            'transition-duration':"0.2s",
            "text-wrap": "wrap",
            "text-max-width": 100
        }
    },
    {
        "selector": "node[type='tf']",
        "style": {
           "background-color":"#4473b8",
           'shape': 'ellipse',
           'color': 'white',
           'text-outline-color': '#333',
           'text-outline-width': 2
        }
    },
    {
        "selector": "node[type='target']",
        "style": {
           "background-color":'#c2b62f',
           'shape': 'rectangle',
           'color': 'black',
        }
    },
    {
        "selector": "edge[interaction_type='Activation']",
        "style": {
            "line-color": "#00b200",
            'target-arrow-color':'#00b200'
        }
    },
    {
        "selector": "edge[interaction_type='Repression']",
        "style": {
            "line-color": "#e60000",
            'target-arrow-color':'#e60000',
            'target-arrow-shape': 'tee'
        }
    },
    {
        "selector": ".highlighted",
        "style": {
            "border-width": 4,
            "border-color": '#ff8c00',
            "opacity":1,
            "z-index":10
        }
    },
    {
        "selector": ".highlighted-edge",
        "style": {
            # 'line-color': '#ff8c00',
            # 'target-arrow-color': '#ff8c00',
            'width': 3,
            'opacity': 1,
            'z-index': 9
        }
    },
    {
        "selector": ".faded",
        "style": {
            'opacity': 0.04,
        }
    },

]

