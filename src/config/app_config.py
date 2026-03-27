# Local-friendly cache (persists between runs). For Redis, swap config.
CACHE_CONFIG = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 3600,
}