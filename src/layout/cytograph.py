"""
CytoGraph Layout Module

CytoGraph
    - Responsible for all data preprocess/process/cache for the graph
    - Add your params to the CytoGraph(...) class
    - The class obj will have all metadata aswell all data for the specific graph
"""

import dash
import dash_bootstrap_components as dbc
from typing import Literal
import dash_cytoscape as cyto
from services import load_grn
from config.ui_config import _CYTOGRAPH_STYLE, _CYTOGRAPH_CLASS_NAME

cyto.load_extra_layouts()


class CytoGraph:
    def __init__(
        self,
        preprocess_function: callable = None,
        preprocess_role: str = Literal["bygene", "bytf"],
        creation_function: callable = None,
        threshold_function: callable = None,
        threshold: float = None,
        threshold_ratio: float = None,
        stylesheet: dict = None,
        layout_config: dict = None,
        dropdown_options: callable = None,
    ):
        self.preprocess_function = preprocess_function
        self.preprocess_role = preprocess_role
        self.creation_function = creation_function
        self.threshold_function = threshold_function
        self.threshold = threshold
        self.threshold_ratio = threshold_ratio
        self.stylesheet = stylesheet
        self.layout_config = layout_config
        self.dropdown_options = dropdown_options
        self.computed = False  # Bool to check later
        self.store = {  # intial
            "selected": [],
            "metadata": {
                "total_nodes": 0,
                "total_edges": 0,
                "selected_nodes": 0,
                "selected_edges": 0,
            },
        }

    @property
    def _store(self):
        if not self.uid:
            raise KeyError("pack(uid) the class object")
        store = self.store
        store.update({"uid": self.uid})

        if self.threshold is not None:
            store.update(
                {
                    "threshold": self.threshold,
                    "threshold_ratio": self.threshold_ratio,
                    "preprocess_role": self.preprocess_role,
                }
            )

        return store

    def pack(self, uid):
        """Add info from UILayout class before unpack()"""
        self.uid = uid
        return self

    def compute(self):

        if self.preprocess_function:
            # NOTE we can cache this
            pre_data = self.preprocess_function(load_grn(), self.preprocess_role)

            # NOTE NOT STABLE
            app = dash.get_app()
            cache = app.server.config["SERVER_CACHE"]
            cache.set(self.uid, pre_data)

            if not self.threshold:
                self.threshold = self.threshold_function(pre_data, self.threshold_ratio)

            data = self.creation_function(pre_data, self.threshold)
        else:
            data = self.creation_function(load_grn())

        self.elements = data["nodes"] + data["edges"]

        self._store["metadata"]["total_nodes"] = len(data["nodes"])
        self._store["metadata"]["total_edges"] = len(data["edges"])

        if self.dropdown_options:
            self.options = self.dropdown_options(data["nodes"])  # TODO Remove hardcod

        self.computed = True

        return self

    def unpack(self):
        """Returns the entire layou"""
        if not self.computed:
            raise KeyError("compute() the class object")

        if self.uid is None:
            raise ValueError

        return [
            cyto.Cytoscape(
                id={"type": "network-graph", "uid": self.uid},
                style=_CYTOGRAPH_STYLE,
                minZoom=0.1,
                maxZoom=2,
                elements=self.elements,
                stylesheet=self.stylesheet,
                layout=self.layout_config,
                className=_CYTOGRAPH_CLASS_NAME,
            )
        ]
