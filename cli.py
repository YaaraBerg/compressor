"""
Main CLI entry point
"""
import sys
from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from huffman_coding import huffman_encode, huffman_decode


def main():
    if len(sys.argv) != 4:
        print(f'Usage: {sys.argv[0]} encode/decode FILE RESULT')
        sys.exit(-1)
    operation = sys.argv[1]
    data_file = sys.argv[2]
    result_file = sys.argv[3]
    with open(data_file, 'rb') as f:
        data = bitarray(f.read())
    if operation == 'encode':
        # Try 4 methods
        try:
            enc_huff8 = huffman_encode(data, symbol_bits=8)
        except:
            enc_huff8 = None
        try:
            enc_huff16 = huffman_encode(data, symbol_bits=16)
        except:
            enc_huff16 = None
        enc_plain = data
        options = [enc_huff8, enc_huff16, enc_plain]
        best_index = min(range(3), key=lambda i: len(options[i]) if options[i] is not None else float('inf'))
        # index - 2 bits
        data_with_header = int2ba(best_index, 2) + options[best_index]
        with open(result_file, 'wb') as f:
            f.write(data_with_header)
    elif operation == 'decode':
        header = ba2int(data[:2])
        body = data[2:]
        if header == 0:
            decoded = huffman_decode(body, 8)
        elif header == 1:
            decoded = huffman_decode(body, 16)
        elif header == 2:
            decoded = body
        with open(result_file, 'wb') as f:
            f.write(decoded)
    else:
        print(f'Usage: {sys.argv[0]} encode/decode FILE RESULT')
        sys.exit(-1)

if __name__ == '__main__':
    main()
