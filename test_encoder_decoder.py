import unittest
from bitarray import bitarray
from main import encoder, decoder, CONFIG


def b2ba(data: bytes) -> bitarray:
    ba = bitarray()
    ba.frombytes(data)
    return ba


class TestEncoderDecoder(unittest.TestCase):
    """Comprehensive tests to ensure encoder/decoder consistency: decoder(encoder(X)) == X"""

    def test_empty_data(self):
        """Test with empty bitarray"""
        data = bitarray()
        compressed = encoder(data)
        decoded = decoder(compressed)
        self.assertEqual(data, decoded)

    def test_single_byte(self):
        """Test with single byte"""
        data = b2ba(b'A')
        compressed = encoder(data)
        decoded = decoder(compressed)
        self.assertEqual(data, decoded)

    def test_simple_text_patterns(self):
        """Test with simple text patterns"""
        patterns = [
            b'ABC',
            b'XYZ',
            b'123',
            b'Hello',
            b'Test!',
            b'ab',
            b'AB'
        ]

        for pattern in patterns:
            with self.subTest(pattern=pattern):
                data = b2ba(pattern)
                compressed = encoder(data)
                decoded = decoder(compressed)
                self.assertEqual(data, decoded, f"Failed for pattern: {pattern}")

    def test_repeating_byte_patterns(self):
        """Test with repeating byte patterns that should compress well"""
        patterns = [
            b'A' * 10,           # All A's
            b'B' * 10,           # All B's
            b'AB' * 10,          # Alternating AB
            b'BA' * 10,          # Alternating BA
            b'XYZ' * 7,          # Repeating XYZ
            b'ABC' * 7,          # Repeating ABC
            b'1234' * 5,         # Repeating 1234
            b'AABB' * 5,         # Repeating AABB
        ]

        for pattern in patterns:
            with self.subTest(pattern=pattern[:20].decode('utf-8', errors='ignore') + "..."):
                data = b2ba(pattern)
                compressed = encoder(data)
                decoded = decoder(compressed)
                self.assertEqual(data, decoded, f"Failed for repeating pattern: {pattern[:20]}...")

    def test_varied_content_patterns(self):
        """Test with varied content patterns"""
        patterns = [
            b'Hello World!',
            b'The quick brown fox',
            b'ABCDEFGHIJKLMNOP',
            b'1234567890',
            b'Testing123',
            b'Mix3d_Ch4r5!',
        ]

        for pattern in patterns:
            with self.subTest(pattern=pattern):
                data = b2ba(pattern)
                compressed = encoder(data)
                decoded = decoder(compressed)
                self.assertEqual(data, decoded, f"Failed for varied pattern: {pattern}")

    def test_gradual_lengths(self):
        """Test with gradually increasing lengths"""
        base_text = b'Hello123'

        for length in [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]:
            # Cycle the pattern to get desired length
            pattern = (base_text * ((length // len(base_text)) + 1))[:length]

            with self.subTest(length=length):
                data = b2ba(pattern)
                compressed = encoder(data)
                decoded = decoder(compressed)
                self.assertEqual(data, decoded, f"Failed for length {length}")

    def test_compression_cases(self):
        """Test cases that should compress well"""
        test_cases = [
            ('repeated_As', b'A' * 100),
            ('repeated_pattern', b'ABC' * 50),
            ('text_with_repetition', b'Hello World! ' * 20),
        ]

        for name, pattern in test_cases:
            with self.subTest(case=name):
                data = b2ba(pattern)
                compressed = encoder(data)
                decoded = decoder(compressed)
                self.assertEqual(data, decoded, f"Failed for {name}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
