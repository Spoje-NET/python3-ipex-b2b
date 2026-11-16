"""Python client for the IPEX B2B REST API (restapi.ipex.cz)."""

from .client import ApiClient, Ipex
from .exceptions import IpexAuthError, IpexError
from .operations import BY_NAME, OPERATIONS, Operation

__version__ = "0.1.0"
__all__ = [
    "ApiClient",
    "Ipex",
    "IpexError",
    "IpexAuthError",
    "Operation",
    "OPERATIONS",
    "BY_NAME",
    "__version__",
]
