import unittest
from app import text_to_number, number_to_text, base64_to_number, number_to_base64
from flask import json
from app import app
import base64

class TestNumberConverterFunctions(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Test cases that should work for all conversion types
        self.test_numbers = [
            0,      # Zero
            42,     # Simple positive number
            255,    # Max single byte
            1000,   # Four digits
            65535,  # Max two bytes
        ]

    def test_text_conversion(self):
        # Test basic numbers
        test_cases = {
            "zero": 0,
            "nil": 0,
            "one": 1,
            "ten": 10,
            "twenty": 20,
            "forty-two": 42,
            "one hundred": 100,
            "one thousand": 1000,
            "one hundred and twenty-three": 123
        }
        for text, expected in test_cases.items():
            self.assertEqual(text_to_number(text), expected)
            # Test reverse conversion
            result = number_to_text(expected)
            self.assertTrue(isinstance(result, str))

        # Test case insensitivity
        self.assertEqual(text_to_number("FORTY-TWO"), 42)
        self.assertEqual(text_to_number("Forty-Two"), 42)

        # Test invalid inputs
        invalid_inputs = [
            "",             # Empty string
            "invalid",      # Invalid word
            "one.two",     # Invalid punctuation
            "million billion",  # Invalid combination
            "123",         # Contains digits
            "1st",         # Contains digits
            "twenty 5",    # Mixed text and digits
            None,           # Not a string
            123,            # Not a string
            3.14,          # Not a string
            [],            # Not a string
            {}             # Not a string
        ]
        for invalid in invalid_inputs:
            try:
                text_to_number(invalid)
                self.fail(f"Expected ValueError for input: {invalid}")
            except ValueError:
                pass  # Test passed

    def test_binary_conversion(self):
        # Test binary string conversion through API
        test_cases = [
            ("0", 0),
            ("101010", 42),
            ("11111111", 255),
            ("1111111111111111", 65535)
        ]
        for binary, decimal in test_cases:
            response = self.make_conversion_request(binary, 'binary', 'decimal')
            self.assertEqual(response['result'], str(decimal))
            # Test reverse conversion
            response = self.make_conversion_request(str(decimal), 'decimal', 'binary')
            self.assertEqual(response['result'], binary.zfill(len(binary)))

    def test_octal_conversion(self):
        # Test octal string conversion through API
        test_cases = [
            ("0", 0),
            ("52", 42),
            ("377", 255),
            ("177777", 65535)
        ]
        for octal, decimal in test_cases:
            response = self.make_conversion_request(octal, 'octal', 'decimal')
            self.assertEqual(response['result'], str(decimal))
            # Test reverse conversion
            response = self.make_conversion_request(str(decimal), 'decimal', 'octal')
            self.assertEqual(response['result'], octal if octal != '0' else '0')

    def test_hexadecimal_conversion(self):
        # Test hexadecimal string conversion through API
        test_cases = [
            ("0", 0),
            ("2a", 42),
            ("ff", 255),
            ("ffff", 65535)
        ]
        for hex_str, decimal in test_cases:
            response = self.make_conversion_request(hex_str, 'hexadecimal', 'decimal')
            self.assertEqual(response['result'], str(decimal))
            # Test reverse conversion
            response = self.make_conversion_request(str(decimal), 'decimal', 'hexadecimal')
            self.assertEqual(response['result'], hex_str)

    def test_base64_conversion(self):
        # Test base64 conversion (using big-endian as per app implementation)
        for num in self.test_numbers:
            # Convert to base64
            encoded = number_to_base64(num)
            # Convert back to number
            decoded = base64_to_number(encoded)
            self.assertEqual(decoded, num)

        # Test special case for zero
        self.assertEqual(number_to_base64(0), 'AA==')
        self.assertEqual(base64_to_number('AA=='), 0)

        # Test invalid inputs for base64_to_number
        invalid_base64_inputs = [
            "",             # Empty string
            "invalid!",     # Invalid characters
            "AAA=",        # Invalid padding
            "=====",       # Too much padding
            "@#$%",       # Non-base64 characters
            None,           # Not a string
            123,            # Not a string
            3.14,          # Not a string
            [],            # Not a string
            {},            # Not a string
            "A",           # Single character
            "AA",          # Two characters
            "AAA",         # Three characters
            "A====",       # Too much padding
            "A===",        # Invalid padding
            "AA===",       # Invalid padding
            "AAA==",       # Invalid padding
            "=====",       # All padding
            "=",           # Single padding
            "==",          # Double padding
            "===",         # Triple padding
            "A=B=",        # Padding in middle
            "A==",         # Invalid content with valid padding
            "AB==",        # Invalid content with valid padding
            "ABC=",        # Invalid content with valid padding
            "ABCD="       # Invalid content with valid padding
        ]
        for invalid in invalid_base64_inputs:
            try:
                base64_to_number(invalid)
                self.fail(f"Expected ValueError for input: {invalid}")
            except ValueError:
                pass  # Test passed

        # Test invalid inputs for number_to_base64
        invalid_numbers = [
            None,           # Not a number
            "123",         # Not a number
            -1,            # Negative number
            3.14,          # Float
            complex(1, 2),  # Complex number
            [],            # Not a number
            {},            # Not a number
            2**32,         # Very large number
            2**64          # Very large number
        ]
        for invalid in invalid_numbers:
            try:
                number_to_base64(invalid)
                self.fail(f"Expected ValueError for input: {invalid}")
            except ValueError:
                pass  # Test passed

    def test_all_conversion_paths(self):
        # Test conversion between all possible types
        types = ['text', 'binary', 'octal', 'decimal', 'hexadecimal', 'base64']
        test_value = 42

        for input_type in types:
            for output_type in types:
                if input_type == output_type:
                    continue

                # Prepare input value based on input type
                if input_type == 'text':
                    input_val = 'forty-two'
                elif input_type == 'binary':
                    input_val = '101010'
                elif input_type == 'octal':
                    input_val = '52'
                elif input_type == 'decimal':
                    input_val = '42'
                elif input_type == 'hexadecimal':
                    input_val = '2a'
                else:  # base64
                    input_val = number_to_base64(test_value)

                response = self.make_conversion_request(input_val, input_type, output_type)
                self.assertIsNone(response['error'], 
                    f"Error converting from {input_type} to {output_type}: {response['error']}")

    def test_large_numbers(self):
        """Test handling of very large numbers across all conversion types"""
        # Test numbers that should work
        safe_numbers = [
            2**16,      # 65536
            2**24,      # 16,777,216
        ]

        # Test numbers that should fail
        unsafe_numbers = [
            2**32,      # 4,294,967,296
            2**48,      # 281,474,976,710,656
            2**63 - 1   # Maximum safe integer in many systems
        ]

        # Test safe numbers - these should all work
        for num in safe_numbers:
            decimal_str = str(num)
            
            # Test all conversions
            for output_type in ['binary', 'hexadecimal', 'octal', 'base64']:
                response = self.make_conversion_request(decimal_str, 'decimal', output_type)
                self.assertIsNone(response['error'], 
                    f"Failed to convert {num} to {output_type}")
                
                # Test conversion back to decimal
                if output_type != 'base64':  # Skip base64 round-trip as it's tested separately
                    result = response['result']
                    response = self.make_conversion_request(result, output_type, 'decimal')
                    self.assertEqual(response['result'], decimal_str, 
                        f"Round-trip conversion failed for {num} via {output_type}")

            # Test base64 specifically
            try:
                encoded = number_to_base64(num)
                decoded = base64_to_number(encoded)
                self.assertEqual(decoded, num, 
                    f"base64 conversion failed for safe number {num}")
            except ValueError as e:
                self.fail(f"base64 conversion should work for safe number {num}")

        # Test unsafe numbers - these should fail for base64
        for num in unsafe_numbers:
            decimal_str = str(num)
            
            # Test base64 conversion - should fail
            with self.assertRaises(ValueError, 
                msg=f"base64 conversion should fail for unsafe number {num}"):
                number_to_base64(num)

            # Other conversions should still work
            for output_type in ['binary', 'hexadecimal', 'octal']:
                response = self.make_conversion_request(decimal_str, 'decimal', output_type)
                self.assertIsNone(response['error'], 
                    f"Failed to convert {num} to {output_type}")
                
                # Test conversion back to decimal
                result = response['result']
                response = self.make_conversion_request(result, output_type, 'decimal')
                self.assertEqual(response['result'], decimal_str, 
                    f"Round-trip conversion failed for {num} via {output_type}")

    def test_error_handling(self):
        # Test missing or invalid JSON fields
        invalid_requests = [
            {},  # Empty request
            {'input': '42'},  # Missing types
            {'input': '42', 'inputType': 'decimal'},  # Missing output type
            {'inputType': 'decimal', 'outputType': 'binary'},  # Missing input
        ]
        for req in invalid_requests:
            response = self.app.post('/convert',
                                   data=json.dumps(req),
                                   content_type='application/json')
            data = json.loads(response.data)
            self.assertIsNotNone(data['error'])

        # Test invalid conversion types
        response = self.make_conversion_request('42', 'invalid', 'binary')
        self.assertIsNotNone(response['error'])
        response = self.make_conversion_request('42', 'decimal', 'invalid')
        self.assertIsNotNone(response['error'])

        # Test invalid inputs for each type
        invalid_cases = [
            ('text', 'not-a-number'),
            ('binary', '102'),  # Invalid binary digit
            ('octal', '89'),    # Invalid octal digit
            ('decimal', 'abc'),  # Not a number
            ('hexadecimal', 'gh'),  # Invalid hex digit
            ('base64', '!@#')   # Invalid base64
        ]
        for input_type, invalid_input in invalid_cases:
            response = self.make_conversion_request(invalid_input, input_type, 'decimal')
            self.assertIsNotNone(response['error'])

    def test_index_route(self):
        # Test the index route returns 200 and contains expected content
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def make_conversion_request(self, input_val, input_type, output_type):
        """Helper method to make conversion requests"""
        request_data = {
            'input': input_val,
            'inputType': input_type,
            'outputType': output_type
        }
        response = self.app.post('/convert',
                               data=json.dumps(request_data),
                               content_type='application/json')
        return json.loads(response.data)

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()
