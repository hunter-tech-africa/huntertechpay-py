# HunterTechPay SDK - Python

Official SDK for integrating HunterTechPay into your Python applications.

**Version**: 1.1.0
**Last Updated**: March 14, 2026

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Available Methods](#available-methods)
- [Complete Examples](#complete-examples)
- [Security](#security)
- [Error Handling](#error-handling)
- [Support](#support)

---

## Installation

```bash
pip install requests
```

Copy the `huntertechpay.py` file into your project.

---

## Quick Start

### Initialization

```python
from huntertechpay import HunterTechPay

hunter = HunterTechPay(
    api_key='htp_live_abc123...',      # API Key provided by HunterTechPay
    secret_key='sk_live_xyz789...',    # Secret Key (NEVER expose on client side!)
    base_url='https://api.huntertechpay.com'  # Production URL
)
```

---

## Available Methods

### 1. Get Available Providers

```python
providers = hunter.get_providers('CM')

print(providers)
# {
#   'success': True,
#   'country_code': 'CM',
#   'currency': 'XAF',
#   'providers': [
#     {
#       'provider_code': 'orange_money',
#       'name': 'Orange Money Cameroun',
#       'cashin_service_code': 'OM_CM_CASHIN',   # ✅ Code for deposit
#       'cashout_service_code': 'OM_CM_CASHOUT', # ✅ Code for withdrawal
#       'supports_cashin': True,
#       'supports_cashout': True,
#       'logo_url': 'https://...',
#       'is_active': True
#     }
#   ]
# }
```

---

### 2. Deposit (CASHIN) - Mobile Money → Wallet

Transfer money from a mobile money account to the HunterTechPay wallet.

```python
deposit = hunter.deposit(
    amount=5000,                    # Amount in XAF
    currency='XAF',                 # Currency (must match country)
    country='CM',                   # Country code (CM, SN, CI, etc.)
    phone='+237690000000',          # Customer phone number
    provider='orange_money',        # Selected provider
    reference=f'DEPOSIT_{int(time.time())}',  # Your unique reference
    description='Deposit to wallet',   # Description (optional)
    callback_url='https://mysite.com/webhook',  # Webhook (optional)
)

print('Deposit initiated:')
print(f"Transaction ID: {deposit['transaction_id']}")
print(f"Status: {deposit['status']}")  # 'pending', 'success', etc.
```

**Flow**:
1. User initiates a deposit
2. System automatically uses the CASHIN service code (e.g., `OM_CM_CASHIN`)
3. User receives a USSD push to confirm payment
4. Amount is debited from mobile money and credited to wallet

---

### 3. Withdraw (CASHOUT) - Wallet → Mobile Money

Transfer money from the HunterTechPay wallet to a mobile money account.

```python
withdrawal = hunter.withdraw(
    amount=3000,                       # Amount in XAF
    currency='XAF',                    # Currency (must match country)
    country='CM',                      # Country code
    phone='+237670000000',             # Recipient phone number
    provider='mtn_momo',               # Selected provider
    reference=f'WITHDRAW_{int(time.time())}',  # Your unique reference
    description='Withdrawal to mobile money',  # Description (optional)
    callback_url='https://mysite.com/webhook',  # Webhook (optional)
)

print('Withdrawal initiated:')
print(f"Transaction ID: {withdrawal['transaction_id']}")
print(f"Status: {withdrawal['status']}")
```

**Validation**:
- System checks available balance before authorizing withdrawal
- System verifies CASHOUT is enabled for merchant

---

### 4. Initiate Generic Payment

```python
payment = hunter.initiate_payment(
    amount=5000,
    currency='XAF',
    country='CM',
    phone='+237690000000',
    provider='orange_money',
    reference='ORDER_123',
    description='Purchase product XYZ',
    callback_url='https://mysite.com/webhook',
    return_url='https://mysite.com/success'
)

print(f"Payment initiated: {payment['transaction_id']}")
```

---

### 5. Check Transaction Status

```python
# By transaction_id
status = hunter.check_status('txn_abc123')

# By reference
status = hunter.check_status('ORDER_123', search_type='reference')

print(f"Status: {status['status']}")  # 'pending', 'success', 'failed'
print(f"Amount: {status['amount']}")
print(f"Currency: {status['currency']}")
```

---

### 6. List Transactions

```python
transactions = hunter.list_transactions(
    page=1,
    page_size=50,
    status='success',            # Filter by status (optional)
    start_date='2026-03-01',     # Start date (optional)
    end_date='2026-03-14'        # End date (optional)
)

print(f"Total transactions: {transactions['total']}")
for tx in transactions['transactions']:
    print(f"{tx['transaction_id']}: {tx['amount']} {tx['currency']}")
```

---

### 7. Get Balance

```python
balance = hunter.get_balance('merchant_123')

print(f"Available balance: {balance['available_balance']} {balance['currency']}")
print(f"Pending balance: {balance['pending_balance']} {balance['currency']}")
```

---

## Complete Examples

### Django Example

#### View (views.py)

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import os
import time
from huntertechpay import HunterTechPay, HunterTechPayError

# ⚠️ IMPORTANT: Initialize on server side with environment variables
hunter = HunterTechPay(
    api_key=os.environ['HUNTER_API_KEY'],
    secret_key=os.environ['HUNTER_SECRET_KEY'],
)

@require_http_methods(["GET"])
def get_providers(request):
    """Get available providers"""
    try:
        country = request.GET.get('country', 'CM')
        providers = hunter.get_providers(country)
        return JsonResponse(providers)
    except HunterTechPayError as e:
        return JsonResponse(
            {'error': str(e)},
            status=e.status_code
        )

@csrf_exempt
@require_http_methods(["POST"])
def initiate_deposit(request):
    """Initiate a deposit (CASHIN)"""
    import json
    try:
        data = json.loads(request.body)

        deposit = hunter.deposit(
            amount=data['amount'],
            currency='XAF',
            country='CM',
            phone=data['phone'],
            provider=data['provider'],
            reference=f"DEPOSIT_{int(time.time())}",
        )

        return JsonResponse(deposit, status=201)

    except HunterTechPayError as e:
        return JsonResponse(
            {'error': str(e)},
            status=e.status_code
        )
    except Exception as e:
        return JsonResponse(
            {'error': 'Internal server error'},
            status=500
        )

@csrf_exempt
@require_http_methods(["POST"])
def initiate_withdrawal(request):
    """Initiate a withdrawal (CASHOUT)"""
    import json
    try:
        data = json.loads(request.body)

        withdrawal = hunter.withdraw(
            amount=data['amount'],
            currency='XAF',
            country='CM',
            phone=data['phone'],
            provider=data['provider'],
            reference=f"WITHDRAW_{int(time.time())}",
        )

        return JsonResponse(withdrawal, status=201)

    except HunterTechPayError as e:
        # Specific error handling
        error_msg = str(e)

        if e.status_code == 400 and 'Insufficient balance' in error_msg:
            return JsonResponse(
                {'error': 'Insufficient balance', 'details': error_msg},
                status=400
            )
        elif e.status_code == 403 and 'frozen' in error_msg:
            return JsonResponse(
                {'error': 'Account frozen', 'details': error_msg},
                status=403
            )
        else:
            return JsonResponse(
                {'error': error_msg},
                status=e.status_code
            )
```

---

### Flask Example

```python
from flask import Flask, request, jsonify
import os
import time
from huntertechpay import HunterTechPay, HunterTechPayError

app = Flask(__name__)

# ⚠️ IMPORTANT: Use environment variables
hunter = HunterTechPay(
    api_key=os.environ['HUNTER_API_KEY'],
    secret_key=os.environ['HUNTER_SECRET_KEY'],
)

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Get available providers"""
    try:
        country = request.args.get('country', 'CM')
        providers = hunter.get_providers(country)
        return jsonify(providers)
    except HunterTechPayError as e:
        return jsonify({'error': str(e)}), e.status_code

@app.route('/api/deposit', methods=['POST'])
def initiate_deposit():
    """Initiate a deposit (CASHIN)"""
    try:
        data = request.get_json()

        deposit = hunter.deposit(
            amount=data['amount'],
            currency='XAF',
            country='CM',
            phone=data['phone'],
            provider=data['provider'],
            reference=f"DEPOSIT_{int(time.time())}",
        )

        return jsonify(deposit), 201

    except HunterTechPayError as e:
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/withdraw', methods=['POST'])
def initiate_withdrawal():
    """Initiate a withdrawal (CASHOUT)"""
    try:
        data = request.get_json()

        withdrawal = hunter.withdraw(
            amount=data['amount'],
            currency='XAF',
            country='CM',
            phone=data['phone'],
            provider=data['provider'],
            reference=f"WITHDRAW_{int(time.time())}",
        )

        return jsonify(withdrawal), 201

    except HunterTechPayError as e:
        # Specific error handling
        error_msg = str(e)

        if e.status_code == 400 and 'Insufficient balance' in error_msg:
            return jsonify({
                'error': 'Insufficient balance',
                'details': error_msg
            }), 400
        elif e.status_code == 403 and 'frozen' in error_msg:
            return jsonify({
                'error': 'Account frozen',
                'details': error_msg
            }), 403
        else:
            return jsonify({'error': error_msg}), e.status_code

if __name__ == '__main__':
    app.run(debug=True)
```

---

### FastAPI Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import time
from huntertechpay import HunterTechPay, HunterTechPayError

app = FastAPI()

# ⚠️ IMPORTANT: Use environment variables
hunter = HunterTechPay(
    api_key=os.environ['HUNTER_API_KEY'],
    secret_key=os.environ['HUNTER_SECRET_KEY'],
)

class DepositRequest(BaseModel):
    amount: float
    phone: str
    provider: str

class WithdrawRequest(BaseModel):
    amount: float
    phone: str
    provider: str

@app.get("/api/providers")
async def get_providers(country: str = 'CM'):
    """Get available providers"""
    try:
        providers = hunter.get_providers(country)
        return providers
    except HunterTechPayError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@app.post("/api/deposit")
async def initiate_deposit(request: DepositRequest):
    """Initiate a deposit (CASHIN)"""
    try:
        deposit = hunter.deposit(
            amount=request.amount,
            currency='XAF',
            country='CM',
            phone=request.phone,
            provider=request.provider,
            reference=f"DEPOSIT_{int(time.time())}",
        )
        return deposit
    except HunterTechPayError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@app.post("/api/withdraw")
async def initiate_withdrawal(request: WithdrawRequest):
    """Initiate a withdrawal (CASHOUT)"""
    try:
        withdrawal = hunter.withdraw(
            amount=request.amount,
            currency='XAF',
            country='CM',
            phone=request.phone,
            provider=request.provider,
            reference=f"WITHDRAW_{int(time.time())}",
        )
        return withdrawal
    except HunterTechPayError as e:
        # Specific error handling
        error_msg = str(e)

        if e.status_code == 400 and 'Insufficient balance' in error_msg:
            raise HTTPException(
                status_code=400,
                detail={'error': 'Insufficient balance', 'details': error_msg}
            )
        elif e.status_code == 403 and 'frozen' in error_msg:
            raise HTTPException(
                status_code=403,
                detail={'error': 'Account frozen', 'details': error_msg}
            )
        else:
            raise HTTPException(status_code=e.status_code, detail=error_msg)
```

---

## Security - VERY IMPORTANT

### ❌ NEVER DO THIS

```python
# ❌ DANGER: Secret key in source code
hunter = HunterTechPay(
    api_key='htp_live_...',
    secret_key='sk_live_...'  # ❌ EXPOSED in code!
)
```

### ✅ CORRECT APPROACH

#### Using .env file

**.env** (NEVER commit to Git):
```
HUNTER_API_KEY=htp_live_abc123...
HUNTER_SECRET_KEY=sk_live_xyz789...
```

**.gitignore**:
```
.env
*.pyc
__pycache__/
```

**Code**:
```python
import os
from dotenv import load_dotenv
from huntertechpay import HunterTechPay

# Load environment variables
load_dotenv()

# ✅ SECURE
hunter = HunterTechPay(
    api_key=os.environ['HUNTER_API_KEY'],
    secret_key=os.environ['HUNTER_SECRET_KEY'],
)
```

#### Django settings.py

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Environment variables
HUNTER_API_KEY = os.environ.get('HUNTER_API_KEY')
HUNTER_SECRET_KEY = os.environ.get('HUNTER_SECRET_KEY')
```

---

## Error Handling

The SDK provides comprehensive error handling with detailed API error information.

### Basic Error Handling

```python
from huntertechpay import HunterTechPay
from huntertechpay.exceptions import (
    HunterTechPayError,
    ValidationError,
    AuthenticationError,
    PaymentError,
    InsufficientBalanceError,
    NotFoundError,
    NetworkError,
    ServerError
)

hunter = HunterTechPay(
    api_key=os.environ['HUNTER_API_KEY'],
    secret_key=os.environ['HUNTER_SECRET_KEY'],
)

try:
    deposit = hunter.deposit(
        amount=5000,
        currency='XAF',
        country='CM',
        phone='+237690000000',
        service_code='OM_CM_CASHIN',
        partner_id='DEP_001'
    )

except HunterTechPayError as e:
    # Print complete error details
    print(f"Error: {e}")
    # Output: "Invalid phone number | Status: 400 | Code: VALIDATION_ERROR | Details: {"field": "phone"}"

    # Access error properties
    print(f"Status code: {e.status_code}")    # HTTP status code
    print(f"Message: {e.message}")            # Error message
    print(f"Error code: {e.error_code}")      # API error code
    print(f"Request ID: {e.request_id}")      # For support/debugging
    print(f"Data: {e.data}")                  # Full API response data
```

### Accessing Specific Error Details

```python
try:
    withdrawal = hunter.withdraw(
        amount=100000.00,
        currency='XAF',
        country='CM',
        phone='+237670000000',
        service_code='MTN_CM_CASHOUT'
    )

except InsufficientBalanceError as e:
    # Use get_detail() to access specific fields from API response
    available = e.get_detail('available_balance', 0)
    required = e.get_detail('required_balance', 0)
    currency = e.get_detail('currency', 'XAF')

    print(f"Insufficient balance!")
    print(f"Required: {required} {currency}")
    print(f"Available: {available} {currency}")
    print(f"Short by: {required - available} {currency}")
```

### Getting Complete Error Information

```python
try:
    result = hunter.check_status('INVALID_PARTNER_ID')

except NotFoundError as e:
    # Convert error to dictionary for logging
    error_info = e.to_dict()

    # error_info contains:
    # {
    #     'error_type': 'NotFoundError',
    #     'message': 'Transaction not found',
    #     'status_code': 404,
    #     'error_code': 'NOT_FOUND',
    #     'request_id': 'req_abc123',
    #     'data': {...}  # Full API response
    # }

    # Log to monitoring system
    logger.error("Transaction not found", extra=error_info)
```

### Handling Different Error Types

```python
try:
    deposit = hunter.deposit(...)

except ValidationError as e:
    # 400 - Invalid parameters
    print(f"Invalid request: {e.message}")
    print(f"Details: {e.data}")

except AuthenticationError as e:
    # 401 - Authentication failed
    print(f"Authentication failed: {e.message}")

except InsufficientBalanceError as e:
    # 402 - Insufficient balance (specific type of PaymentError)
    available = e.get_detail('available_balance', 0)
    print(f"Insufficient balance. Available: {available}")

except PaymentError as e:
    # 402 - Other payment errors
    print(f"Payment failed: {e.message}")

except NotFoundError as e:
    # 404 - Resource not found
    print(f"Not found: {e.message}")

except ServerError as e:
    # 500/502/503/504 - Server errors (retryable)
    print(f"Server error: {e.message}")
    print(f"Request ID: {e.request_id}")

except NetworkError as e:
    # Network/connection errors
    print(f"Network error: {e.message}")

except HunterTechPayError as e:
    # Catch all other errors
    print(f"Unexpected error: {e}")
```

### Complete Example with Retry Logic

```python
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        result = hunter.deposit(
            amount=5000.00,
            currency='XAF',
            country='CM',
            phone='+237690000000',
            service_code='OM_CM_CASHIN'
        )
        print(f"Success: {result.transaction_id}")
        break

    except (ServerError, NetworkError) as e:
        # Retry on server/network errors
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"Error: {e.message}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
        else:
            print(f"Failed after {max_retries} attempts")
            # Log full error details
            error_info = e.to_dict()
            logger.error("Deposit failed", extra=error_info)
            raise

    except ValidationError as e:
        # Don't retry validation errors
        print(f"Validation error: {e}")
        print(f"Fix parameters and try again")
        break
```

For complete error handling examples, see `error_handling_examples.py`.

---

## Currency/Country Validation

The SDK automatically validates that the currency matches the country:

| Country | Accepted Currency | Rejected Currency |
|---------|-------------------|-------------------|
| CM (Cameroon) | ✅ XAF | ❌ XOF |
| SN (Senegal) | ✅ XOF | ❌ XAF |

**Error Example**:
```python
# Attempt: XOF in Cameroon
deposit = hunter.deposit(
    currency='XOF',  # ❌ Error
    country='CM'
)

# Error returned:
# "Invalid currency for country CM. Expected XAF, got XOF"
```

---

## License

MIT

---

## Support

- **Complete Documentation**: `DOCUMENTATION_INDEX.md`
- **Email**: support@huntertechpay.com
- **GitHub**: https://github.com/hunter-tech-africa
