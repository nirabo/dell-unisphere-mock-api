"""Version management module for Dell Unisphere Mock API."""

import importlib.metadata
import logging

logger = logging.getLogger(__name__)


def get_version() -> str:
    """
    Get the current version of the package from pyproject.toml.

    Returns:
        str: The current version string.
    """
    try:
        return importlib.metadata.version("dell-unisphere-mock-api")
    except importlib.metadata.PackageNotFoundError:
        logger.warning("Package metadata not found, falling back to default version")
        return "0.0.0"  # Fallback version for development
