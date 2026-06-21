# Changelog

All notable changes to the HunterTechPay Python SDK will be documented in this file.

## [1.0.1] - 2026-06-21

### Added - Enhanced Error Handling

#### New Exception Methods

- **`to_dict()`**: Convert exception to dictionary format for logging and debugging
  ```python
  error_info = e.to_dict()
  # Returns: {'error_type': 'ValidationError', 'message': '...', 'status_code': 400, ...}
  ```

- **`get_detail(key, default=None)`**: Access specific fields from API error response
  ```python
  available = e.get_detail('available_balance', 0)
  required = e.get_detail('required_balance', 0)
  ```

#### Improved Error Messages

- Error messages now include **all API response details** automatically
- Format: `"Message | Status: 400 | Code: ERROR_CODE | Details: {...}"`
- Previously hidden API error details are now visible in the error string

#### Better Error Parsing

- Support for multiple error message fields: `detail`, `message`, `error`, `error_message`
- Support for multiple error code fields: `error_code`, `code`
- Support for multiple request ID headers: `X-Request-ID`, `X-Hunter-Request-ID`
- Better handling of non-JSON error responses (includes response text)
- Response text included in error message when JSON parsing fails

### Changed

- Enhanced `HunterTechPayError.__str__()` to display additional API response details
- Improved `exception_from_response()` to capture more error information
- Added `json` module import to exceptions module

### Examples

New file `error_handling_examples.py` with comprehensive examples:
- Basic error handling with detailed messages
- Accessing specific error details
- Getting complete error information as dictionary
- Handling different error types
- Retry logic with error details
- Accessing raw API response data

### Documentation

- Updated README.md Error Handling section with:
  - New methods documentation
  - Complete examples of error handling patterns
  - Retry logic examples
  - Accessing error details examples

### Migration Guide

**No breaking changes!** All existing code continues to work.

New features are additive:

```python
# Before (still works)
try:
    hunter.deposit(...)
except HunterTechPayError as e:
    print(f"Error: {e.message}")
    print(f"Status: {e.status_code}")

# After (now you can also do this)
try:
    hunter.deposit(...)
except HunterTechPayError as e:
    # Complete error string with all details
    print(f"Error: {e}")

    # Access specific API response fields
    field_value = e.get_detail('specific_field', default_value)

    # Get complete error info for logging
    error_dict = e.to_dict()
    logger.error("Operation failed", extra=error_dict)
```

### Benefits

1. **Better Debugging**: All API error details are now visible
2. **Easier Error Handling**: Access specific error fields with `get_detail()`
3. **Better Logging**: Convert errors to dictionaries for structured logging
4. **No Breaking Changes**: Backward compatible with existing code
5. **Complete Transparency**: Users can see exactly what the API returned

---

## [1.1.0] - 2026-03-14

### Added
- Initial SDK release
- Support for all HunterTechPay API endpoints
- Comprehensive exception handling
- Request signing and authentication
- Validation utilities
- Model classes for type safety

---

## Format

This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

Types of changes:
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes
