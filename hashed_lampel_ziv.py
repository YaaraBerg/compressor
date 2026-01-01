from typing import List, Tuple, Dict
from bitarray import bitarray


def hashed_lempel_ziv(data: bitarray, search_length: int, match_length: int, minimum_match_length: int, **kwargs) -> List[Tuple[int, int, bitarray]]:
    """
    Lempel-Ziv compression on a bitarray using hashed table

    Args:
        data (bitarray): The input binary data to be compressed
        search_length (int): The maximum length of the search buffer
        match_length (int): The maximum length of a matching substring
        minimum_match_length (int): The minimum match length to consider

    Returns:
        List[Tuple[int, int, bitarray]]: A list of tuples representing the compressed data.
        Each tuple contains (offset_bytes, length_bytes, next_byte_bits).
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
                        while (length < match_length and i + length < byte_count - 1 and
                               data[(j + length)*8:(j + length + 1)*8] == data[(i + length)*8:(i + length + 1)*8]):
                            length += 1

                        if length > best_length:
                            best_length = length
                            best_offset = i - j        # Update hash table with current position
        for start_pos in range(max(0, i - minimum_match_length + 1), i + 1):
            if start_pos + minimum_match_length <= byte_count:
                key = data[start_pos*8:(start_pos + minimum_match_length)*8].to01()

                if key not in hash_table:
                    hash_table[key] = []
                hash_table[key].append(start_pos)

        # Next byte after the match
        next_byte = data[(i + best_length)*8:(i + best_length + 1)*8]

        # Append the tuple (offset_bytes, length_bytes, next_byte_bits)
        result.append((best_offset, best_length, next_byte))

        # Move the index forward
        i += best_length + 1

    return result
