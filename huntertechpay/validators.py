"""
Input validation for HunterTechPay SDK

This module provides robust validation functions for all SDK inputs,
ensuring data integrity and providing clear error messages.
"""

from typing import Optional
from . import constants
from .exceptions import ValidationError


def validate_required(value: any, field_name: str) -> None:
    """
    Validate that a required field is provided.

    Args:
        value: The value to validate
        field_name: Name of the field for error messages

    Raises:
        ValidationError: If value is None or empty string
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(
            f"{field_name} is required",
            error_code="MISSING_REQUIRED_FIELD",
            data={"field": field_name}
        )


def validate_country_code(country: str) -> str:
    """
    Validate and normalize country code.

    Args:
        country: Country code (e.g., 'CM', 'cm')

    Returns:
        str: Normalized uppercase country code

    Raises:
        ValidationError: If country code is invalid
    """
    validate_required(country, "country")

    country = country.strip().upper()

    # ✅ Validation basique du format ISO 3166-1 alpha-2 (2 lettres majuscules)
    # La validation métier (pays supportés) est faite côté serveur qui vérifie dans la base de données
    if len(country) != 2 or not country.isalpha():
        raise ValidationError(
            f"Invalid country code format: {country}. "
            f"Country code must be 2 letters (ISO 3166-1 alpha-2)",
            error_code="INVALID_COUNTRY_FORMAT",
            data={"country": country}
        )

    return country


def validate_currency(currency: str, country: Optional[str] = None) -> str:
    """
    Validate and normalize currency code.

    Args:
        currency: Currency code (e.g., 'XAF', 'xaf')
        country: Optional country code (not used - validation done server-side)

    Returns:
        str: Normalized uppercase currency code

    Raises:
        ValidationError: If currency format is invalid
    """
    validate_required(currency, "currency")

    currency = currency.strip().upper()

    # ✅ Validation basique du format ISO 4217 (3 lettres majuscules)
    # La validation métier (devises supportées, correspondance pays-devise) est faite côté serveur
    if len(currency) != 3 or not currency.isalpha():
        raise ValidationError(
            f"Invalid currency format: {currency}. "
            f"Currency code must be 3 letters (ISO 4217)",
            error_code="INVALID_CURRENCY_FORMAT",
            data={"currency": currency}
        )

    return currency


def validate_amount(amount: float, field_name: str = "amount") -> int:
    """
    Validate and convert amount to cents.

    Args:
        amount: Amount in main units (e.g., 100.50 XAF)
        field_name: Name of the field for error messages

    Returns:
        int: Amount in cents (e.g., 10050)

    Raises:
        ValidationError: If amount is invalid
    """
    validate_required(amount, field_name)

    # Check type
    if not isinstance(amount, (int, float)):
        raise ValidationError(
            f"{field_name} must be a number, got {type(amount).__name__}",
            error_code="INVALID_TYPE",
            data={"field": field_name, "type": type(amount).__name__}
        )

    # Check positive
    if amount <= 0:
        raise ValidationError(
            f"{field_name} must be positive, got {amount}",
            error_code="INVALID_AMOUNT",
            data={"field": field_name, "value": amount}
        )

    # Convert to cents
    amount_cents = int(amount * 100)

    # Check limits
    if amount_cents < constants.MIN_AMOUNT_CENTS:
        min_amount = constants.MIN_AMOUNT_CENTS / 100
        raise ValidationError(
            f"{field_name} must be at least {min_amount}, got {amount}",
            error_code="AMOUNT_TOO_SMALL",
            data={
                "field": field_name,
                "value": amount,
                "minimum": min_amount
            }
        )

    if amount_cents > constants.MAX_AMOUNT_CENTS:
        max_amount = constants.MAX_AMOUNT_CENTS / 100
        raise ValidationError(
            f"{field_name} must be at most {max_amount}, got {amount}",
            error_code="AMOUNT_TOO_LARGE",
            data={
                "field": field_name,
                "value": amount,
                "maximum": max_amount
            }
        )

    return amount_cents


def validate_phone_number(phone: str) -> str:
    """
    Validate phone number format.

    Args:
        phone: Phone number (with or without + prefix)

    Returns:
        str: Normalized phone number

    Raises:
        ValidationError: If phone number format is invalid
    """
    validate_required(phone, "phone_number")

    phone = phone.strip()

    # Check format using regex
    if not constants.PHONE_PATTERN.match(phone):
        raise ValidationError(
            f"Invalid phone number format: {phone}. "
            f"Expected format: +237XXXXXXXXX or 237XXXXXXXXX",
            error_code="INVALID_PHONE_FORMAT",
            data={"phone": phone}
        )

    # Check length
    # Remove + if present for length check
    phone_digits = phone.lstrip('+')
    if len(phone_digits) < constants.PHONE_MIN_LENGTH or len(phone_digits) > constants.PHONE_MAX_LENGTH:
        raise ValidationError(
            f"Phone number length must be between {constants.PHONE_MIN_LENGTH} "
            f"and {constants.PHONE_MAX_LENGTH} digits, got {len(phone_digits)}",
            error_code="INVALID_PHONE_LENGTH",
            data={"phone": phone, "length": len(phone_digits)}
        )

    return phone


def validate_provider_code(provider: str) -> str:
    """
    Validate provider/service code format.

    Args:
        provider: Provider or service code (e.g., 'orange_cm', 'HT_PAIEMENTMARCHAND_MTN_CM')

    Returns:
        str: Service code as-is (preserves case for service codes)

    Raises:
        ValidationError: If provider code format is invalid
    """
    validate_required(provider, "provider")

    provider = provider.strip()
    # Don't convert to lowercase - preserve the original case
    # Service codes are case-sensitive (e.g., HT_PAIEMENTMARCHAND_MTN_CM)

    # Basic format validation (alphanumeric + underscore)
    if not provider.replace('_', '').replace('-', '').isalnum():
        raise ValidationError(
            f"Invalid provider code format: {provider}",
            error_code="INVALID_PROVIDER_FORMAT",
            data={"provider": provider}
        )

    return provider


def validate_reference(reference: Optional[str]) -> Optional[str]:
    """
    Validate transaction reference if provided.

    Args:
        reference: Optional transaction reference

    Returns:
        str | None: Normalized reference or None

    Raises:
        ValidationError: If reference format is invalid
    """
    if not reference:
        return None

    reference = reference.strip()

    # Check format
    if not constants.REFERENCE_PATTERN.match(reference):
        raise ValidationError(
            f"Invalid reference format: {reference}. "
            f"Reference must contain only alphanumeric characters, underscores, "
            f"and hyphens, and be 1-100 characters long",
            error_code="INVALID_REFERENCE_FORMAT",
            data={"reference": reference}
        )

    return reference


def validate_callback_url(url: Optional[str]) -> Optional[str]:
    """
    Validate callback URL if provided.

    Args:
        url: Optional callback URL

    Returns:
        str | None: Validated URL or None

    Raises:
        ValidationError: If URL format is invalid
    """
    if not url:
        return None

    url = url.strip()

    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        raise ValidationError(
            f"Callback URL must start with http:// or https://, got: {url}",
            error_code="INVALID_URL_FORMAT",
            data={"url": url}
        )

    # Check length
    if len(url) > 2048:
        raise ValidationError(
            f"Callback URL too long (max 2048 characters), got {len(url)}",
            error_code="URL_TOO_LONG",
            data={"url_length": len(url)}
        )

    return url


def validate_transaction_id(transaction_id: str) -> str:
    """
    Validate transaction ID format.

    Args:
        transaction_id: Transaction ID (UUID or reference)

    Returns:
        str: Validated transaction ID

    Raises:
        ValidationError: If transaction ID format is invalid
    """
    validate_required(transaction_id, "transaction_id")

    transaction_id = transaction_id.strip()

    # Accept UUIDs or custom references
    is_uuid = constants.UUID_PATTERN.match(transaction_id)
    is_reference = constants.REFERENCE_PATTERN.match(transaction_id)

    if not is_uuid and not is_reference:
        raise ValidationError(
            f"Invalid transaction ID format: {transaction_id}",
            error_code="INVALID_TRANSACTION_ID",
            data={"transaction_id": transaction_id}
        )

    return transaction_id


def validate_page_params(page: Optional[int] = None, page_size: Optional[int] = None) -> tuple:
    """
    Validate pagination parameters.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        tuple: (page, page_size) with defaults applied

    Raises:
        ValidationError: If pagination parameters are invalid
    """
    # Apply defaults
    if page is None:
        page = 1
    if page_size is None:
        page_size = constants.DEFAULT_PAGE_SIZE

    # Validate page
    if not isinstance(page, int) or page < 1:
        raise ValidationError(
            f"Page must be a positive integer, got {page}",
            error_code="INVALID_PAGE",
            data={"page": page}
        )

    # Validate page_size
    if not isinstance(page_size, int) or page_size < 1:
        raise ValidationError(
            f"Page size must be a positive integer, got {page_size}",
            error_code="INVALID_PAGE_SIZE",
            data={"page_size": page_size}
        )

    if page_size > constants.MAX_PAGE_SIZE:
        raise ValidationError(
            f"Page size must be at most {constants.MAX_PAGE_SIZE}, got {page_size}",
            error_code="PAGE_SIZE_TOO_LARGE",
            data={"page_size": page_size, "max": constants.MAX_PAGE_SIZE}
        )

    return page, page_size


def validate_status_filter(status: Optional[str]) -> Optional[str]:
    """
    Validate transaction status filter.

    Args:
        status: Optional status filter

    Returns:
        str | None: Normalized status or None

    Raises:
        ValidationError: If status is invalid
    """
    if not status:
        return None

    status = status.strip().lower()

    if status not in constants.TRANSACTION_STATUSES:
        raise ValidationError(
            f"Invalid status: {status}. "
            f"Valid statuses: {', '.join(sorted(constants.TRANSACTION_STATUSES))}",
            error_code="INVALID_STATUS",
            data={
                "status": status,
                "valid_statuses": list(constants.TRANSACTION_STATUSES)
            }
        )

    return status
