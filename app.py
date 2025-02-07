from flask import Flask, render_template, request, jsonify
from num2words import num2words
from text2digits import text2digits
import base64
import re

app = Flask(__name__)

def text_to_number(text):
    """Convert English text number to integer"""
    # Validate input type
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    # Check for empty string
    if not text:
        raise ValueError("Empty string")

    # Check for invalid characters (only allow letters, spaces, and hyphens)
    if not all(c.isalpha() or c.isspace() or c == '-' for c in text):
        raise ValueError("Text should only contain letters, spaces, and hyphens")

    # Remove extra spaces and convert to lowercase
    text = ' '.join(text.lower().split())
    
    # Special case for zero
    if text in ['zero', 'nil']:
        return 0

    # Reject strings containing digits
    if any(c.isdigit() for c in text):
        raise ValueError("Text should not contain digits")

    # Check for invalid word combinations
    words = text.split()
    magnitude_words = ['billion', 'million', 'trillion']
    if any(word in magnitude_words for word in words[1:]):
        raise ValueError("Invalid number word combination")

    # Initialize text2digits converter
    t2d = text2digits.Text2Digits()
    
    try:
        # Convert text to number string
        # Replace hyphens with spaces to handle cases like "twenty-one"
        text = text.replace('-', ' ')
        number_str = t2d.convert(text)
        
        # The converter might return multiple numbers; we'll take the first one
        # Find all numbers in the string
        numbers = re.findall(r'\d+', number_str)
        if numbers:
            return int(numbers[0])
        
        raise ValueError("No valid number found in text")
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Unable to convert text to number: {str(e)}")

def number_to_text(number):
    """Convert integer to English text"""
    try:
        return num2words(number)
    except:
        raise ValueError("Unable to convert number to text")

def base64_to_number(b64_str):
    """Convert base64 to integer"""
    # Validate input type
    if not isinstance(b64_str, str):
        raise ValueError("Input must be a string")

    # Check for empty string
    if not b64_str:
        raise ValueError("Empty base64 string")

    # Special case for zero
    if b64_str == 'AA==':
        return 0

    # Validate base64 format
    try:
        # Try to decode the base64 string
        decoded_bytes = base64.b64decode(b64_str, validate=True)
        if len(decoded_bytes) == 0:
            raise ValueError("Invalid base64 input")
            
        # Convert to integer
        return int.from_bytes(decoded_bytes, byteorder='big')
    except Exception:
        raise ValueError("Invalid base64 input")

def number_to_base64(number):
    """Convert integer to base64"""
    try:
        if not isinstance(number, int):
            raise ValueError("Input must be an integer")
        if number < 0:
            raise ValueError("Number must be non-negative")
            
        # Special case for zero to ensure consistent encoding
        if number == 0:
            return 'AA=='
            
        # Convert integer to bytes, then encode to base64
        byte_count = max(1, (number.bit_length() + 7) // 8)
        number_bytes = number.to_bytes(byte_count, byteorder='big')
        return base64.b64encode(number_bytes).decode('utf-8')
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Unable to convert to base64: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Missing request data")

        # Validate required fields
        required_fields = ['input', 'inputType', 'outputType']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        input_value = data['input']
        input_type = data['inputType']
        output_type = data['outputType']

        # Validate input value is not empty
        if not input_value and input_value != '0':
            raise ValueError("Input value cannot be empty")

        # Validate conversion types
        valid_types = {'text', 'binary', 'octal', 'decimal', 'hexadecimal', 'base64'}
        if input_type not in valid_types:
            raise ValueError(f"Invalid input type: {input_type}")
        if output_type not in valid_types:
            raise ValueError(f"Invalid output type: {output_type}")
        
        # Convert input to integer based on input type
        try:
            if input_type == 'text':
                number = text_to_number(input_value)
            elif input_type == 'binary':
                if not all(c in '01' for c in input_value):
                    raise ValueError("Invalid binary number")
                number = int(input_value, 2)
            elif input_type == 'octal':
                if not all(c in '01234567' for c in input_value):
                    raise ValueError("Invalid octal number")
                number = int(input_value, 8)
            elif input_type == 'decimal':
                if not input_value.strip('-').isdigit():
                    raise ValueError("Invalid decimal number")
                number = int(input_value)
            elif input_type == 'hexadecimal':
                if not all(c in '0123456789abcdefABCDEF' for c in input_value):
                    raise ValueError("Invalid hexadecimal number")
                number = int(input_value, 16)
            else:  # base64
                number = base64_to_number(input_value)
        except ValueError as e:
            raise ValueError(f"Invalid {input_type} input: {str(e)}")

        # Validate number is non-negative for certain conversions
        if number < 0 and output_type in {'binary', 'octal', 'hexadecimal', 'base64'}:
            raise ValueError(f"Negative numbers cannot be converted to {output_type}")
            
        # Convert integer to output type
        try:
            if output_type == 'text':
                result = number_to_text(number)
            elif output_type == 'binary':
                result = bin(number)[2:]  # Remove '0b' prefix
            elif output_type == 'octal':
                result = oct(number)[2:]  # Remove '0o' prefix
            elif output_type == 'decimal':
                result = str(number)
            elif output_type == 'hexadecimal':
                result = hex(number)[2:]  # Remove '0x' prefix
            else:  # base64
                result = number_to_base64(number)
        except ValueError as e:
            raise ValueError(f"Error converting to {output_type}: {str(e)}")
            
        return jsonify({'result': result, 'error': None})
    except Exception as e:
        return jsonify({'result': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
