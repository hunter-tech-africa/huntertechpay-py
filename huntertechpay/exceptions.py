"""
Exceptions for HunterTechPay SDK

This module defines all custom exceptions used throughout the SDK.
Each exception provides detailed error information to help developers
debug and handle errors appropriately.
"""

from typing import Optional, Dict, Any


class HunterTechPayError(Exception):
    """
    Base exception for all HunterTechPay SDK errors.

    All other SDK exceptions inherit from this class, allowing you to catch
    all SDK-related errors with a single except clause.

    Attributes:
        message (str): Human-readable error message
        status_code (int): HTTP status code (if applicable)
        error_code (str): Machine-readable error code
        data (dict): Additional error context/data
        request_id (str): Request ID for tracing (if available)
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.data = data or {}
        self.request_id = request_id

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"error_code={self.error_code!r})"
        )


class AuthenticationError(HunterTechPayError):
    """
    Raised when authentication fails.

    This occurs when:
    - API key is invalid or expired
    - Secret key is incorrect
    - Signature validation fails
    - API key doesn't have required permissions

    Example:
        >>> try:
        ...     hunter.get_providers('CM')
        ... except AuthenticationError as e:
        ...     print(f"Authentication failed: {e.message}")
        ...     # Check your API credentials
    """

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=kwargs.pop('status_code', 401), **kwargs)


class ValidationError(HunterTechPayError):
    """
    Raised when request validation fails.

    This occurs when:
    - Required parameters are missing
    - Parameter values are invalid (wrong type, format, or range)
    - Currency doesn't match country
    - Phone number format is invalid

    Example:
        >>> try:
        ...     hunter.deposit(amount=-100, currency='XAF', ...)
        ... except ValidationError as e:
        ...     print(f"Invalid request: {e.message}")
        ...     print(f"Details: {e.data}")
    """

    def __init__(self, message: str = "Validation error", **kwargs):
        super().__init__(message, status_code=kwargs.pop('status_code', 400), **kwargs)


class PaymentError(HunterTechPayError):
    """
    Raised when a payment operation fails.

    This occurs when:
    - Payment is rejected by the provider
    - Transaction times out
    - Insufficient balance (for withdrawals)
    - Provider is temporarily unavailable

    Example:
        >>> try:
        ...     hunter.withdraw(amount=1000000, ...)
        ... except PaymentError as e:
        ...     if 'Insufficient balance' in e.message:
        ...         print("Not enough funds")
        ...     elif e.error_code == 'PROVIDER_TIMEOUT':
        ...         print("Payment timeout, please retry")
    """

    def __init__(self, message: str = "Payment failed", **kwargs):
        super().__init__(message, status_code=kwargs.pop('status_code', 402), **kwargs)


class InsufficientBalanceError(PaymentError):
    """
    Raised when account has insufficient balance for an operation.

    This is a specific subclass of PaymentError for balance-related failures.

    Example:
        >>> try:
        ...     hunter.withdraw(amount=1000000, ...)
        ... except InsufficientBalanceError as e:
        ...     available = e.data.get('available_balance', 0)
        ...     print(f"Insufficient balance. Available: {available}")
    """

    def __init__(self, message: str = "Insufficient balance", **kwargs):
        super().__init__(message, status_code=kwargs.pop('status_code', 402), **kwargs)


class FrozenAccountError(HunterTechPayError):
    """
    Raised when attempting operations on a frozen account.

    This occurs when:
    - Account/wallet has been frozen by admin
    - Compliance or security hold
    - Pending verification

    Example:
        >>> try:
        ...     hunter.withdraw(amount=5000, ...)
        ... except FrozenAccountError:
        ...     print("Account is frozen. Please contact support.")
    """

    def __init__(self, message: str = "Account is frozen", **kwargs):
        super().__init__(message, status_code=kwargs.pop('status_code', 403), **kwargs)


class NotFoundError(HunterTechPayError):
    """
    Raised when a requested resource is not found.

    This occurs when:
    - Transaction ID doesn't exist
    - Provider code is invalid
    - Merchant/user not found

    Example:
        >>> try:
        ...     hunter.check_status('invalid_transaction_id')
        ... except NotFoundError as e:
        ...     print(f"Resource not found: {e.message}")
    """

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=kwargs.pop('status_code', 404), **kwargs)


class RateLimitError(HunterTechPayError):
    """
    Raised when API rate limit is exceeded.

    This occurs when:
    - Too many requests in a short period
    - Rate limit for API key exceeded

    Attributes:
        retry_after (int): Seconds to wait before retrying

    Example:
        >>> try:
        ...     hunter.list_transactions()
        ... except RateLimitError as e:
        ...     print(f"Rate limit exceeded. Retry after {e.data.get('retry_after')}s")
        ...     time.sleep(e.data.get('retry_after', 60))
    """

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, status_code=kwargs.pop('status_code', 429), **kwargs)


class ServerError(HunterTechPayError):
    """
    Raised when server encounters an internal error.

    This occurs when:
    - Server error (5xx response)
    - Service temporarily unavailable
    - Unexpected server condition

    These errors should be retried with exponential backoff.

    Example:
        >>> import time
        >>> for attempt in range(3):
        ...     try:
        ...         result = hunter.deposit(...)
        ...         break
        ...     except ServerError:
        ...         if attempt < 2:
        ...             time.sleep(2 ** attempt)  # Exponential backoff
        ...         else:
        ...             raise
    """

    def __init__(self, message: str = "Server error", **kwargs):
        super().__init__(message, status_code=kwargs.pop('status_code', 500), **kwargs)


class NetworkError(HunterTechPayError):
    """
    Raised when a network-level error occurs.

    This occurs when:
    - Connection timeout
    - DNS resolution fails
    - Network unreachable
    - SSL/TLS errors

    Example:
        >>> try:
        ...     hunter.get_providers('CM')
        ... except NetworkError as e:
        ...     print(f"Network error: {e.message}")
        ...     # Check your internet connection
    """

    def __init__(self, message: str = "Network error", **kwargs):
        # Network errors don't have HTTP status codes
        kwargs.pop('status_code', None)
        super().__init__(message, status_code=0, **kwargs)


class TimeoutError(NetworkError):
    """
    Raised when a request times out.

    This is a specific subclass of NetworkError for timeout situations.

    Example:
        >>> try:
        ...     hunter = HunterTechPay(..., timeout=5)
        ...     hunter.deposit(...)
        ... except TimeoutError:
        ...     print("Request timed out. Try increasing timeout or retry later.")
    """

    def __init__(self, message: str = "Request timed out", **kwargs):
        super().__init__(message, **kwargs)


class ConfigurationError(HunterTechPayError):
    """
    Raised when SDK configuration is invalid.

    This occurs when:
    - Missing required configuration (API key, secret key)
    - Invalid base URL
    - Invalid timeout value

    This exception is raised at SDK initialization time.

    Example:
        >>> try:
        ...     hunter = HunterTechPay(api_key='', secret_key='')
        ... except ConfigurationError as e:
        ...     print(f"Configuration error: {e.message}")
    """

    def __init__(self, message: str = "Invalid SDK configuration", **kwargs):
        kwargs.pop('status_code', None)
        super().__init__(message, status_code=0, **kwargs)


# Mapping of HTTP status codes to exception classes
STATUS_CODE_TO_EXCEPTION = {
    400: ValidationError,
    401: AuthenticationError,
    402: PaymentError,
    403: FrozenAccountError,
    404: NotFoundError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: ServerError,
}


def exception_from_response(response, message: Optional[str] = None) -> HunterTechPayError:
    """
    Create appropriate exception from HTTP response.

    Args:
        response: HTTP response object
        message: Optional custom error message

    Returns:
        HunterTechPayError: Appropriate exception subclass based on status code
    """
    status_code = response.status_code

    # Try to parse error details from response
    try:
        data = response.json()
        if not message:
            message = data.get('detail') or data.get('message') or data.get('error', '')
        error_code = data.get('error_code')
        request_id = response.headers.get('X-Request-ID')
    except Exception:
        data = {}
        error_code = None
        request_id = None
        if not message:
            message = f"HTTP {status_code}: {response.reason}"

    # Convert message to string if it's a list
    if isinstance(message, list):
        message = '; '.join(str(m) for m in message)

    # Ensure message is a string
    message_str = str(message) if message else ""

    # Special cases based on message content
    if message_str and 'insufficient balance' in message_str.lower():
        return InsufficientBalanceError(message, status_code=status_code, data=data, request_id=request_id)

    if message_str and 'frozen' in message_str.lower():
        return FrozenAccountError(message, status_code=status_code, data=data, request_id=request_id)

    # Use status code mapping
    exception_class = STATUS_CODE_TO_EXCEPTION.get(status_code, HunterTechPayError)

    return exception_class(
        message=message,
        status_code=status_code,
        error_code=error_code,
        data=data,
        request_id=request_id
    )
