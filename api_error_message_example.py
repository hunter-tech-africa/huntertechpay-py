"""
Example: Accessing Original API Error Messages

This example shows how to access the exact error message from the HunterTechPay API.
"""

from huntertechpay import HunterTechPay
from huntertechpay.exceptions import HunterTechPayError, ValidationError
import os


def example_api_message():
    """Example showing how to get the original API error message"""
    hunter = HunterTechPay(
        api_key=os.environ.get('HUNTER_API_KEY', 'test_key'),
        secret_key=os.environ.get('HUNTER_SECRET_KEY', 'test_secret')
    )

    try:
        # This will fail with validation error
        result = hunter.deposit(
            amount=5000.00,
            currency='XAF',
            country='CM',
            phone='invalid_phone',  # Invalid phone format
            service_code='OM_CM_CASHIN'
        )

    except HunterTechPayError as e:
        print("=" * 60)
        print("ORIGINAL API ERROR MESSAGE")
        print("=" * 60)

        # Get the exact message from the API (unmodified)
        print(f"\nOriginal API message: {e.api_message}")

        # The message property might be the same or formatted
        print(f"Exception message: {e.message}")

        print("\n" + "=" * 60)
        print("COMPLETE ERROR DETAILS")
        print("=" * 60)

        # Full error string with all details
        print(f"\nFull error: {e}")

        print("\n" + "=" * 60)
        print("ERROR ATTRIBUTES")
        print("=" * 60)

        print(f"\nStatus Code: {e.status_code}")
        print(f"Error Code: {e.error_code}")
        print(f"Request ID: {e.request_id}")

        print("\n" + "=" * 60)
        print("COMPLETE API RESPONSE")
        print("=" * 60)

        # The 'data' attribute contains the full API response
        print(f"\nComplete API response data:")
        import json
        print(json.dumps(e.data, indent=2))

        print("\n" + "=" * 60)
        print("ERROR DICTIONARY (for logging)")
        print("=" * 60)

        # Convert to dict for logging
        error_dict = e.to_dict()
        print(json.dumps(error_dict, indent=2))


def example_comparing_messages():
    """Example comparing SDK message vs API message"""
    print("\n" + "=" * 60)
    print("COMPARING SDK MESSAGE VS API MESSAGE")
    print("=" * 60)

    hunter = HunterTechPay(
        api_key=os.environ.get('HUNTER_API_KEY', 'test_key'),
        secret_key=os.environ.get('HUNTER_SECRET_KEY', 'test_secret')
    )

    try:
        result = hunter.deposit(
            amount=-100,  # Invalid negative amount
            currency='XAF',
            country='CM',
            phone='+237690000000',
            service_code='OM_CM_CASHIN'
        )

    except ValidationError as e:
        print("\n1. Original API message (exact as received):")
        print(f"   '{e.api_message}'")

        print("\n2. SDK message (might be formatted):")
        print(f"   '{e.message}'")

        print("\n3. Are they the same?", e.api_message == e.message)

        print("\n4. Complete API response in 'data' attribute:")
        import json
        print(json.dumps(e.data, indent=2))


def example_raw_response_on_json_error():
    """Example when API returns non-JSON response"""
    print("\n" + "=" * 60)
    print("HANDLING NON-JSON API RESPONSES")
    print("=" * 60)

    # Simulate scenario where API returns HTML or plain text instead of JSON
    print("\nIf the API returns a non-JSON response (like HTML error page),")
    print("the SDK will capture it in e.data['raw_response']")
    print("\nExample:")
    print("  e.api_message = '<html>500 Internal Server Error</html>'")
    print("  e.data = {'raw_response': '<html>500 Internal Server Error</html>'}")


def example_accessing_specific_api_fields():
    """Example accessing specific fields from API error response"""
    print("\n" + "=" * 60)
    print("ACCESSING SPECIFIC API RESPONSE FIELDS")
    print("=" * 60)

    hunter = HunterTechPay(
        api_key=os.environ.get('HUNTER_API_KEY', 'test_key'),
        secret_key=os.environ.get('HUNTER_SECRET_KEY', 'test_secret')
    )

    try:
        result = hunter.withdraw(
            amount=100000.00,
            currency='XAF',
            country='CM',
            phone='+237670000000',
            service_code='MTN_CM_CASHOUT'
        )

    except HunterTechPayError as e:
        print("\nThe API might return additional fields in the error response:")
        print(f"- Original message: {e.api_message}")
        print(f"- Error code: {e.error_code}")

        # Access specific fields from the complete API response
        print("\nAccessing specific fields from API response:")

        # Method 1: Direct access to e.data
        if 'field' in e.data:
            print(f"  Field with error: {e.data['field']}")

        if 'validation_errors' in e.data:
            print(f"  Validation errors: {e.data['validation_errors']}")

        # Method 2: Using get_detail() helper
        field_name = e.get_detail('field', 'unknown')
        expected_value = e.get_detail('expected', 'N/A')
        received_value = e.get_detail('received', 'N/A')

        print(f"\n  Using get_detail() helper:")
        print(f"    Field: {field_name}")
        print(f"    Expected: {expected_value}")
        print(f"    Received: {received_value}")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("HUNTERTECHPAY SDK - API ERROR MESSAGE EXAMPLES")
    print("=" * 60)

    print("\nNote: These examples demonstrate error handling.")
    print("They may not run without valid API credentials.")
    print("The examples show the structure of error information.")

    # Uncomment to run specific examples:
    # example_api_message()
    # example_comparing_messages()
    # example_raw_response_on_json_error()
    # example_accessing_specific_api_fields()

    print("\n" + "=" * 60)
    print("KEY POINTS")
    print("=" * 60)
    print("""
1. e.api_message - Original error message from API (unmodified)
2. e.message     - Error message (might be formatted by SDK)
3. e.data        - Complete API response (all fields from API)
4. e.error_code  - Error code from API
5. e.status_code - HTTP status code
6. e.request_id  - Request ID for debugging

To log errors in your application:
    error_info = e.to_dict()
    logger.error("API call failed", extra=error_info)

This gives you:
    - error_type: Exception class name
    - message: Formatted message
    - api_message: Original API message
    - status_code: HTTP status
    - error_code: API error code
    - request_id: For support
    - data: Complete API response
""")
