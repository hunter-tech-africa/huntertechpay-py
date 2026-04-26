"""
Security utilities for HunterTechPay SDK

This module handles cryptographic operations including HMAC-SHA512 signature
generation for request authentication.
"""

import hmac
import hashlib
import json
import time
from typing import Dict, Any, Tuple


def generate_signature(
    secret_key: str,
    payload: Dict[str, Any] | str,
    timestamp: str
) -> str:
    """
    Generate HMAC-SHA512 signature for request authentication.

    The signature is computed over a message composed of:
    - Unix timestamp
    - JSON-serialized payload (sorted keys, no spaces)

    Format: HMAC-SHA512(secret_key, "{timestamp}.{json_payload}")

    Args:
        secret_key: API secret key
        payload: Request payload (dictionary or JSON string)
        timestamp: Unix timestamp as string

    Returns:
        str: Hex-encoded HMAC-SHA512 signature

    Example:
        >>> signature = generate_signature(
        ...     secret_key="sk_live_abc123",
        ...     payload={"amount": 5000, "currency": "XAF"},
        ...     timestamp="1710849600"
        ... )
        >>> print(signature)
        'a1b2c3d4...'
    """
    # Serialize payload if it's a dict
    if isinstance(payload, dict):
        json_payload = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    else:
        json_payload = payload

    # Construct message: timestamp.payload
    message = f"{timestamp}.{json_payload}"

    # Generate HMAC-SHA512 signature
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()

    return signature


def generate_timestamp() -> str:
    """
    Generate current Unix timestamp as string.

    Returns:
        str: Current Unix timestamp (seconds since epoch)

    Example:
        >>> timestamp = generate_timestamp()
        >>> print(timestamp)
        '1710849600'
    """
    return str(int(time.time()))


def prepare_signed_request(
    secret_key: str,
    payload: Dict[str, Any]
) -> Tuple[str, str, str]:
    """
    Prepare signed request with timestamp and signature.

    This is a convenience function that generates both timestamp and signature
    for a request payload.

    Args:
        secret_key: API secret key
        payload: Request payload dictionary

    Returns:
        tuple: (timestamp, signature, json_payload) as strings

    Example:
        >>> timestamp, signature, json_body = prepare_signed_request(
        ...     secret_key="sk_live_abc123",
        ...     payload={"amount": 5000}
        ... )
        >>> print(f"Timestamp: {timestamp}")
        >>> print(f"Signature: {signature[:20]}...")
    """
    timestamp = generate_timestamp()

    # Serialize payload with consistent formatting
    json_payload = json.dumps(payload, separators=(',', ':'), sort_keys=True)

    # Generate signature on the serialized JSON
    signature = generate_signature(secret_key, json_payload, timestamp)

    return timestamp, signature, json_payload


def verify_signature(
    secret_key: str,
    payload: Dict[str, Any],
    timestamp: str,
    provided_signature: str
) -> bool:
    """
    Verify HMAC signature for incoming webhook/callback.

    Args:
        secret_key: API secret key
        payload: Received payload dictionary
        timestamp: Received timestamp
        provided_signature: Signature from request headers

    Returns:
        bool: True if signature is valid, False otherwise

    Example:
        >>> is_valid = verify_signature(
        ...     secret_key="sk_live_abc123",
        ...     payload=webhook_data,
        ...     timestamp=request_headers['X-Timestamp'],
        ...     provided_signature=request_headers['X-Signature']
        ... )
        >>> if not is_valid:
        ...     raise SecurityError("Invalid signature")
    """
    expected_signature = generate_signature(secret_key, payload, timestamp)

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, provided_signature)


def is_timestamp_fresh(timestamp: str, max_age_seconds: int = 300) -> bool:
    """
    Check if timestamp is recent enough (within max_age_seconds).

    This helps prevent replay attacks by rejecting old signed requests.

    Args:
        timestamp: Unix timestamp as string
        max_age_seconds: Maximum age in seconds (default: 300 = 5 minutes)

    Returns:
        bool: True if timestamp is fresh, False if too old

    Example:
        >>> if not is_timestamp_fresh(webhook_timestamp):
        ...     raise SecurityError("Timestamp too old, possible replay attack")
    """
    try:
        request_time = int(timestamp)
        current_time = int(time.time())
        age = current_time - request_time

        # Check if timestamp is not from the future (with 60s tolerance for clock skew)
        if age < -60:
            return False

        # Check if timestamp is not too old
        if age > max_age_seconds:
            return False

        return True

    except (ValueError, TypeError):
        # Invalid timestamp format
        return False
