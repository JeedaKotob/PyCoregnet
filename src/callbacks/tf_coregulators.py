from dash import Input, Output, State, ctx, get_app, no_update,dcc,html
import dash_ag_grid as dag
from graph.adj import get_byregulation_data
from analysis.enrichment import Enrichment
import callbacks.enrichment  # noqa: F401

app = get_app()


@app.callback(
    Output({"type": "inspector_tabs_content", "uid": "coregs"}, "children"),
    Input({"type": "inspector_tabs", "uid": "coregs"}, "active_tab"),
    Input({"type": "store", "uid": "coregs"}, "data"),
    State({"type": "network-graph", "uid": "coregs"}, "elements"),
    prevent_initial_call=True,
)
def update_inspector_tabs(active_tab, store, ___):

    selected = store.get("selected", [])

    threshold = store["threshold"]

    # TODO UPDATE BASED ON THE FINAL PRODUCT
    # CACHE OR RELOAD?

    if active_tab == "table":
        if selected:
            from dash import get_app

            app = get_app()
            cache = app.server.config["SERVER_CACHE"]
            pre_data = cache.get(store["uid"])

            if not pre_data:
                raise NameError("Getting cache has failed")

            edges = [e.copy() for e in ___ if "source" in e["data"]]

            rowData = get_byregulation_data(pre_data, selected, edges, threshold)
        else:
            rowData = []

        return dag.AgGrid(
            rowData=rowData,
            columnSize="responsiveSizeToFit",
            dashGridOptions={
                "suppressHorizontalScroll": True,
            },
            style={"height": "100%"},
            defaultColDef={
                "resizable": True,
                "sortable": True,
                "filter": True,
                "minWidth": 120,
                "flex": 1,
            },
            columnDefs=[
                {
                    "field": "column1",
                    "headerName": "TF (C) ⓘ",
                    "headerTooltip": "Transcription Factor (Count)",
                },
                {
                    "field": "column2",
                    "headerName": "Coreg ⓘ",
                    "headerTooltip": "Coregulator",
                    "tooltipField": "partner_tooltip",
                    "cellStyle": {
                        "styleConditions": [
                            {
                                "condition": "params.data.is_common",
                                "style": {
                                    "color": "#0052CC",
                                    "fontWeight": "bold",
                                    "textAlign": "left",
                                },
                            }
                        ],
                    },
                },
                {
                    "field": "column3",
                    "headerName": "STC ⓘ",
                    "headerTooltip": "Shared Target Count",
                },
            ],
        )

    elif active_tab == "enrichment":
        # Avoid rebuilding GO UI when only the store updates (e.g., graph selection changes).
        if (
            isinstance(ctx.triggered_id, dict)
            and ctx.triggered_id.get("type") == "store"
        ):
            return no_update
        return Enrichment(uid=store["uid"]).unpack()
    
    elif active_tab == "hms" and False:
        print("adsasd")
        from analysis.hm import get_hm_fig
        from analysis.heatmaps import sm
        
        if len(selected) != 0:
            if len(selected) > 1:
                selected = selected[0]
            
            
            fig = sm.tf_plot(selected)
            
            return html.Div(
                children=dcc.Graph(
                    figure=fig,
                    style={"height": "100%"},
                    responsive=True,
                ),
                style={"height": "100%", "display": "flex", "flexDirection": "column"},
            )
            
    elif active_tab == 'hms':
        
        if len(selected) != 0:
            if len(selected) > 0:
                selected = selected[0]
        
            from analysis.heatmaps import SpecificMutation
            import plotly.graph_objects as go
            from services import (
                load_grn,
                load_expression_matrix,
                load_alterationData,
                load_clinicalData,
                load_influence,
            )

            GRN = load_grn()
            CIT_BLCA_EXP = load_expression_matrix()
            CIT_BLCA_Subgroup = load_clinicalData()
            CIT_BLCA_CNV = load_alterationData()
            CITinf = load_influence()

            CIT_BLCA_Subgroup.columns = [0]  # TODO update data

            sm = SpecificMutation(
                GRN=GRN,
                numerical_exp=CIT_BLCA_EXP,
                tf_activity=CITinf,
                alteration_data=CIT_BLCA_CNV,
                clinical_data=CIT_BLCA_Subgroup,
            )
            
            maps = sm.tf_plot(selected)
            if maps is None:
                return html.Div()
            
            fig = go.Figure()
            for hm in maps:
                fig.add_trace(hm)

            # Render all tracks as one visual body with shared pan/zoom interactions.
            fig.update_layout(
                dragmode="pan",
                margin=dict(t=0, b=0, l=0, r=0),
                yaxis=dict(
                    type="linear",
                    range=[-0.5, 2.5],
                    tickmode="array",
                    tickvals=[2, 1, 0],
                    ticktext=["Clinical", "Copy Number", "Influence"],
                ),
            )
            fig.update_xaxes(showgrid=False, zeroline=False)
            fig.update_yaxes(showgrid=False, zeroline=False)
                    
                    
            return html.Div(
                children=dcc.Graph(
                    figure=fig,
                    style={"height": "100%"},
                    responsive=True,
                ),
                style={"height": "100%", "display": "flex", "flexDirection": "column"},
            )
            
            