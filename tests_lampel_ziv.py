import unittest
from bitarray import bitarray
from lampel_ziv import basic_lempel_ziv, convert_lampel_ziv_list_to_binarray

TEST_CONFIG = {
    'minimum_match_length': 1
}


def b2ba(data: bytes) -> bitarray:
    ba = bitarray()
    ba.frombytes(data)
    return ba


class TestBasicLempelZiv(unittest.TestCase):

    def test_empty_data(self):
        """Test with empty bitarray"""
        data = bitarray()
        result = basic_lempel_ziv(data, 1, 1, **TEST_CONFIG)
        self.assertEqual(result, [])

    def test_single_byte(self):
        """Test with single byte"""
        data = b2ba(b'A')  # 'A' = 0x41 = 01000001
        result = basic_lempel_ziv(data, 1, 1, **TEST_CONFIG)
        expected = [(0, 0, b2ba(b'A'))]  # No match found for first byte
        self.assertEqual(result, expected)

    def test_two_same_bytes(self):
        """Test with two identical bytes"""
        data = b2ba(b'AA')
        result = basic_lempel_ziv(data, 1, 1, **TEST_CONFIG)
        expected = [(0, 0, b2ba(b'A')), (0, 0, b2ba(b'A'))]
        self.assertEqual(result, expected)

    def test_two_different_bytes(self):
        """Test with two different bytes"""
        data = b2ba(b'AB')
        result = basic_lempel_ziv(data, 1, 1, **TEST_CONFIG)
        expected = [(0, 0, b2ba(b'A')), (0, 0, b2ba(b'B'))]
        self.assertEqual(result, expected)

    def test_simple_pattern(self):
        """Test simple repeating pattern"""
        data = b2ba(b'ABAB')
        result = basic_lempel_ziv(data, 2, 2, **TEST_CONFIG)
        expected = [(0, 0, b2ba(b'A')), (0, 0, b2ba(b'B')), (2, 1, b2ba(b'B'))]
        self.assertEqual(result, expected)

    def test_longer_matches(self):
        """Test that longer matches are found"""
        data = b2ba(b'ABABA')
        result = basic_lempel_ziv(data, 2, 2, **TEST_CONFIG)
        expected = [(0, 0, b2ba(b'A')), (0, 0, b2ba(b'B')), (2, 2, b2ba(b'A'))]
        self.assertEqual(result, expected)

    def test_repeated_byte_pattern(self):
        """Test with repeated byte pattern"""
        data = b2ba(b'AAAAA')
        result = basic_lempel_ziv(data, 3, 3, **TEST_CONFIG)
        expected = [(0, 0, b2ba(b'A')), (1, 3, b2ba(b'A'))]
        self.assertEqual(result, expected)

    def test_comprehensive_pattern(self):
        """Comprehensive test with longer pattern"""
        data = b2ba(b'ABCABC')
        result = basic_lempel_ziv(data, 3, 3, **TEST_CONFIG)
        expected = [(0, 0, b2ba(b'A')), (0, 0, b2ba(b'B')), (0, 0, b2ba(b'C')), (3, 2, b2ba(b'C'))]
        self.assertEqual(result, expected)


class TestRoundTrip(unittest.TestCase):
    """Test that compression and decompression work correctly together"""

    def test_round_trip_simple(self):
        """Test round trip for simple data"""
        test_cases = [
            b'A',
            b'AB',
            b'ABC',
            b'ABCD',
            b'AAAA',
            b'ABAB',
            b'ABCABC'
        ]

        for test_data in test_cases:
            with self.subTest(data=test_data):
                data = b2ba(test_data)
                lz_triplets = basic_lempel_ziv(data, 256, 32, **TEST_CONFIG)
                decoded = convert_lampel_ziv_list_to_binarray(lz_triplets)
                self.assertEqual(data, decoded)

    def test_round_trip_text(self):
        """Test round trip for text data"""
        text_data = b"Hello, World! This is a test message with some repetition. Hello again!"
        data = b2ba(text_data)
        lz_triplets = basic_lempel_ziv(data, 256, 32, **TEST_CONFIG)
        decoded = convert_lampel_ziv_list_to_binarray(lz_triplets)
        self.assertEqual(data, decoded)


class MinReproduce(unittest.TestCase):
    def test_reproduce(self):
        """Test the minimal reproduce case"""
        # Convert the bit pattern to a byte-aligned pattern
        # Original: '01011' -> pad to '01011000' (5 bits -> 8 bits)
        data = bitarray('01011000')  # Padded to byte boundary
        lz_triplets = basic_lempel_ziv(data, 256, 32, **TEST_CONFIG)
        decoded = convert_lampel_ziv_list_to_binarray(lz_triplets)
        self.assertEqual(data, decoded)

if __name__ == '__main__':
    unittest.main()
