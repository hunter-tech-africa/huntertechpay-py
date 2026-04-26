"""
Data models for HunterTechPay SDK

This module defines Pydantic-like data classes for type-safe request/response handling.
Models provide validation, serialization, and convenient access to API data.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Provider:
    """
    Payment provider information.

    Attributes:
        provider_code: Unique provider code (e.g., 'orange_cm')
        name: Display name (e.g., 'Orange Money Cameroun')
        country_code: Country code (e.g., 'CM')
        currency: Currency code (e.g., 'XAF')
        supports_cashin: Whether provider supports deposits
        supports_cashout: Whether provider supports withdrawals
        cashin_service_code: Service code for deposits
        cashout_service_code: Service code for withdrawals
        logo_url: Provider logo URL
        is_active: Whether provider is currently active
    """
    provider_code: str
    name: str
    country_code: str
    currency: str
    supports_cashin: bool
    supports_cashout: bool
    cashin_service_code: Optional[str] = None
    cashout_service_code: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Provider':
        """Create Provider from API response dict."""
        return cls(
            provider_code=data.get('provider_code', ''),
            name=data.get('name', ''),
            country_code=data.get('country_code', ''),
            currency=data.get('currency', ''),
            supports_cashin=data.get('supports_cashin', False),
            supports_cashout=data.get('supports_cashout', False),
            cashin_service_code=data.get('cashin_service_code'),
            cashout_service_code=data.get('cashout_service_code'),
            logo_url=data.get('logo_url'),
            is_active=data.get('is_active', True)
        )


@dataclass
class Transaction:
    """
    Payment transaction information.

    Attributes:
        transaction_id: Unique transaction ID
        partner_id: Your merchant reference (same as reference for compatibility)
        reference: Your custom reference (deprecated, use partner_id)
        status: Transaction status ('pending', 'success', 'failed', etc.)
        transaction_type: Type of transaction
        amount: Amount in decimal format (e.g., 50.00)
        currency: Currency code
        provider: Provider code
        phone_number: Phone number (may be masked)
        description: Transaction description
        created_at: Creation timestamp
        updated_at: Last update timestamp
        completed_at: Completion timestamp
        fee_amount: Fee charged in decimal format
        net_amount: Net amount after fees in decimal format
        error_message: Error message if failed
        metadata: Additional transaction data
    """
    transaction_id: str
    status: str
    amount: float
    currency: str
    partner_id: Optional[str] = None
    reference: Optional[str] = None
    transaction_type: Optional[str] = None
    provider: Optional[str] = None
    phone_number: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    fee_amount: Optional[float] = None
    net_amount: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_pending(self) -> bool:
        """Check if transaction is still pending."""
        return self.status in ('pending', 'processing')

    @property
    def is_successful(self) -> bool:
        """Check if transaction completed successfully."""
        return self.status in ('success', 'completed')

    @property
    def is_failed(self) -> bool:
        """Check if transaction failed."""
        return self.status == 'failed'

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create Transaction from API response dict."""
        # API returns amounts as Decimal/float, use directly
        amount = float(data.get('amount', 0))
        fee_amount = float(data['fee_amount']) if data.get('fee_amount') is not None else None
        net_amount = float(data['net_amount']) if data.get('net_amount') is not None else None

        return cls(
            transaction_id=data.get('transaction_id', data.get('id', '')),
            partner_id=data.get('partner_id'),
            reference=data.get('reference'),
            status=data.get('status', 'unknown'),
            transaction_type=data.get('transaction_type'),
            amount=amount,
            currency=data.get('currency', ''),
            provider=data.get('provider'),
            phone_number=data.get('phone_number'),
            description=data.get('description'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            completed_at=data.get('completed_at'),
            fee_amount=fee_amount,
            net_amount=net_amount,
            error_message=data.get('error_message'),
            metadata=data.get('metadata', {})
        )


@dataclass
class Wallet:
    """
    Wallet information.

    Attributes:
        wallet_id: Unique wallet ID
        currency: Currency code
        balance: Total balance in cents
        available_balance: Available balance in cents
        pending_balance: Pending balance in cents
        is_active: Whether wallet is active
        is_frozen: Whether wallet is frozen
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    wallet_id: str
    currency: str
    balance: int
    available_balance: int
    pending_balance: int
    is_active: bool = True
    is_frozen: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def balance_decimal(self) -> float:
        """Get balance in decimal format."""
        return self.balance / 100

    @property
    def available_balance_decimal(self) -> float:
        """Get available balance in decimal format."""
        return self.available_balance / 100

    @property
    def pending_balance_decimal(self) -> float:
        """Get pending balance in decimal format."""
        return self.pending_balance / 100

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Wallet':
        """Create Wallet from API response dict."""
        return cls(
            wallet_id=data.get('id', ''),
            currency=data.get('currency', ''),
            balance=data.get('balance', 0),
            available_balance=data.get('available_balance', 0),
            pending_balance=data.get('pending_balance', 0),
            is_active=data.get('is_active', True),
            is_frozen=data.get('is_frozen', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


@dataclass
class ProvidersResponse:
    """
    Response from get_providers API call.

    Attributes:
        success: Whether request was successful
        country_code: Requested country code
        currency: Country currency
        providers: List of available providers
    """
    success: bool
    country_code: str
    currency: str
    providers: List[Provider]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProvidersResponse':
        """Create ProvidersResponse from API response dict."""
        providers_data = data.get('providers', [])
        providers = [Provider.from_dict(p) for p in providers_data]

        return cls(
            success=data.get('success', False),
            country_code=data.get('country_code', ''),
            currency=data.get('currency', ''),
            providers=providers
        )


@dataclass
class TransactionResponse:
    """
    Response from transaction API calls (deposit, withdraw, etc.).

    Attributes:
        success: Whether request was successful
        transaction_id: Created transaction ID
        partner_id: Your merchant reference
        reference: Your custom reference (deprecated, use partner_id)
        status: Initial transaction status
        message: Response message
        transaction: Full transaction object (if available)
    """
    success: bool
    transaction_id: str
    status: str
    partner_id: Optional[str] = None
    reference: Optional[str] = None
    message: Optional[str] = None
    transaction: Optional[Transaction] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionResponse':
        """Create TransactionResponse from API response dict."""
        transaction_data = data.get('transaction', data)
        transaction = Transaction.from_dict(transaction_data) if transaction_data else None

        return cls(
            success=data.get('success', False),
            transaction_id=data.get('transaction_id', ''),
            partner_id=data.get('partner_id'),
            reference=data.get('reference'),
            status=data.get('status', 'unknown'),
            message=data.get('message'),
            transaction=transaction
        )


@dataclass
class TransactionListResponse:
    """
    Response from list_transactions API call.

    Attributes:
        success: Whether request was successful
        transactions: List of transactions
        total: Total number of transactions
        page: Current page number
        page_size: Items per page
    """
    success: bool
    transactions: List[Transaction]
    total: int
    page: int
    page_size: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionListResponse':
        """Create TransactionListResponse from API response dict."""
        transactions_data = data.get('transactions', [])
        transactions = [Transaction.from_dict(t) for t in transactions_data]

        return cls(
            success=data.get('success', False),
            transactions=transactions,
            total=data.get('total', 0),
            page=data.get('page', 1),
            page_size=data.get('page_size', 50)
        )


@dataclass
class BalanceResponse:
    """
    Response from get_balance API call.

    Attributes:
        success: Whether request was successful
        wallets: List of wallets with balances
        total_wallets: Number of wallets
    """
    success: bool
    wallets: List[Wallet]
    total_wallets: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BalanceResponse':
        """Create BalanceResponse from API response dict."""
        wallets_data = data.get('wallets', [])
        wallets = [Wallet.from_dict(w) for w in wallets_data]

        return cls(
            success=data.get('success', False),
            wallets=wallets,
            total_wallets=data.get('total', len(wallets))
        )


@dataclass
class KYCVerification:
    """
    Response from KYC verification API call.

    Attributes:
        verification_id: Unique ID for this verification
        partner_id: Optional merchant reference
        status: Verification status (pending, verified, failed, error)
        phone_number: Phone number that was verified
        country_code: Country code
        provider_code: Provider code
        kyc_data: KYC data returned by provider (name, etc.)
        verified_at: Timestamp when verification completed
        success: Whether request was successful
        message: Response message
    """
    verification_id: str
    status: str
    phone_number: str
    country_code: str
    provider_code: str
    kyc_data: Optional[Dict[str, Any]] = None
    partner_id: Optional[str] = None
    verified_at: Optional[str] = None
    success: bool = True
    message: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KYCVerification':
        """Create KYCVerification from API response dict."""
        return cls(
            verification_id=data['verification_id'],
            partner_id=data.get('partner_id'),
            status=data['status'],
            phone_number=data['phone_number'],
            country_code=data['country_code'],
            provider_code=data['provider_code'],
            kyc_data=data.get('kyc_data'),
            verified_at=data.get('verified_at'),
            success=data.get('success', True),
            message=data.get('message', '')
        )
