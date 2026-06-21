"""
Test script for improved error handling in HunterTechPay SDK

This script tests the new error handling features to ensure they work correctly.
"""

import sys
from huntertechpay.exceptions import (
    HunterTechPayError,
    ValidationError,
    AuthenticationError,
    PaymentError,
    InsufficientBalanceError,
    NotFoundError,
    ServerError
)


def test_basic_exception():
    """Test basic exception creation and string representation"""
    print("Test 1: Basic exception creation")
    print("-" * 50)

    exc = ValidationError(
        message="Invalid phone number format",
        status_code=400,
        error_code="VALIDATION_ERROR",
        data={
            'field': 'phone',
            'expected': 'E.164 format',
            'received': '690000000'
        },
        request_id='req_abc123'
    )

    print(f"Exception string: {exc}")
    print(f"Message: {exc.message}")
    print(f"Status code: {exc.status_code}")
    print(f"Error code: {exc.error_code}")
    print(f"Request ID: {exc.request_id}")
    print(f"Data: {exc.data}")
    print()


def test_to_dict():
    """Test to_dict() method"""
    print("Test 2: to_dict() method")
    print("-" * 50)

    exc = InsufficientBalanceError(
        message="Insufficient balance for withdrawal",
        status_code=402,
        error_code="INSUFFICIENT_BALANCE",
        data={
            'available_balance': 5000,
            'required_balance': 10000,
            'currency': 'XAF'
        },
        request_id='req_xyz789'
    )

    error_dict = exc.to_dict()
    print("Error dictionary:")
    for key, value in error_dict.items():
        print(f"  {key}: {value}")
    print()


def test_get_detail():
    """Test get_detail() method"""
    print("Test 3: get_detail() method")
    print("-" * 50)

    exc = InsufficientBalanceError(
        message="Insufficient balance",
        data={
            'available_balance': 5000,
            'required_balance': 10000,
            'currency': 'XAF',
            'wallet_id': 'wallet_123'
        }
    )

    available = exc.get_detail('available_balance', 0)
    required = exc.get_detail('required_balance', 0)
    currency = exc.get_detail('currency', 'XAF')
    non_existent = exc.get_detail('non_existent_field', 'default_value')

    print(f"Available balance: {available} {currency}")
    print(f"Required balance: {required} {currency}")
    print(f"Short by: {required - available} {currency}")
    print(f"Non-existent field (with default): {non_existent}")
    print()


def test_string_representation_with_details():
    """Test that __str__() includes additional details"""
    print("Test 4: String representation with details")
    print("-" * 50)

    exc = PaymentError(
        message="Payment rejected by provider",
        status_code=402,
        error_code="PROVIDER_REJECTED",
        data={
            'provider': 'orange_money',
            'provider_message': 'Insufficient funds in mobile money account',
            'transaction_id': 'txn_123',
            'timestamp': '2026-06-21T10:30:00Z'
        },
        request_id='req_test123'
    )

    print(f"Full error string:\n{exc}\n")

    # The string should include the extra details (provider, provider_message, etc.)
    # but exclude the fields already displayed (message, error_code)
    print()


def test_exception_hierarchy():
    """Test exception inheritance"""
    print("Test 5: Exception hierarchy")
    print("-" * 50)

    # InsufficientBalanceError is a subclass of PaymentError
    exc1 = InsufficientBalanceError("Test")
    print(f"InsufficientBalanceError isinstance of PaymentError: {isinstance(exc1, PaymentError)}")
    print(f"InsufficientBalanceError isinstance of HunterTechPayError: {isinstance(exc1, HunterTechPayError)}")
    print()

    # All exceptions should be instances of HunterTechPayError
    exc2 = ValidationError("Test")
    exc3 = AuthenticationError("Test")
    exc4 = NotFoundError("Test")
    exc5 = ServerError("Test")

    print(f"ValidationError isinstance of HunterTechPayError: {isinstance(exc2, HunterTechPayError)}")
    print(f"AuthenticationError isinstance of HunterTechPayError: {isinstance(exc3, HunterTechPayError)}")
    print(f"NotFoundError isinstance of HunterTechPayError: {isinstance(exc4, HunterTechPayError)}")
    print(f"ServerError isinstance of HunterTechPayError: {isinstance(exc5, HunterTechPayError)}")
    print()


def test_exception_without_data():
    """Test exception without data"""
    print("Test 6: Exception without additional data")
    print("-" * 50)

    exc = ValidationError(
        message="Invalid request",
        status_code=400
    )

    print(f"Exception string: {exc}")
    print(f"Data: {exc.data}")
    error_dict = exc.to_dict()
    print(f"to_dict() result: {error_dict}")
    print()


def test_repr():
    """Test __repr__() method"""
    print("Test 7: __repr__() method")
    print("-" * 50)

    exc = ValidationError(
        message="Invalid phone number",
        status_code=400,
        error_code="VALIDATION_ERROR"
    )

    print(f"repr: {repr(exc)}")
    print()


def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("HunterTechPay SDK - Error Handling Tests")
    print("=" * 50)
    print()

    try:
        test_basic_exception()
        test_to_dict()
        test_get_detail()
        test_string_representation_with_details()
        test_exception_hierarchy()
        test_exception_without_data()
        test_repr()

        print("=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
