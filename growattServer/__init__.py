"""Growatt Server API client library."""  # noqa: N999

# Import everything from base_api to ensure backward compatibility
from .base_api import *  # noqa: F403
from .exceptions import GrowattError, GrowattParameterError, GrowattV1ApiError
from .open_api_v1 import DeviceType, OpenApiV1

# Define the name of the package
name = "growattServer"

__all__ = [
    "DeviceType",
    "GrowattError",
    "GrowattParameterError",
    "GrowattV1ApiError",
    "OpenApiV1",
    "name",
]
