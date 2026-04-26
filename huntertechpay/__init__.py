"""
HunterTechPay Python SDK

Official Python client library for the HunterTechPay payment API.

Basic usage:
    >>> from huntertechpay import HunterTechPay
    >>> hunter = HunterTechPay(
    ...     api_key='htp_live_...',
    ...     secret_key='sk_live_...'
    ... )
    >>> providers = hunter.get_providers('CM')
    >>> for provider in providers.providers:
    ...     print(provider.name)

For more examples, see:
- README.md
- https://docs.huntertechpay.com
"""

from .client import HunterTechPay
from .exceptions import (
    HunterTechPayError,
    AuthenticationError,
    ValidationError,
    PaymentError,
    InsufficientBalanceError,
    FrozenAccountError,
    NotFoundError,
    RateLimitError,
    ServerError,
    NetworkError,
    TimeoutError,
    ConfigurationError,
)
from .models import (
    Provider,
    Transaction,
    Wallet,
    ProvidersResponse,
    TransactionResponse,
    TransactionListResponse,
    BalanceResponse,
    KYCVerification,
)
from . import constants

__version__ = constants.SDK_VERSION
__all__ = [
    # Main client
    "HunterTechPay",

    # Exceptions
    "HunterTechPayError",
    "AuthenticationError",
    "ValidationError",
    "PaymentError",
    "InsufficientBalanceError",
    "FrozenAccountError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    "TimeoutError",
    "ConfigurationError",

    # Models
    "Provider",
    "Transaction",
    "Wallet",
    "ProvidersResponse",
    "TransactionResponse",
    "TransactionListResponse",
    "BalanceResponse",
    "KYCVerification",

    # Metadata
    "__version__",
]
