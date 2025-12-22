import unittest
from bitarray import bitarray
from main import encoder, decoder, CONFIG


class TestEncoderDecoder(unittest.TestCase):
    """Comprehensive tests to ensure encoder/decoder consistency: decoder(encoder(X)) == X"""

    def test_empty_data(self):
        """Test with empty bitarray"""
        data = bitarray()
        compressed = encoder(data)
        decoded = decoder(compressed)
        self.assertEqual(data, decoded)

    def test_single_bit(self):
        """Test with single bit 0"""
        data = bitarray('0')
        compressed = encoder(data)
        decoded = decoder(compressed)
        self.assertEqual(data, decoded)

    def test_short_patterns(self):
        """Test with short bit patterns"""
        patterns = [
            '000',
            '111',
            '101',
            '010',
            '1010',
            '0101',
            '1100',
            '0011',
            '1001',
            '0110'
        ]

        for pattern in patterns:
            with self.subTest(pattern=pattern):
                data = bitarray(pattern)
                compressed = encoder(data)
                decoded = decoder(compressed)
                self.assertEqual(data, decoded, f"Failed for pattern: {pattern}")

    def test_repeating_patterns(self):
        """Test with repeating patterns that should compress well"""
        patterns = [
            '0' * 10,           # All zeros
            '1' * 10,           # All ones
            '01' * 10,          # Alternating 01
            '10' * 10,          # Alternating 10
            '001' * 7,          # Repeating 001
            '110' * 7,          # Repeating 110
            '1010' * 5,         # Repeating 1010
            '1100' * 5,         # Repeating 1100
        ]

        for pattern in patterns:
            with self.subTest(pattern=pattern[:20] + "..."):
                data = bitarray(pattern)
                compressed = encoder(data)
                decoded = decoder(compressed)
                self.assertEqual(data, decoded, f"Failed for repeating pattern: {pattern[:20]}...")

    def test_random_like_patterns(self):
        """Test with pseudo-random patterns that should not compress well"""
        patterns = [
            '10110100101',
            '01001011010',
            '11010010110',
            '00101101001',
            '10101100110010',
            '01100100101101',
            '11001010011010',
            '00110101100101'
        ]

        for pattern in patterns:
            with self.subTest(pattern=pattern):
                data = bitarray(pattern)
                compressed = encoder(data)
                decoded = decoder(compressed)
                self.assertEqual(data, decoded, f"Failed for random pattern: {pattern}")

    def test_gradual_lengths(self):
        """Test with gradually increasing lengths"""
        base_pattern = '1010110011'

        for length in [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 200]:
            # Cycle the pattern to get desired length
            pattern = (base_pattern * ((length // len(base_pattern)) + 1))[:length]

            with self.subTest(length=length):
                data = bitarray(pattern)
                compressed = encoder(data)
                decoded = decoder(compressed)
                self.assertEqual(data, decoded, f"Failed for length {length}")


    def test_compression_and_expansion_cases(self):
        """Test cases that should compress well and cases that should expand"""
        test_cases = [
            ('highly_compressible_zeros', '0' * 1000),
            ('highly_compressible_ones', '1' * 1000),
            ('highly_compressible_pattern', '0101' * 250),
        ]

        for name, pattern in test_cases:
            with self.subTest(case=name):
                data = bitarray(pattern)
                compressed = encoder(data)
                decoded = decoder(compressed)
                self.assertEqual(data, decoded, f"Failed for {name}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
