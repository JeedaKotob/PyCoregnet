# Data loading is now centralized in services.data_loader
# Import from there instead of defining locally
from services import load_grn

# Legacy compatibility - grn is loaded on-demand
grn = None


def get_grn():
    """Get GRN data, loading on first call."""
    global grn
    if grn is None:
        grn = load_grn()
    return grn
