import unittest
from bitarray import bitarray
from lampel_ziv import basic_lempel_ziv


class TestBasicLempelZiv(unittest.TestCase):

    def test_empty_data(self):
        """Test with empty bitarray"""
        data = bitarray()
        result = basic_lempel_ziv(data, 1, 1)
        self.assertEqual(result, [])

    def test_single_bit(self):
        """Test with single bit"""
        data = bitarray('1')
        result = basic_lempel_ziv(data, 1, 1)
        expected = [(0, 0, 1)]  # No match found for first bit
        self.assertEqual(result, expected)

    def test_two_same_bits(self):
        """Test with two identical bits - new algorithm includes next symbol"""
        data = bitarray('11')
        result = basic_lempel_ziv(data, 1, 1)
        expected = [(0, 0, 1), (0, 0, 1)]
        self.assertEqual(result, expected)

    def test_two_different_bits(self):
        """Test with two different bits"""
        data = bitarray('10')
        result = basic_lempel_ziv(data, 1, 1)
        expected = [(0, 0, 1), (0, 0, 0)]
        self.assertEqual(result, expected)

    def test_simple_pattern_new_algo(self):
        """Test simple pattern with new algorithm behavior"""
        data = bitarray('1010')
        result = basic_lempel_ziv(data, 2, 2)
        expected = [(0, 0, 1), (0, 0, 0), (2, 1, 0)]
        self.assertEqual(result, expected)

    def test_longer_matches_length_2(self):
        """Test that longer matches are found with search_length=2"""
        data = bitarray('10101')
        result = basic_lempel_ziv(data, 2, 2)
        expected = [(0, 0, 1), (0, 0, 0), (2, 2, 1)]
        self.assertEqual(result, expected)

    def test_future_string(self):
        """Test with repeated pattern - new algorithm behavior"""
        data = bitarray('11111')
        result = basic_lempel_ziv(data, 3, 3)
        expected = [(0, 0, 1), (1, 3, 1)]
        self.assertEqual(result, expected)


    def test_search_length_2_comprehensive(self):
        """Comprehensive test with search_length=2"""
        data = bitarray('101010')
        result = basic_lempel_ziv(data, 3, 3)
        expected = [(0, 0, 1), (0, 0, 0), (2, 3, 0)]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
