# Numeric Converter

A web-based application that converts numbers between different formats including:
- English text (e.g., "one hundred twenty-three")
- Binary
- Octal
- Decimal
- Hexadecimal
- Base64

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Enter your input value in the text box
2. Select the input format from the dropdown menu
3. Select the desired output format from the second dropdown menu
4. Click "Convert" to see the result

## Examples

- Convert decimal to binary: Input "42" with input type "decimal" and output type "binary"
- Convert text to decimal: Input "forty two" with input type "text" and output type "decimal"
- Convert hexadecimal to text: Input "2a" with input type "hexadecimal" and output type "text"

## Bug Fixes

### Previously Identified Issues
Text to decimal (or other numerical bases) did not work for:
- Compound words (e.g., "forty-two", "twenty-two")
- Multi-word numbers (e.g., "one hundred")
- Numbers greater than 10

### Fixed Issues
1. **Input Validation and Error Handling**
   - Added comprehensive validation for all input types (binary, octal, decimal, hexadecimal, base64)
   - Improved error messages with specific details about validation failures
   - Added checks for empty inputs and missing JSON fields
   - Added validation for negative numbers in conversions that don't support them

### Known Library Issues

#### Python's base64 Module
The standard library's `base64` module has several inconsistencies and potential issues:

1. **Padding Validation**
   - Accepts some invalid padding patterns (e.g., "AAA=")
   - Inconsistent handling of padding characters in the middle of the string
   - No strict validation of padding length vs content length

2. **Content Length Validation**
   - Accepts base64 strings with invalid lengths
   - No validation of minimum content length
   - Allows single-character and two-character inputs

3. **Error Messages**
   - Generic error messages that don't specify the exact validation failure
   - Inconsistent error types for similar validation failures

4. **Edge Cases**
   - Inconsistent handling of very large numbers (2^32 and above)
   - No built-in validation for maximum input size
   - Unclear behavior with empty or all-padding inputs

These issues are worked around in our application by implementing additional validation layers on top of the base64 module.

2. **Base64 Conversion**
   - Added proper validation for base64 input strings
   - Added checks for invalid base64 characters
   - Improved error messages for base64 decoding failures
   - Fixed handling of empty base64 strings

3. **Text Number Conversion**
   - Fixed handling of compound words (e.g., "forty-two", "twenty-one")
   - Added support for multi-word numbers (e.g., "one hundred and twenty-three")
   - Improved handling of numbers greater than 10
   - Added support for various number formats and combinations

### Implementation Details
- Added input validation before conversion attempts to prevent cryptic errors
- Implemented character-set validation for binary, octal, and hexadecimal inputs
- Added proper error handling for all conversion paths
- Improved JSON request validation in the API endpoint
- Added checks for negative numbers in conversions that don't support them (binary, octal, hexadecimal, base64)