"""
HunterTechPay SDK - Error Handling Examples

This file demonstrates how to properly handle errors from the HunterTechPay API.
With the improved error handling, you can now access all API error details.
"""

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


def example_basic_error_handling():
    """Example 1: Basic error handling with detailed error messages"""
    hunter = HunterTechPay(
        api_key='htp_test_your_key',
        secret_key='sk_test_your_secret'
    )

    try:
        result = hunter.deposit(
            amount=5000.00,
            currency='XAF',
            country='CM',
            phone='+237690000000',
            service_code='OM_CM_CASHIN'
        )
        print(f"Success: {result.transaction_id}")

    except HunterTechPayError as e:
        # The error message now includes all API details
        print(f"Error occurred: {e}")
        # Output example:
        # "Invalid phone number format | Status: 400 | Code: VALIDATION_ERROR | Details: {"field": "phone", "expected": "E.164 format"}"


def example_accessing_error_details():
    """Example 2: Accessing specific error details from API"""
    hunter = HunterTechPay(
        api_key='htp_test_your_key',
        secret_key='sk_test_your_secret'
    )

    try:
        result = hunter.withdraw(
            amount=100000.00,
            currency='XAF',
            country='CM',
            phone='+237670000000',
            service_code='MTN_CM_CASHOUT'
        )

    except InsufficientBalanceError as e:
        # Access specific error details using get_detail()
        available = e.get_detail('available_balance', 0)
        required = e.get_detail('required_balance', 0)
        currency = e.get_detail('currency', 'XAF')

        print(f"Insufficient balance!")
        print(f"Required: {required} {currency}")
        print(f"Available: {available} {currency}")
        print(f"Short by: {required - available} {currency}")


def example_full_error_info():
    """Example 3: Getting complete error information as dictionary"""
    hunter = HunterTechPay(
        api_key='htp_test_your_key',
        secret_key='sk_test_your_secret'
    )

    try:
        result = hunter.check_status('INVALID_PARTNER_ID')

    except NotFoundError as e:
        # Convert error to dictionary for logging or debugging
        error_info = e.to_dict()

        print("Complete error information:")
        print(f"  Error Type: {error_info['error_type']}")
        print(f"  Message: {error_info['message']}")
        print(f"  Status Code: {error_info['status_code']}")
        print(f"  Error Code: {error_info['error_code']}")
        print(f"  Request ID: {error_info['request_id']}")
        print(f"  Full API Data: {error_info['data']}")

        # You can log this to your monitoring system
        # logger.error("Transaction not found", extra=error_info)


def example_specific_error_types():
    """Example 4: Handling different error types differently"""
    hunter = HunterTechPay(
        api_key='htp_test_your_key',
        secret_key='sk_test_your_secret'
    )

    try:
        result = hunter.deposit(
            amount=5000.00,
            currency='XAF',
            country='CM',
            phone='+237690000000',
            service_code='OM_CM_CASHIN'
        )

    except ValidationError as e:
        # Handle validation errors (400)
        print(f"Invalid request parameters: {e.message}")
        print(f"Details: {e.data}")
        # Fix the parameters and retry

    except AuthenticationError as e:
        # Handle authentication errors (401)
        print(f"Authentication failed: {e.message}")
        print("Please check your API credentials")
        # Don't retry, credentials need to be fixed

    except InsufficientBalanceError as e:
        # Handle insufficient balance (402)
        available = e.get_detail('available_balance', 0)
        print(f"Insufficient balance. Available: {available}")
        # Notify user to top up their account

    except PaymentError as e:
        # Handle other payment errors (402)
        print(f"Payment failed: {e.message}")
        error_code = e.error_code
        if error_code == 'PROVIDER_TIMEOUT':
            print("Provider timeout, please retry")
            # Retry logic here
        elif error_code == 'PROVIDER_REJECTED':
            print("Payment rejected by provider")
            # Don't retry

    except NotFoundError as e:
        # Handle not found errors (404)
        print(f"Resource not found: {e.message}")

    except ServerError as e:
        # Handle server errors (500, 502, 503, 504)
        print(f"Server error occurred: {e.message}")
        print(f"Request ID for support: {e.request_id}")
        # Retry with exponential backoff

    except NetworkError as e:
        # Handle network errors
        print(f"Network error: {e.message}")
        # Check internet connection and retry

    except HunterTechPayError as e:
        # Catch all other SDK errors
        print(f"Unexpected error: {e}")
        error_dict = e.to_dict()
        # Log for investigation


def example_error_with_retry():
    """Example 5: Retry logic with detailed error information"""
    import time

    hunter = HunterTechPay(
        api_key='htp_test_your_key',
        secret_key='sk_test_your_secret'
    )

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
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Error on attempt {attempt + 1}: {e.message}")
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts")
                print(f"Last error: {e}")
                # Get full error details for logging
                error_info = e.to_dict()
                print(f"Full error details: {error_info}")
                raise

        except ValidationError as e:
            # Don't retry validation errors
            print(f"Validation error (won't retry): {e}")
            print(f"Error details: {e.data}")
            break


def example_accessing_raw_api_response():
    """Example 6: Accessing raw API response data"""
    hunter = HunterTechPay(
        api_key='htp_test_your_key',
        secret_key='sk_test_your_secret'
    )

    try:
        result = hunter.kyc(
            phone_number='+237690000000',
            country='CM',
            service_code='HT_PAIEMENTMARCHAND_ORANGE_CM'
        )

    except HunterTechPayError as e:
        # The 'data' attribute contains the full API response
        api_response = e.data

        print("Raw API response:")
        for key, value in api_response.items():
            print(f"  {key}: {value}")

        # Access specific fields from API response
        if 'validation_errors' in api_response:
            print("\nValidation errors from API:")
            for error in api_response['validation_errors']:
                print(f"  - {error}")


if __name__ == '__main__':
    print("HunterTechPay Error Handling Examples")
    print("=" * 50)
    print()

    print("Note: These examples will fail without valid API credentials")
    print("They are meant to demonstrate error handling patterns")
    print()

    # Uncomment to run specific examples:
    # example_basic_error_handling()
    # example_accessing_error_details()
    # example_full_error_info()
    # example_specific_error_types()
    # example_error_with_retry()
    # example_accessing_raw_api_response()
