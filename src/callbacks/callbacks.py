"""
Main callback registry and callback map.

This module is the single import point used by layout modules to register
all generic graph callbacks by side effect.

Callback index:
- sync.py
  - sync
  - update_thresh
  - dropdown_selection_mode
  - highlightor
- controls.py
  - create_dropdown_options
  - update_graph_thresh
- stats.py
  - update_network_stats
- view.py
  - switch_view

Feature-specific callback modules remain separate and are imported by their
own pages:
- fullbipartite.py
- tf_coregulators.py
- target_coregulators.py
"""

import callbacks.sync  # noqa: F401
import callbacks.controls  # noqa: F401
import callbacks.stats  # noqa: F401
import callbacks.view  # noqa: F401
