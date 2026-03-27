import dash
from dash import dcc, dash_table
import random
import plotly.graph_objects as go
import pandas as pd
from components.backend import table
from services import load_grn, load_expression_matrix


def create_network(grn_data):
    edges = []
    nodes = []
    bygene = grn_data.get("adjlist").get("bygene")
    bytf = grn_data.get("adjlist").get("bytf")
    tfs = sorted(bytf.keys())

    targets = sorted([g for g in bygene.keys() if g not in tfs])
    for tf, tf_data in bytf.items():
        for tgt in tf_data.get("act", []):
            edges.append(
                {
                    "data": {
                        "id": f"{tf}->{tgt}",
                        "source": tf,
                        "target": tgt,
                        "interaction_type": "Activation",
                    }
                }
            )
        for tgt in tf_data.get("rep", []):
            edges.append(
                {
                    "data": {
                        "id": f"{tf}->{tgt}",
                        "source": tf,
                        "target": tgt,
                        "interaction_type": "Repression",
                    }
                }
            )

    # TFs left
    for tf in tfs:
        nodes.append(
            {
                "data": {"id": tf, "type": "tf"},
                "position": {
                    "x": random.randint(50, 400),
                    "y": random.randint(50, 2500),
                },
            }
        )

    # Target genes right
    for tgt in targets:
        nodes.append(
            {
                "data": {"id": tgt, "type": "target"},
                "position": {
                    "x": random.randint(1000, 4000),
                    "y": random.randint(50, 2500),
                },
            }
        )

    return {"nodes": nodes, "edges": edges}


def options(graph_net):
    return [
        {
            "label": f"{node['data']['id']}   ({node['data']['type']})",
            "value": node["data"]["id"],
        }
        for node in graph_net
    ]


layout = {"name": "preset", "fit": True}


def get_heat_map(genes):
    """Generate heatmap for selected genes using centralized data loader."""
    ne = load_expression_matrix()
    if isinstance(genes, str):
        genes = [genes]

    selected_df = ne.loc[genes].T
    global_mean = ne.values.mean()
    z_scores = selected_df - global_mean
    zmin = z_scores.min().min()
    zmax = z_scores.max().max()

    n_genes = len(z_scores.columns)
    n_samples = len(z_scores.index)

    heatmap = go.Figure(
        data=go.Heatmap(
            z=z_scores.values,
            x=z_scores.columns,
            y=z_scores.index,
            zmin=zmin,
            zmax=zmax,
            colorscale=[[0, "red"], [0.5, "black"], [1, "green"]],
        )
    )
    heatmap.update_layout(
        # xaxis=dict(showticklabels=False),
        # yaxis=dict(showticklabels=False),
        xaxis_title="Genes",
        yaxis_title="Samples",
    )
    return dcc.Graph(
        figure=heatmap, className="flex-1", style={"height": "100%", "width": "100%"}
    )


def get_regulation(selected_nodes):
    rows = []
    partners = []
    grn_data = load_grn()
    bygene = grn_data.get("adjlist").get("bygene")
    bytf = grn_data.get("adjlist").get("bytf")

    for node in selected_nodes:
        if node in bytf:
            # TF perspective: list its targets
            acts = bytf.get(node, {}).get("act", []) or []
            reps = bytf.get(node, {}).get("rep", []) or []
            rows.extend(
                {
                    "Partner": tgt,
                    "Regulation": "Positive",
                    "Source": node,
                    "partner_label": "TF",
                }
                for tgt in acts
            )
            rows.extend(
                {
                    "Partner": tgt,
                    "Regulation": "Negative",
                    "Source": node,
                    "partner_label": "TF",
                }
                for tgt in reps
            )
            partners.extend(acts + reps)
        elif node in bygene:
            # Gene perspective: list its regulators (TFs)
            acts = bygene.get(node, {}).get("act", []) or []
            reps = bygene.get(node, {}).get("rep", []) or []
            rows.extend(
                {
                    "Partner": tf,
                    "Regulation": "Positive",
                    "Source": node,
                    "partner_label": "Target",
                }
                for tf in acts
            )
            rows.extend(
                {
                    "Partner": tf,
                    "Regulation": "Negative",
                    "Source": node,
                    "partner_label": "Target",
                }
                for tf in reps
            )
            partners.extend(acts + reps)
        else:
            # Unknown node id — ignore
            pass

    duplicates = list(set([x for x in partners if partners.count(x) > 1]))

    for d in rows:
        if d["Partner"] in duplicates:
            d["shared"] = "true"
        else:
            d["shared"] = "false"

    return rows
