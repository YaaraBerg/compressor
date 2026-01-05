from typing import List, Tuple, Dict, Union
from bitarray import bitarray
from bitarray.util import ba2int
from nat_encoder import encode_number, decode_number
from huffman_coding import tree_size_and_structure_encode, decode_huffman_tree

TREE_SIZE_FIELD = 12


def dynamic_lempel_ziv_encoder(data: bitarray, **kwargs) -> bitarray:
    """
    Compresses a bitarray using an improved version of Lempel-Ziv compression with nat encoder.
    """
    if len(data) == 0:
        return bitarray()

    lz_list = dynamic_lempel_ziv(data, **kwargs)
    result, symbol_translation = encode_huffman_tree_from_dynamic_lz_list(lz_list, symbol_bits=8)
    for cur_tuple in lz_list:
        if len(cur_tuple) == 1:
            result.extend('0') # Indicate that this is a literal byte
            next_byte = cur_tuple[0]
            result.extend(symbol_translation[ba2int(next_byte)])
        else:
            result.extend('1') # Indicate that this is a (offset, length) pair
            encode_number(result, cur_tuple[0])
            encode_number(result, cur_tuple[1])

    return result


def dynamic_lempel_ziv_decoder(compressed_data: bitarray, **kwargs) -> bitarray:
    """
    Decompresses a bitarray that was compressed with the byte-level encoder function.
    """
    if len(compressed_data) == 0:
        return bitarray()

    lz_list = []
    data_copy = compressed_data.copy()
    
    tree_size_bits = compressed_data[:TREE_SIZE_FIELD]
    tree_size = int(tree_size_bits.to01(), 2)
    tree_start = TREE_SIZE_FIELD
    tree_end = tree_start + tree_size
    tree_data = data_copy[tree_start:tree_end]
    root = decode_huffman_tree(tree_data, symbol_bits=8)
    del data_copy[:tree_end]
    
    while len(data_copy) > 0:
        if len(data_copy) == 0:
            break
            
        flag = data_copy[0]
        del data_copy[:1]
        
        if flag == 0:  # only symbol
            current_node = root
            bits_consumed = 0
            
            # traverse tree
            for i in range(len(data_copy)):
                bit = data_copy[i]
                if bit == 0 and current_node.left:
                    current_node = current_node.left
                elif bit == 1 and current_node.right:
                    current_node = current_node.right
                
                bits_consumed += 1
                
                if current_node.is_leaf():
                    symbol_bits_str = f'{current_node.symbol:0{8}b}'
                    symbol_bitarray = bitarray(symbol_bits_str)
                    lz_list.append((symbol_bitarray,))
                    del data_copy[:bits_consumed]
                    break
        else:  # (offset, length) pair
            offset = decode_number(data_copy)
            length = decode_number(data_copy)
            lz_list.append((offset, length))

    return reverse_dynamic_lempel_ziv(lz_list)


def dynamic_lempel_ziv(data: bitarray, search_length: int, match_length: int, minimum_match_length: int, **kwargs) \
        -> List[Union[Tuple[int, int], Tuple[bitarray]]]:
    """
    The Lempel-Ziv tuples are stored as either (offset, length) pairs or literal bytes.
    Uses a hash table to find matches efficiently.
    """
    byte_count = len(data) // 8
    result = []
    i = 0
    hash_table: Dict[str, List[int]] = {}

    while i < byte_count:
        best_offset = 0
        best_length = 0

        # Build hash key for minimum_match_length bytes starting at position i
        if i + minimum_match_length <= byte_count:
            hash_key = data[i*8:(i + minimum_match_length)*8].to01()

            # Look for matches using hash table
            if hash_key in hash_table:
                for j in hash_table[hash_key]:
                    if j >= max(0, i - search_length) and j < i:
                        length = 0
                        while (length < match_length and i + length < byte_count and
                               data[(j + length)*8:(j + length + 1)*8] == data[(i + length)*8:(i + length + 1)*8]):
                            length += 1

                        if length >= best_length: # Prefer later matches (for shorter offset)
                            best_length = length
                            best_offset = i - j        # Update hash table with current position

        for start_pos in range(max(0, i - minimum_match_length + 1), i + 1):
            if start_pos + minimum_match_length <= byte_count:
                key = data[start_pos*8:(start_pos + minimum_match_length)*8].to01()

                if key not in hash_table:
                    hash_table[key] = []
                hash_table[key].append(start_pos)


        if best_length > 0:
            result.append((best_offset, best_length))
            i += best_length
        else:
            next_byte = data[(i + best_length)*8:(i + best_length + 1)*8]
            result.append((next_byte,))
            i += 1

    return result


def reverse_dynamic_lempel_ziv(lz_list: List[Union[Tuple[int, int], Tuple[bitarray]]]) -> bitarray:
    """
    Converts a list of Lempel-Ziv tuples back into a bitarray format
    """
    result = bitarray()

    for cur_tuple in lz_list:
        if len(cur_tuple) == 1:
            next_byte = cur_tuple[0]
            result.extend(bitarray(next_byte))
        else:
            offset, length = cur_tuple
            current_byte_count = len(result) // 8
            for i in range(length):
                source_byte_index = current_byte_count - offset + i
                source_byte_bits = result[source_byte_index*8:(source_byte_index+1)*8]
                result.extend(source_byte_bits)

    return result

def build_frequency_table_from_symbols_list(symbols_list: List[bitarray], symbol_bits: int) -> Dict[int, int]:
    """
    Build a frequency table from a list of symbols represented as bitarrays.
    """
    freq_table: Dict[int, int] = {}

    for symbol_bits_array in symbols_list:
        if len(symbol_bits_array) != symbol_bits:
            raise ValueError(f"Symbol length mismatch: expected {symbol_bits}, got {len(symbol_bits_array)}")
        symbol_value = int(symbol_bits_array.to01(), 2)
        if symbol_value not in freq_table:
            freq_table[symbol_value] = 0
        freq_table[symbol_value] += 1

    return freq_table


def encode_huffman_tree_from_dynamic_lz_list(lz_list: List[Union[Tuple[int, int], Tuple[bitarray]]], symbol_bits: int) \
        -> Tuple[bitarray, Dict[int, str]]:
    """
    Encode a Huffman tree from a dynamic Lempel-Ziv list (only for the synbols).
    """
    symbols_list = [cur_tuple[0] for cur_tuple in lz_list if len(cur_tuple) == 1]
    freq_table = build_frequency_table_from_symbols_list(symbols_list, symbol_bits)
    return tree_size_and_structure_encode(freq_table, symbol_bits)
