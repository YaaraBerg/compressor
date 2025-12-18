import unittest
from bitarray import bitarray
from lampel_ziv import convert_binarray_to_lampel_ziv_list


class TestLempelZiv(unittest.TestCase):

    def test_empty_data(self):
        """Test with empty bitarray"""
        data = bitarray()
        result = convert_binarray_to_lampel_ziv_list(data)
        self.assertEqual(result, [])

    def test_single_bit(self):
        """Test with single bit"""
        data = bitarray('1')
        result = convert_binarray_to_lampel_ziv_list(data)
        expected = [(0, 0, 1)]  # No match found for first bit
        self.assertEqual(result, expected)

    def test_two_same_bits(self):
        """Test with two identical bits - new algorithm includes next symbol"""
        data = bitarray('11')
        result = convert_binarray_to_lampel_ziv_list(data)
        expected = [(0, 0, 1), (0, 0, 1)]
        self.assertEqual(result, expected)

    def test_two_different_bits(self):
        """Test with two different bits"""
        data = bitarray('10')
        result = convert_binarray_to_lampel_ziv_list(data)
        expected = [(0, 0, 1), (0, 0, 0)]
        self.assertEqual(result, expected)

    def test_simple_pattern_new_algo(self):
        """Test simple pattern with new algorithm behavior"""
        data = bitarray('1010')
        result = convert_binarray_to_lampel_ziv_list(data, 1)
        expected = [(0, 0, 1), (0, 0, 0), (2, 1, 0)]
        self.assertEqual(result, expected)

    def test_longer_matches_length_2(self):
        """Test that longer matches are found with search_length=2"""
        data = bitarray('10101')
        result = convert_binarray_to_lampel_ziv_list(data, 2)
        expected = [(0, 0, 1), (0, 0, 0), (2, 2, 1)]
        self.assertEqual(result, expected)

    # def test_repeated_pattern_new_algo(self):
    #     """Test with repeated pattern - new algorithm behavior"""
    #     data = bitarray('11111')
    #     result = convert_binarray_to_lampel_ziv_list(data, 3)
    #     expected = [(0, 0, 1), (1, 3, 1)]
    #     self.assertEqual(result, expected)

    # def test_max_search_length_boundary(self):
    #     """Test behavior at search_length boundaries"""
    #     data = bitarray('11111')
    #     result_1 = convert_binarray_to_lampel_ziv_list(data, 1)
    #     result_2 = convert_binarray_to_lampel_ziv_list(data, 2)
    #     result_3 = convert_binarray_to_lampel_ziv_list(data, 3)

    #     # Longer search lengths should result in fewer, longer matches
    #     self.assertGreaterEqual(len(result_1), len(result_2))
    #     self.assertGreaterEqual(len(result_2), len(result_3))

    # def test_search_length_2_comprehensive(self):
    #     """Comprehensive test with search_length=2"""
    #     data = bitarray('101010')
    #     result = convert_binarray_to_lampel_ziv_list(data, 2)
    #     # Algorithm behavior: '10' (no match), '10' (matches at offset 2), '1' (matches at offset 2)
    #     expected = [
    #         (0, 0, 1),  # '1': no match
    #         (0, 0, 0),  # '0': no match
    #         (2, 2, 1),  # '10': matches previous '10', next symbol is '1'
    #         (2, 1, 0)   # '1': matches at offset 2, next symbol is 0 (end)
    #     ]
    #     self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
