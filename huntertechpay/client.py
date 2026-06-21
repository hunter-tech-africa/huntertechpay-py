"""
HunterTechPay API Client

This is the main client class for interacting with the HunterTechPay API.
It provides methods for all API operations with proper error handling,
validation, and retry logic.
"""

import requests
import time
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin

from . import constants
from . import validators
from . import security
from . import models
from .exceptions import (
    HunterTechPayError,
    NetworkError,
    TimeoutError as SDKTimeoutError,
    ConfigurationError,
    exception_from_response
)

# Configure logging
logger = logging.getLogger(__name__)


class HunterTechPay:
    """
    HunterTechPay API Client

    This is the main entry point for the SDK. Initialize it with your API credentials
    and use its methods to interact with the HunterTechPay API.

    Args:
        api_key: Your API key (starts with htp_live_ or htp_test_)
        secret_key: Your secret key (starts with sk_live_ or sk_test_)
        base_url: Base API URL (default: http://localhost:8007)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts for failed requests (default: 3)

    Example:
        >>> from huntertechpay import HunterTechPay
        >>> hunter = HunterTechPay(
        ...     api_key='htp_live_abc123...',
        ...     secret_key='sk_live_xyz789...'
        ... )
        >>> providers = hunter.get_providers('CM')
    """

    def __init__(
        self,
        api_key: str,
        secret_key: str,
        base_url: str = constants.DEFAULT_BASE_URL,
        timeout: int = constants.DEFAULT_TIMEOUT,
        max_retries: int = constants.MAX_RETRY_ATTEMPTS
    ):
        # Validate configuration
        if not api_key or not isinstance(api_key, str):
            raise ConfigurationError("api_key is required and must be a string")

        if not secret_key or not isinstance(secret_key, str):
            raise ConfigurationError("secret_key is required and must be a string")

        if not base_url or not isinstance(base_url, str):
            raise ConfigurationError("base_url must be a non-empty string")

        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ConfigurationError("timeout must be a positive number")

        if not isinstance(max_retries, int) or max_retries < 0:
            raise ConfigurationError("max_retries must be a non-negative integer")

        self.api_key = api_key.strip()
        self.secret_key = secret_key.strip()
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries

        # Create session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            constants.HEADER_USER_AGENT: constants.USER_AGENT,
            constants.HEADER_CONTENT_TYPE: "application/json"
        })

        logger.info(f"HunterTechPay SDK initialized (version {constants.SDK_VERSION})")

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API with authentication and error handling.

        Args:
            method: HTTP method ('GET', 'POST', etc.)
            endpoint: API endpoint path
            data: Request body data
            params: URL query parameters
            retry_count: Current retry attempt number

        Returns:
            dict: Response JSON data

        Raises:
            HunterTechPayError: On API errors
            NetworkError: On network errors
            TimeoutError: On request timeout
        """
        url = urljoin(self.base_url, endpoint)
        # Prepare request payload and signature
        if method in ('POST', 'PUT', 'PATCH'):
            # For requests with body, sign the JSON payload
            payload = data or {}
            timestamp, signature, json_body = security.prepare_signed_request(self.secret_key, payload)
            request_body = json_body.encode('utf-8')
        else:
            # For GET/DELETE/OPTIONS, sign an empty body
            timestamp = security.generate_timestamp()
            signature = security.generate_signature(self.secret_key, "", timestamp)
            request_body = None

        headers = {
            constants.HEADER_API_KEY: self.api_key,
            constants.HEADER_TIMESTAMP: timestamp,
            constants.HEADER_SIGNATURE: signature
        }

        try:
            logger.debug(f"{method} {url} (attempt {retry_count + 1}/{self.max_retries + 1})")

            response = self.session.request(
                method=method,
                url=url,
                data=request_body,
                params=params,
                headers=headers,
                timeout=self.timeout
            )

            # Handle successful responses
            if response.status_code in constants.SUCCESS_STATUS_CODES:
                return response.json()

            # Handle error responses
            # Check if we should retry
            if (retry_count < self.max_retries and
                response.status_code in constants.RETRYABLE_STATUS_CODES):

                # Exponential backoff
                sleep_time = constants.RETRY_BACKOFF_FACTOR ** retry_count
                logger.warning(
                    f"Request failed with status {response.status_code}, "
                    f"retrying in {sleep_time}s..."
                )
                time.sleep(sleep_time)

                return self._request(method, endpoint, data, params, retry_count + 1)

            # Raise appropriate exception
            raise exception_from_response(response)

        except requests.exceptions.Timeout as e:
            if retry_count < self.max_retries:
                sleep_time = constants.RETRY_BACKOFF_FACTOR ** retry_count
                logger.warning(f"Request timeout, retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                return self._request(method, endpoint, data, params, retry_count + 1)

            raise SDKTimeoutError(
                f"Request timed out after {self.timeout}s",
                data={"url": url, "timeout": self.timeout}
            ) from e

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(
                f"Connection error: {str(e)}",
                data={"url": url}
            ) from e

        except requests.exceptions.RequestException as e:
            raise NetworkError(
                f"Network error: {str(e)}",
                data={"url": url}
            ) from e

    def get_providers(self, country: Optional[str] = None) -> models.ProvidersResponse:
        """
        Get list of available payment providers.

        Args:
            country: Optional country code (e.g., 'CM', 'SN').
                    If provided, returns providers for that country only.
                    If omitted, returns all providers from all configured countries.

        Returns:
            ProvidersResponse: Available providers information

        Raises:
            ValidationError: If country code format is invalid
            HunterTechPayError: On API errors

        Examples:
            >>> # Get all providers from all countries
            >>> all_providers = hunter.get_providers()
            >>>
            >>> # Get providers for Cameroon only
            >>> cm_providers = hunter.get_providers('CM')
            >>> for provider in cm_providers.providers:
            ...     print(f"{provider.name}: {provider.provider_code}")
        """
        endpoint = constants.ENDPOINT_PROVIDERS
        params = {}

        if country:
            country = validators.validate_country_code(country)
            params['country_code'] = country

        data = self._request('GET', endpoint, params=params)

        return models.ProvidersResponse.from_dict(data)

    def deposit(
        self,
        amount: float,
        currency: str,
        country: str,
        phone: str,
        service_code: str,
        partner_id: Optional[str] = None,
        description: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> models.TransactionResponse:
        """
        Initiate a deposit (CASHIN) - transfer from mobile money to wallet.

        Args:
            amount: Amount in main currency units (e.g., 5000.00 XAF)
            currency: Currency code (e.g., 'XAF')
            country: Country code (e.g., 'CM')
            phone: Phone number (e.g., '+237690000000')
            service_code: Service code (e.g., 'OM_CM_CASHIN', 'MTN_CM_CASHIN')
            partner_id: Your unique merchant reference
            description: Optional transaction description
            callback_url: Optional webhook URL for status updates

        Returns:
            TransactionResponse: Transaction information

        Raises:
            ValidationError: If parameters are invalid
            PaymentError: If payment fails
            HunterTechPayError: On other API errors

        Example:
            >>> result = hunter.deposit(
            ...     amount=5000.00,
            ...     currency='XAF',
            ...     country='CM',
            ...     phone='+237690000000',
            ...     service_code='OM_CM_CASHIN',
            ...     partner_id='ORDER-123'
            ... )
            >>> print(f"Transaction ID: {result.transaction_id}")
            >>> print(f"Status: {result.status}")
        """
        # Validate inputs (but don't convert to cents - API expects main units)
        validators.validate_amount(amount)  # Just validate, don't convert
        currency = validators.validate_currency(currency, country)
        country = validators.validate_country_code(country)
        phone = validators.validate_phone_number(phone)
        service_code = validators.validate_provider_code(service_code)  # Validates format
        partner_id = validators.validate_reference(partner_id)
        callback_url = validators.validate_callback_url(callback_url)

        # Prepare request - send amount in main currency units (API will convert to cents)
        payload = {
            "amount": amount,  # Send as main units, not cents
            "currency": currency,
            "country": country,
            "phone": phone,
            "service_code": service_code,
        }

        if partner_id:
            payload["partner_id"] = partner_id
        if description:
            payload["description"] = description
        if callback_url:
            payload["callback_url"] = callback_url

        data = self._request('POST', constants.ENDPOINT_DEPOSIT, data=payload)

        return models.TransactionResponse.from_dict(data)

    def withdraw(
        self,
        amount: float,
        currency: str,
        country: str,
        phone: str,
        service_code: str,
        partner_id: Optional[str] = None,
        description: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> models.TransactionResponse:
        """
        Initiate a withdrawal (CASHOUT) - transfer from wallet to mobile money.

        Args:
            amount: Amount in main currency units (e.g., 3000.00 XAF)
            currency: Currency code (e.g., 'XAF')
            country: Country code (e.g., 'CM')
            phone: Recipient phone number
            service_code: Service code (e.g., 'OM_CM_CASHOUT', 'MTN_CM_CASHOUT')
            partner_id: Your unique merchant reference
            description: Optional transaction description
            callback_url: Optional webhook URL for status updates

        Returns:
            TransactionResponse: Transaction information

        Raises:
            ValidationError: If parameters are invalid
            InsufficientBalanceError: If wallet balance is insufficient
            PaymentError: If payment fails
            HunterTechPayError: On other API errors

        Example:
            >>> result = hunter.withdraw(
            ...     amount=3000.00,
            ...     currency='XAF',
            ...     country='CM',
            ...     phone='+237670000000',
            ...     service_code='MTN_CM_CASHOUT',
            ...     partner_id='WITHDRAW-123'
            ... )
            >>> print(f"Transaction ID: {result.transaction_id}")
        """
        # Validate inputs (but don't convert to cents - API expects main units)
        validators.validate_amount(amount)  # Just validate, don't convert
        currency = validators.validate_currency(currency, country)
        country = validators.validate_country_code(country)
        phone = validators.validate_phone_number(phone)
        service_code = validators.validate_provider_code(service_code)  # Validates format
        partner_id = validators.validate_reference(partner_id)
        callback_url = validators.validate_callback_url(callback_url)

        # Prepare request - send amount in main currency units (API will convert to cents)
        payload = {
            "amount": amount,  # Send as main units, not cents
            "currency": currency,
            "country": country,
            "phone": phone,
            "service_code": service_code,
        }

        if partner_id:
            payload["partner_id"] = partner_id
        if description:
            payload["description"] = description
        if callback_url:
            payload["callback_url"] = callback_url

        data = self._request('POST', constants.ENDPOINT_WITHDRAW, data=payload)

        return models.TransactionResponse.from_dict(data)

    def initiate_payment(
        self,
        amount: float,
        currency: str,
        country: str,
        phone: str,
        provider: str,
        reference: Optional[str] = None,
        description: Optional[str] = None,
        callback_url: Optional[str] = None,
        return_url: Optional[str] = None
    ) -> models.TransactionResponse:
        """
        Initiate a generic payment.

        This is similar to deposit() but with additional options.

        Args:
            amount: Amount in main currency units
            currency: Currency code
            country: Country code
            phone: Phone number
            provider: Provider code
            reference: Optional custom reference
            description: Optional description
            callback_url: Optional webhook URL
            return_url: Optional redirect URL after payment

        Returns:
            TransactionResponse: Transaction information

        Example:
            >>> result = hunter.initiate_payment(
            ...     amount=10000.00,
            ...     currency='XAF',
            ...     country='CM',
            ...     phone='+237690000000',
            ...     provider='orange_cm',
            ...     reference='INV-456'
            ... )
        """
        # Use deposit endpoint for now
        return self.deposit(
            amount=amount,
            currency=currency,
            country=country,
            phone=phone,
            provider=provider,
            reference=reference,
            description=description,
            callback_url=callback_url
        )

    def check_status(
        self,
        partner_id: str
    ) -> models.Transaction:
        """
        Check status of a transaction using your partner_id (merchant reference).

        Args:
            partner_id: Your partner_id/reference for the transaction

        Returns:
            Transaction: Transaction information with current status

        Raises:
            ValidationError: If partner_id is invalid
            NotFoundError: If transaction not found
            HunterTechPayError: On other API errors

        Example:
            >>> tx = hunter.check_status('ORDER-123')
            >>> print(f"Status: {tx.status}")
            >>> print(f"Amount: {tx.amount} {tx.currency}")
        """
        if not partner_id or not isinstance(partner_id, str):
            raise validators.ValidationError("partner_id must be a non-empty string")

        endpoint = constants.ENDPOINT_STATUS.format(partner_id=partner_id)

        data = self._request('GET', endpoint)

        return models.Transaction.from_dict(data)

    def kyc(
        self,
        phone_number: str,
        country: str,
        service_code: str,
        partner_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> models.KYCVerification:
        """
        Verify KYC (Know Your Customer) information for a phone number.

        This method allows you to verify the identity of a phone number through
        the mobile money provider.

        Args:
            phone_number: Phone number to verify (e.g., '+237690000000' or '690000000')
            country: Country code (e.g., 'CM', 'SN', 'CI')
            service_code: Service code (e.g., 'HT_PAIEMENTMARCHAND_ORANGE_CM', 'HT_PAIEMENTMARCHAND_MTN_CM')
            partner_id: Optional unique reference for this verification
            metadata: Optional custom metadata dictionary

        Returns:
            KYCVerification: KYC verification result with customer information

        Raises:
            ValidationError: If parameters are invalid
            HunterTechPayError: On API errors

        Example:
            >>> kyc_result = hunter.kyc(
            ...     phone_number='+237690000000',
            ...     country='CM',
            ...     service_code='HT_PAIEMENTMARCHAND_ORANGE_CM',
            ...     partner_id='KYC-123'
            ... )
            >>> print(f"Status: {kyc_result.status}")
            >>> if kyc_result.kyc_data:
            ...     print(f"Name: {kyc_result.kyc_data.get('name')}")
        """
        if not phone_number or not isinstance(phone_number, str):
            raise validators.ValidationError("phone_number must be a non-empty string")

        if not country or not isinstance(country, str):
            raise validators.ValidationError("country must be a non-empty string")

        if not service_code or not isinstance(service_code, str):
            raise validators.ValidationError("service_code must be a non-empty string")

        payload = {
            'phone_number': phone_number,
            'country': country.upper(),
            'service_code': service_code
        }

        if partner_id:
            payload['partner_id'] = partner_id

        if metadata:
            payload['metadata'] = metadata
        
        data = self._request('POST', constants.ENDPOINT_KYC, data=payload)

        return models.KYCVerification.from_dict(data)

    def list_transactions(
        self,
        page: int = 1,
        page_size: int = constants.DEFAULT_PAGE_SIZE,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> models.TransactionListResponse:
        """
        List transactions with optional filters.

        Args:
            page: Page number (1-indexed)
            page_size: Items per page (max 100)
            status: Filter by status ('pending', 'success', 'failed', etc.)
            start_date: Filter by start date (ISO format: 'YYYY-MM-DD')
            end_date: Filter by end date (ISO format: 'YYYY-MM-DD')

        Returns:
            TransactionListResponse: Paginated list of transactions

        Example:
            >>> # List all transactions
            >>> result = hunter.list_transactions()
            >>> print(f"Total: {result.total}")
            >>> for tx in result.transactions:
            ...     print(f"{tx.transaction_id}: {tx.amount} {tx.currency}")
            >>>
            >>> # Filter by status
            >>> result = hunter.list_transactions(status='success', page_size=10)
        """
        page, page_size = validators.validate_page_params(page, page_size)
        status = validators.validate_status_filter(status)

        params = {
            'page': page,
            'page_size': page_size
        }

        if status:
            params['status'] = status
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        data = self._request('GET', constants.ENDPOINT_TRANSACTIONS, params=params)

        return models.TransactionListResponse.from_dict(data)

    def get_balance(self) -> models.BalanceResponse:
        """
        Get wallet balances for all currencies.

        Returns:
            BalanceResponse: List of wallets with balances

        Example:
            >>> result = hunter.get_balance()
            >>> for wallet in result.wallets:
            ...     print(f"{wallet.currency}: {wallet.available_balance_decimal}")
        """
        data = self._request('GET', constants.ENDPOINT_BALANCE)

        return models.BalanceResponse.from_dict(data)

    def close(self):
        """
        Close the HTTP session.

        Call this when you're done using the client to clean up resources.

        Example:
            >>> hunter = HunterTechPay(...)
            >>> try:
            ...     # Use the client
            ...     providers = hunter.get_providers('CM')
            ... finally:
            ...     hunter.close()
        """
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        return f"HunterTechPay(base_url='{self.base_url}')"

    # ===================================================================
    # Webhook Methods
    # ===================================================================

    def verify_webhook_signature(
        self,
        payload: Dict[str, Any] | str,
        timestamp: str,
        provided_signature: str,
        max_age_seconds: int = 300
    ) -> bool:
        """
        Verify webhook signature from HunterTechPay.

        This method verifies that a webhook request is authentic by checking:
        1. The HMAC-SHA512 signature matches
        2. The timestamp is recent (to prevent replay attacks)

        Args:
            payload: Webhook payload (dict or JSON string)
            timestamp: X-Hunter-Timestamp header value
            provided_signature: X-Hunter-Signature header value
            max_age_seconds: Maximum age for timestamp (default: 300 seconds)

        Returns:
            bool: True if signature is valid and timestamp is fresh

        Example:
            >>> from flask import request
            >>> @app.route('/webhooks/payment', methods=['POST'])
            ... def handle_webhook():
            ...     payload = request.get_json()
            ...     timestamp = request.headers.get('X-Hunter-Timestamp')
            ...     signature = request.headers.get('X-Hunter-Signature')
            ...
            ...     if not hunter.verify_webhook_signature(payload, timestamp, signature):
            ...         return 'Invalid signature', 401
            ...
            ...     # Process webhook
            ...     if payload['status'] == 'success':
            ...         fulfill_order(payload['partner_id'])
            ...
            ...     return 'OK', 200
        """
        # Check timestamp freshness first (prevent replay attacks)
        if not security.is_timestamp_fresh(timestamp, max_age_seconds):
            logger.warning(f"Webhook timestamp too old or invalid: {timestamp}")
            return False

        # Verify signature
        is_valid = security.verify_signature(
            self.secret_key,
            payload,
            timestamp,
            provided_signature
        )

        if not is_valid:
            logger.warning("Webhook signature verification failed")

        return is_valid

    def parse_webhook_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse webhook payload into structured event data.

        Args:
            payload: Webhook payload dictionary

        Returns:
            dict: Parsed webhook event with standardized fields

        Example:
            >>> event = hunter.parse_webhook_event(request.get_json())
            >>> print(f"Event: {event['event_type']}")
            >>> print(f"Status: {event['status']}")
            >>> print(f"Transaction ID: {event['transaction_id']}")
        """
        # Validate required fields
        required_fields = ['event_type', 'transaction_id', 'status']
        for field in required_fields:
            if field not in payload:
                raise ValueError(f"Missing required field in webhook: {field}")

        return payload
