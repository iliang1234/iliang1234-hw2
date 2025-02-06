import unittest
from app import text_to_number, number_to_text, base64_to_number, number_to_base64
from flask import json
from app import app

class TestNumberConverterFunctions(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_text_to_number_edge_cases(self):
        # Test compound numbers with hyphens
        self.assertEqual(text_to_number("twenty-one"), 21)
        self.assertEqual(text_to_number("forty-two"), 42)
        
        # Test multi-word numbers
        self.assertEqual(text_to_number("one hundred"), 100)
        self.assertEqual(text_to_number("one hundred and twenty three"), 123)
        
        # Test zero synonyms
        self.assertEqual(text_to_number("nil"), 0)
        self.assertEqual(text_to_number("zero"), 0)
        
        # Test invalid inputs
        with self.assertRaises(ValueError):
            text_to_number("nill")
        with self.assertRaises(ValueError):
            text_to_number("")
        with self.assertRaises(ValueError):
            text_to_number("invalid")

    def test_number_to_text_edge_cases(self):
        # Bug 5: Negative numbers aren't properly handled
        with self.assertRaises(ValueError):
            number_to_text(-42)

        # Bug 6: Large numbers might cause issues
        try:
            result = number_to_text(999999999999999)
            self.assertTrue(isinstance(result, str))
        except ValueError:
            self.fail("Large numbers should be handled")

        # Bug 7: Float numbers aren't handled
        with self.assertRaises(ValueError):
            number_to_text(3.14)

    def test_base64_edge_cases(self):
        # Bug 8: Negative numbers in base64
        with self.assertRaises(ValueError):
            number_to_base64(-1)

        # Bug 9: Zero padding in base64
        # This test verifies if leading zeros are handled correctly
        encoded = number_to_base64(0)
        self.assertEqual(base64_to_number(encoded), 0)

        # Bug 10: Very large numbers might overflow
        large_num = 2**64
        try:
            encoded = number_to_base64(large_num)
            decoded = base64_to_number(encoded)
            self.assertEqual(decoded, large_num)
        except OverflowError:
            self.fail("Large numbers should be handled in base64 conversion")

    def test_api_edge_cases(self):
        # Bug 11: Missing fields in JSON
        incomplete_cases = [
            {'input': '42'},  # Missing inputType and outputType
            {'input': '42', 'inputType': 'decimal'},  # Missing outputType
            {'inputType': 'decimal', 'outputType': 'binary'},  # Missing input
        ]
        for test_case in incomplete_cases:
            response = self.app.post('/convert',
                                   data=json.dumps(test_case),
                                   content_type='application/json')
            data = json.loads(response.data)
            self.assertIsNotNone(data['error'])

        # Bug 12: Invalid conversion types
        invalid_types = [
            {
                'input': '42',
                'inputType': 'invalid_type',
                'outputType': 'binary'
            },
            {
                'input': '42',
                'inputType': 'decimal',
                'outputType': 'invalid_type'
            }
        ]
        for test_case in invalid_types:
            response = self.app.post('/convert',
                                   data=json.dumps(test_case),
                                   content_type='application/json')
            data = json.loads(response.data)
            self.assertIsNotNone(data['error'])

        # Bug 13: Empty string inputs
        empty_input = {
            'input': '',
            'inputType': 'decimal',
            'outputType': 'binary'
        }
        response = self.app.post('/convert',
                               data=json.dumps(empty_input),
                               content_type='application/json')
        data = json.loads(response.data)
        self.assertIsNotNone(data['error'])

        # Bug 14: Unicode characters in input
        unicode_input = {
            'input': '４２',  # Full-width digits
            'inputType': 'decimal',
            'outputType': 'binary'
        }
        response = self.app.post('/convert',
                               data=json.dumps(unicode_input),
                               content_type='application/json')
        data = json.loads(response.data)
        self.assertIsNotNone(data['error'])

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()
