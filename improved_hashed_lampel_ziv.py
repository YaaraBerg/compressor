from typing import List, Tuple, Dict, Union
from bitarray import bitarray
from nat_encoder import encode_number, decode_number


def encoder_better_lempel_ziv(data: bitarray, **kwargs) -> bitarray:
    """
    Compresses a bitarray using Lempel-Ziv compression with nat encoder.
    """
    if len(data) == 0:
        return bitarray()

    lz_list = better_lempel_ziv(data, **kwargs)
    result = bitarray()
    for cur_tuple in lz_list:
        if len(cur_tuple) == 1:
            result.extend('0') # Indicate that this is a literal byte
            next_byte = cur_tuple[0]
            result.extend(next_byte)
        else:
            result.extend('1') # Indicate that this is a (offset, length) pair
            encode_number(result, cur_tuple[0])
            encode_number(result, cur_tuple[1])

    return result


def decoder_better_lempel_ziv(compressed_data: bitarray, **kwargs) -> bitarray:
    """
    Decompresses a bitarray that was compressed with the byte-level encoder function.
    """
    if len(compressed_data) == 0:
        return bitarray()

    lz_list = []
    data_copy = compressed_data.copy()
    while len(data_copy) > 0:
        flag = data_copy[0]
        del data_copy[0]
        if flag == 0:
            next_byte = data_copy[:8]
            del data_copy[:8]
            lz_list.append((next_byte,))
        else:
            offset = decode_number(data_copy)
            length = decode_number(data_copy)
            lz_list.append((offset, length))

    return better_convert_lampel_ziv_list_to_binarray(lz_list)


def better_lempel_ziv(data: bitarray, search_length: int, match_length: int, minimum_match_length: int, **kwargs) -> List[Union[Tuple[int, int], Tuple[bitarray]]]:
    """
    Lempel-Ziv compression on a bitarray using hashed table
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


def better_convert_lampel_ziv_list_to_binarray(lz_list: List[Union[Tuple[int, int], Tuple[bitarray]]]) -> bitarray:
    """
    Converts a list of Lempel-Ziv tuples back into a bitarray format
    """
    result = bitarray()

    for cur_tuple in lz_list:
        if len(cur_tuple) == 1:
            next_byte = cur_tuple[0]
            result.extend(next_byte)
        else:
            offset, length = cur_tuple
            current_byte_count = len(result) // 8
            for i in range(length):
                source_byte_index = current_byte_count - offset + i
                source_byte_bits = result[source_byte_index*8:(source_byte_index+1)*8]
                result.extend(source_byte_bits)

    return result
