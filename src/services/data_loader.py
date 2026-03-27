"""
Centralized data loading service with validation and caching support.
Handles GRN JSON, expression CSV, and other bioinformatics data formats.
"""

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from config.paths import GRN_FILE, NE_FILE

logger = logging.getLogger(__name__)


class DataLoadError(Exception):
    """Raised when data loading or validation fails."""

    pass


class DataValidator:
    """Validates data structure and content."""

    @staticmethod
    def validate_grn(data: Dict[str, Any]) -> None:
        """
        Validate GRN (Gene Regulatory Network) JSON structure.

        Args:
            data: Dictionary expected to contain network data

        Raises:
            DataLoadError: If required keys are missing or malformed
        """
        if not isinstance(data, dict):
            raise DataLoadError(f"GRN data must be a dict, got {type(data)}")

        # Customize these checks based on your actual GRN structure
        # Example: if it should have 'nodes' and 'edges':
        # if 'nodes' not in data or 'edges' not in data:
        #     raise DataLoadError("GRN must contain 'nodes' and 'edges' keys")

        logger.info(f"GRN validation passed. Keys: {list(data.keys())}")

    @staticmethod
    def validate_expression_matrix(df: pd.DataFrame) -> None:
        """
        Validate expression matrix structure.

        Args:
            df: Expression matrix (genes × samples, typically)

        Raises:
            DataLoadError: If structure is invalid
        """
        if df.empty:
            raise DataLoadError("Expression matrix is empty")

        if not pd.api.types.is_numeric_dtype(df.iloc[:, 0]):
            raise DataLoadError(
                "Expression matrix should contain numeric values. "
                f"Got dtype: {df.iloc[:, 0].dtype}"
            )

        logger.info(
            f"Expression matrix validated: {df.shape[0]} genes × {df.shape[1]} samples"
        )


class DataLoader:
    """
    Main data loading service.
    Handles file I/O, validation, and provides a clean API.
    """

    def __init__(self, cache_enabled: bool = True):
        """
        Initialize DataLoader.

        Args:
            cache_enabled: Whether to enable caching via LRU cache
        """
        self.cache_enabled = cache_enabled
        self.validator = DataValidator()
        if not cache_enabled:
            # Disable caching by wrapping methods differently
            self._load_grn_impl = self._load_grn_uncached
            self._load_expression_impl = self._load_expression_uncached
        else:
            self._load_grn_impl = self._load_grn_cached
            self._load_expression_impl = self._load_expression_cached

    @staticmethod
    @lru_cache(maxsize=2)
    def _load_grn_cached(file_path: str) -> Dict[str, Any]:
        """Cached implementation of GRN loading."""
        return DataLoader._load_grn_uncached(file_path)

    @staticmethod
    def _load_grn_uncached(file_path: str) -> Dict[str, Any]:
        """Uncached implementation of GRN loading."""
        path = Path(file_path)

        if not path.exists():
            raise DataLoadError(f"GRN file not found: {path}")

        try:
            with open(path, "r") as f:
                data = json.load(f)
            logger.info(f"Loaded GRN from {path}")
            return data
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON in {path}: {e}")
        except Exception as e:
            raise DataLoadError(f"Error loading GRN from {path}: {e}")

    @staticmethod
    @lru_cache(maxsize=2)
    def _load_expression_cached(file_path: str, index_col: int = 0) -> pd.DataFrame:
        """Cached implementation of expression loading."""
        return DataLoader._load_expression_uncached(file_path, index_col)

    @staticmethod
    def _load_expression_uncached(file_path: str, index_col: int = 0) -> pd.DataFrame:
        """Uncached implementation of expression loading."""
        path = Path(file_path)

        if not path.exists():
            raise DataLoadError(f"Expression file not found: {path}")

        try:
            df = pd.read_csv(path, index_col=index_col)
            logger.info(f"Loaded expression matrix from {path}: {df.shape}")
            return df
        except Exception as e:
            raise DataLoadError(f"Error loading expression from {path}: {e}")

    def load_grn(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load and validate GRN data.

        Args:
            file_path: Path to GRN JSON file. If None, uses default.

        Returns:
            Validated GRN dictionary

        Raises:
            DataLoadError: If file not found or invalid
        """
        path_str = str(file_path or GRN_FILE)

        try:
            data = self._load_grn_impl(path_str)
            self.validator.validate_grn(data)
            return data
        except DataLoadError:
            raise
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading GRN: {e}")

    def load_expression(
        self, file_path: Optional[str] = None, index_col: int = 0
    ) -> pd.DataFrame:
        """
        Load and validate expression matrix.

        Args:
            file_path: Path to expression CSV file. If None, uses default.
            index_col: Column index to use as row labels (default: 0, first column)

        Returns:
            Validated expression DataFrame

        Raises:
            DataLoadError: If file not found or invalid
        """
        path_str = str(file_path or NE_FILE)

        try:
            df = self._load_expression_impl(path_str, index_col)
            self.validator.validate_expression_matrix(df)
            return df
        except DataLoadError:
            raise
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading expression: {e}")

    def clear_cache(self) -> None:
        """Clear the LRU cache. Useful for reloading data after changes."""
        if self.cache_enabled:
            self._load_grn_cached.cache_clear()
            self._load_expression_cached.cache_clear()
            logger.info("Data cache cleared")


# Create a singleton instance for app-wide use
_loader = DataLoader(cache_enabled=False)  # NOTE Cache is off, TODO Update


def load_grn(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to load GRN using the default loader.

    Example:
        >>> grn_data = load_grn()
        >>> print(list(grn_data.keys()))

    Args:
        file_path: Optional path to override default

    Returns:
        GRN dictionary
    """
    return _loader.load_grn(file_path)


def load_expression_matrix(
    file_path: Optional[str] = None, index_col: int = 0
) -> pd.DataFrame:
    """
    Convenience function to load expression matrix using the default loader.

    Example:
        >>> expr = load_expression_matrix()
        >>> print(expr.shape)
        (20000, 500)

    Args:
        file_path: Optional path to override default
        index_col: Column to use as index

    Returns:
        Expression DataFrame
    """
    return _loader.load_expression(file_path, index_col)


def clear_data_cache() -> None:
    """Clear all cached data. Use this if you update data files at runtime."""
    _loader.clear_cache()


def get_loader() -> DataLoader:
    """Get the singleton DataLoader instance for direct use."""
    return _loader
