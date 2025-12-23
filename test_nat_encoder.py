from bitarray import bitarray
from nat_encoder import encode_number, decode_number

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


def test_big_number():
    arr = bitarray()
    encode_number(arr, 1000)
    assert decode_number(arr) == 1000
    assert len(arr) == 0

def test_8():
    arr = bitarray()
    encode_number(arr, 8)
    assert decode_number(arr) == 8
    assert len(arr) == 0
