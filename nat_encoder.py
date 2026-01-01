"""
Encode a natural number
"""
from bitarray import bitarray
from bitarray.util import ba2int, int2ba
import math

SMALL_NUMBER_BITS = 5

def encode_number(bit_data: bitarray, number: int) -> None:
    if number < 0:
        raise ValueError(f'Unexpected negative: {number}')
    # Small numbers: 1 then SMALL_NUMBER_BITS bits for the number
    if number < (1 << SMALL_NUMBER_BITS):
        bit_data.extend([1])  # Flag for small number
        number_bits = int2ba(number, length=SMALL_NUMBER_BITS)
        bit_data.extend(number_bits)
        return
    # Bit number: #0 = loglog(n), then log(n), then n
    logn = 1 + math.floor(math.log2(number))
    loglogn = 1 + math.floor(math.log2(logn))
    bit_data.extend([0] * loglogn)
    bit_data.extend(int2ba(logn))
    bit_data.extend(int2ba(number))
    

def decode_number(bit_data: bitarray) -> int:
    first_bit = bit_data[0]
    # Small number
    if first_bit == 1:
        number_bits = bit_data[1:1+SMALL_NUMBER_BITS]
        del bit_data[:1+SMALL_NUMBER_BITS]
        return ba2int(number_bits)
    # Big number
    first_1_idx = bit_data.find(1)
    loglogn = first_1_idx
    logn_end_idx = first_1_idx + loglogn
    logn = ba2int(bit_data[first_1_idx: logn_end_idx])
    n_end_idx = logn_end_idx + logn
    num = ba2int(bit_data[logn_end_idx: n_end_idx])
    del bit_data[:n_end_idx]
    return num
