"""
Constants for HunterTechPay SDK

This module contains all constant values used throughout the SDK,
including country codes, currencies, transaction types, and status values.
"""

from typing import Dict, List, Set

# SDK Version
SDK_VERSION = "1.0.1"  # Improved error handling - exposes complete API responses

# API Endpoints
DEFAULT_BASE_URL = "http://localhost:8007"
DEFAULT_TIMEOUT = 30  # seconds

# HTTP Headers
HEADER_API_KEY = "X-Api-Key"
HEADER_TIMESTAMP = "X-Hunter-Timestamp"
HEADER_SIGNATURE = "X-Hunter-Signature"
HEADER_REQUEST_ID = "X-Request-ID"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_USER_AGENT = "User-Agent"

# User Agent
USER_AGENT = f"HunterTechPay-Python-SDK/{SDK_VERSION}"

# Country Codes (ISO 3166-1 alpha-2)
COUNTRY_CM = "CM"  # Cameroun
COUNTRY_SN = "SN"  # Sénégal
COUNTRY_CI = "CI"  # Côte d'Ivoire
COUNTRY_BJ = "BJ"  # Bénin
COUNTRY_TG = "TG"  # Togo

SUPPORTED_COUNTRIES: Set[str] = {
    COUNTRY_CM,
    COUNTRY_SN,
    COUNTRY_CI,
    COUNTRY_BJ,
    COUNTRY_TG,
}

# Currency Codes (ISO 4217)
CURRENCY_XAF = "XAF"  # Franc CFA (CEMAC)
CURRENCY_XOF = "XOF"  # Franc CFA (UEMOA)

SUPPORTED_CURRENCIES: Set[str] = {
    CURRENCY_XAF,
    CURRENCY_XOF,
}

# Country to Currency Mapping
COUNTRY_CURRENCY_MAP: Dict[str, str] = {
    COUNTRY_CM: CURRENCY_XAF,  # Cameroun → XAF
    COUNTRY_SN: CURRENCY_XOF,  # Sénégal → XOF
    COUNTRY_CI: CURRENCY_XOF,  # Côte d'Ivoire → XOF
    COUNTRY_BJ: CURRENCY_XOF,  # Bénin → XOF
    COUNTRY_TG: CURRENCY_XOF,  # Togo → XOF
}

# Transaction Types
TRANSACTION_TYPE_COLLECTION = "collection"
TRANSACTION_TYPE_DISBURSEMENT = "disbursement"
TRANSACTION_TYPE_P2P = "p2p_transfer"
TRANSACTION_TYPE_PAYMENT_LINK = "payment_link"
TRANSACTION_TYPE_PRODUCT = "product_purchase"

TRANSACTION_TYPES: Set[str] = {
    TRANSACTION_TYPE_COLLECTION,
    TRANSACTION_TYPE_DISBURSEMENT,
    TRANSACTION_TYPE_P2P,
    TRANSACTION_TYPE_PAYMENT_LINK,
    TRANSACTION_TYPE_PRODUCT,
}

# Transaction Statuses
STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_SUCCESS = "success"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"
STATUS_EXPIRED = "expired"

TRANSACTION_STATUSES: Set[str] = {
    STATUS_PENDING,
    STATUS_PROCESSING,
    STATUS_SUCCESS,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_CANCELLED,
    STATUS_EXPIRED,
}

# Final transaction statuses (no further updates expected)
FINAL_STATUSES: Set[str] = {
    STATUS_SUCCESS,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_CANCELLED,
    STATUS_EXPIRED,
}

# Provider Codes
PROVIDER_ORANGE_CM = "orange_cm"
PROVIDER_MTN_CM = "mtn_cm"
PROVIDER_ORANGE_SN = "orange_sn"
PROVIDER_MTN_SN = "mtn_sn"
PROVIDER_WAVE_SN = "wave_sn"
PROVIDER_ORANGE_CI = "orange_ci"
PROVIDER_MTN_CI = "mtn_ci"
PROVIDER_WAVE_CI = "wave_ci"

# Service Code Suffixes
SERVICE_CODE_CASHIN = "CASHIN"
SERVICE_CODE_CASHOUT = "CASHOUT"

# Amount Limits (in cents)
MIN_AMOUNT_CENTS = 100  # 1.00 (minimum transaction amount)
MAX_AMOUNT_CENTS = 100_000_000  # 1,000,000.00 (maximum transaction amount)

# Phone Number
PHONE_MIN_LENGTH = 8
PHONE_MAX_LENGTH = 15

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# Retry Configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2  # Exponential backoff: 1s, 2s, 4s

# Timeout Configuration
CONNECT_TIMEOUT = 10  # seconds
READ_TIMEOUT = 30  # seconds

# Validation Patterns
import re

PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{7,14}$')
REFERENCE_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,100}$')
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)

# API Endpoints paths
ENDPOINT_PROVIDERS = "/api/v1/payments/providers"
ENDPOINT_DEPOSIT = "/api/v1/payments/deposit"
ENDPOINT_WITHDRAW = "/api/v1/payments/withdraw"
ENDPOINT_PAYMENT = "/api/v1/payments/initiate"
ENDPOINT_STATUS = "/api/v1/payments/status/{partner_id}"  # ✅ Changed to partner_id
ENDPOINT_TRANSACTIONS = "/api/v1/payments/transactions"
ENDPOINT_BALANCE = "/api/v1/payments/balance"
ENDPOINT_KYC = "/api/v1/payments/kyc"

# Error Codes
ERROR_CODE_AUTH_FAILED = "AUTH_FAILED"
ERROR_CODE_INVALID_SIGNATURE = "INVALID_SIGNATURE"
ERROR_CODE_INVALID_PARAMS = "INVALID_PARAMS"
ERROR_CODE_INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"
ERROR_CODE_FROZEN_ACCOUNT = "FROZEN_ACCOUNT"
ERROR_CODE_PROVIDER_ERROR = "PROVIDER_ERROR"
ERROR_CODE_PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
ERROR_CODE_DUPLICATE_REFERENCE = "DUPLICATE_REFERENCE"
ERROR_CODE_RATE_LIMIT = "RATE_LIMIT_EXCEEDED"
ERROR_CODE_SERVER_ERROR = "SERVER_ERROR"

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_PAYMENT_REQUIRED = 402
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_ERROR = 500
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503
HTTP_GATEWAY_TIMEOUT = 504

# Success HTTP Status Codes
SUCCESS_STATUS_CODES: Set[int] = {HTTP_OK, HTTP_CREATED}

# Retryable HTTP Status Codes
RETRYABLE_STATUS_CODES: Set[int] = {
    HTTP_TOO_MANY_REQUESTS,
    HTTP_INTERNAL_ERROR,
    HTTP_BAD_GATEWAY,
    HTTP_SERVICE_UNAVAILABLE,
    HTTP_GATEWAY_TIMEOUT,
}
