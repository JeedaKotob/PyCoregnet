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

coreg_network_stylesheet = [
    {
        "selector": "node",
        "style": {
            "shape":'ellipse',
            'background-color': '#66a3ff',
            'border-color': '#555',
            'border-width': 1,
            'label': 'data(id)', 
            'text-valign': 'center',
            'color': 'white',
            'text-outline-width': 2,
            'text-outline-color': '#333',
            'width': 'mapData(target_count, 0, 150, 35, 65)', 
            'height': 'mapData(target_count, 0, 150, 35, 65)',
            'font-size': 'mapData(target_count, 0, 150, 8, 12)',
            'opacity': 1,
            'transition-property': 'opacity, background-color, border-color, border-width',
            'transition-duration': '0.2s'
        }
    },
    {
        "selector": "edge",
        "style": {
            'line-color': '#ccc',
            'width': 2,
            'opacity': 1,
            'label': 'data(shared_count)',
            'font-size': '10px',
            'color': '#333', 
            'text-background-opacity': 1,
            'text-background-color': '#f0f0f0',
            'text-background-padding': '2px',
            'transition-property': 'opacity,line-color, width',
            'transition-duration': '0.2s'
        }
    },
    {
        "selector": ".highlighted",
        "style": {
            'background-color': '#ff8c00',
            'border-color': '#e67300',
            'border-width': 3,
            'opacity': 1,
            'z-index': 10 
        }
    },
    {
        "selector": ".highlighted-edge",
        "style": {
            'line-color': '#ff8c00',
            'width': 4,
            'opacity': 1,
            'z-index': 9
        }
    },
    {
        "selector": ".faded",
        "style": {
            'opacity': 0.15,
            'background-color': '#e0e0e0',
            'border-color': '#c0c0c0',
            'line-color': '#d0d0d0', 
            'text-outline-color': '#d0d0d0',
            'color': '#999'
        }
    },

]

target_network_stylesheet = [
    {
        "selector": "node",
        "style": {
            "shape":'ellipse',
            'background-color': '#66a3ff',
            'border-color': '#555',
            'border-width': 1,
            'label': 'data(id)', 
            'text-valign': 'center',
            'color': 'white',
            'text-outline-width': 2,
            'text-outline-color': '#333',
            'width': 'mapData(tf_count, 10, 25, 50, 100)', 
            'height': 'mapData(tf_count, 10, 25, 50, 100)',
            'font-size': 'mapData(tf_count, 10, 25, 8, 30)',
            'opacity': 1,
            'transition-property': 'opacity, background-color, border-color, border-width',
            'transition-duration': '0.2s'
        }
    },
    {
        "selector": "edge",
        "style": {
            'line-color': '#ccc',
            'width': 2,
            'opacity': 1,
            'label': 'data(shared_count)',
            'font-size': '10px',
            'color': '#333', 
            'text-background-opacity': 1,
            'text-background-color': '#f0f0f0',
            'text-background-padding': '2px',
            'transition-property': 'opacity,line-color, width',
            'transition-duration': '0.2s'
        }
    },
    {
        "selector": ".highlighted",
        "style": {
            'background-color': '#ff8c00',
            'border-color': '#e67300',
            'border-width': 3,
            'opacity': 1,
            'z-index': 10 
        }
    },
    {
        "selector": ".highlighted-edge",
        "style": {
            'line-color': '#ff8c00',
            'width': 4,
            'opacity': 1,
            'z-index': 9
        }
    },
    {
        "selector": ".faded",
        "style": {
            'opacity': 0.15,
            'background-color': '#e0e0e0',
            'border-color': '#c0c0c0',
            'line-color': '#d0d0d0', 
            'text-outline-color': '#d0d0d0',
            'color': '#999'
        }
    },

]