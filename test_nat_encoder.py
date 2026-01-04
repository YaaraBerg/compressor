from bitarray import bitarray
from nat_encoder import encode_number, decode_number, SMALL_NUMBER_BITS

def test_small_numbers():
    arr = bitarray()
    encode_number(arr, 0)
    assert decode_number(arr) == 0
    assert len(arr) == 0

def test_multiple_small_nums():
    arr = bitarray()
    encode_number(arr, 0)
    encode_number(arr, 1)
    encode_number(arr, 2)
    encode_number(arr, 3)
    assert decode_number(arr) == 0
    assert decode_number(arr) == 1
    assert decode_number(arr) == 2
    assert decode_number(arr) == 3
    assert len(arr) == 0

def test_boundary_numbers():
    """Test the boundary between small and large numbers"""
    arr = bitarray()
    # Largest small number: (2^SMALL_NUMBER_BITS - 1)
    max_small = (1 << SMALL_NUMBER_BITS) - 1
    # Smallest large number: 2^SMALL_NUMBER_BITS
    min_large = 1 << SMALL_NUMBER_BITS

    encode_number(arr, max_small)
    encode_number(arr, min_large)
    assert decode_number(arr) == max_small
    assert decode_number(arr) == min_large
    assert len(arr) == 0

def test_big_number():
    arr = bitarray()
    encode_number(arr, 1000)
    assert decode_number(arr) == 1000
    assert len(arr) == 0

