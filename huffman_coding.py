import heapq
from typing import Dict, Tuple, Optional
from bitarray import bitarray
from collections import Counter

LENGTH_FIELD_BITS = 17    # Store length in BYTES
TREE_SIZE_FIELD_BITS_BY_BIT_SIMBOL = {
    2: 6,
    4: 8,
    8: 12,
    16: 16,
    32: 20
}

class HuffmanNode:
    """Node class for building the Huffman tree"""
    def __init__(self, symbol: Optional[int] = None, frequency: int = 0,
                 left: Optional['HuffmanNode'] = None, right: Optional['HuffmanNode'] = None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other: 'HuffmanNode') -> bool:
        """Comparison for heap operations"""
        return self.frequency < other.frequency

    def is_leaf(self) -> bool:
        """Check if this is a leaf node (contains a symbol)"""
        return self.left is None and self.right is None


def build_frequency_table(data: bitarray, symbol_bits: int) -> Dict[int, int]:
    """
    Build frequency table for symbols in the input data.
    """
    if len(data) == 0:
        return {}

    frequency_counter = Counter()

    # Process data in chunks of symbol_bits
    for i in range(0, len(data), symbol_bits):
        symbol_chunk = data[i:i + symbol_bits]
        symbol_value = int(symbol_chunk.to01(), 2)
        frequency_counter[symbol_value] += 1

    return dict(frequency_counter)


def build_huffman_tree(frequency_table: Dict[int, int]) -> Optional[HuffmanNode]:
    """
    Build Huffman tree from frequency table.
    """
    if len(frequency_table) == 1:
        only_symbol = next(iter(frequency_table))
        only_node = HuffmanNode(symbol=only_symbol, frequency=frequency_table[only_symbol])
        return HuffmanNode(frequency=only_node.frequency, left=only_node)

    # Create a min-heap with leaf nodes
    heap = []
    for symbol, freq in frequency_table.items():
        node = HuffmanNode(symbol=symbol, frequency=freq)
        heapq.heappush(heap, node)

    while len(heap) > 1:
        # Get two nodes with the lowest frequency
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        # Create internal node
        merged_freq = left.frequency + right.frequency
        internal_node = HuffmanNode(frequency=merged_freq, left=left, right=right)

        heapq.heappush(heap, internal_node)

    return heap[0]  # tree root


def generate_symbol_translation(root: HuffmanNode) -> Dict[int, str]:
    """
    Generate symbol mapping from the huffman tree.
    """
    if root is None:
        return {}

    symbol_translation = {}

    def traverse(node: HuffmanNode, str_path: str = ""):
        if node.is_leaf():
            symbol_translation[node.symbol] = str_path if str_path else "0"
        else:
            if node.left:
                traverse(node.left, str_path + "0")
            if node.right:
                traverse(node.right, str_path + "1")

    traverse(root)
    return symbol_translation


def encode_huffman_tree(root: Optional[HuffmanNode], symbol_bits: int) -> bitarray:
    """
    Encode the Huffman tree into a bitarray recursively.
    Uses a simple format:
    - Internal node: bit 0
    - Leaf node: bit 1 followed by symbol_bits representing the symbol value
    """
    if root is None:
        return bitarray()

    result = bitarray()

    def encode_huffman_node(node: HuffmanNode):
        if node.is_leaf():
            result.append(1)  # Leaf marker
            symbol_bits_str = f'{node.symbol:0{symbol_bits}b}'  # Add the symbol as {symbol_bits} bits
            result.extend(bitarray(symbol_bits_str))
        else:
            result.append(0)  # Internal node marker
            if node.left:
                encode_huffman_node(node.left)
            if node.right:
                encode_huffman_node(node.right)

    encode_huffman_node(root)
    return result


def decode_huffman_tree(data: bitarray, symbol_bits: int) -> Optional[HuffmanNode]:
    """
    Decode the Huffman tree from a bitarray recursively.
    """
    if len(data) == 0:
        return None, 0

    def decode_huffman_node(pos: int) -> Tuple[Optional[HuffmanNode], int]:
        if len(data) == pos:
            return None, pos

        if data[pos] == 1:  # Leaf
            symbol_chunk = data[pos + 1:pos + 1 + symbol_bits]
            symbol = int(symbol_chunk.to01(), 2)
            return HuffmanNode(symbol=symbol), pos + 1 + symbol_bits
        else:  # Internal node
            left_node, new_pos = decode_huffman_node(pos + 1)
            right_node, final_pos = decode_huffman_node(new_pos)
            return HuffmanNode(left=left_node, right=right_node), final_pos

    root, _ = decode_huffman_node(0)
    return root


def huffman_encode(data: bitarray, symbol_bits: int) -> bitarray:
    """
    Encode data using Huffman coding with configurable symbol size.

    File format:
    [Tree_size: 16 bits][Tree_data][Original_length_bytes: 17 bits][Encoded_data]
    """
    if len(data) == 0:
        return bitarray()

    freq_table = build_frequency_table(data, symbol_bits)
    result, symbol_translation = tree_size_and_structure_encode(freq_table, symbol_bits)

    # Store original data length in BYTES
    original_length_bytes = len(data) // 8
    result.extend(bitarray(f'{original_length_bytes:0{LENGTH_FIELD_BITS}b}'))

    # Encode the data
    for i in range(0, len(data), symbol_bits):
        symbol_chunk = data[i:i + symbol_bits]
        symbol_value = int(symbol_chunk.to01(), 2)
        result.extend(bitarray(symbol_translation[symbol_value]))

    return result


def tree_size_and_structure_encode(freq_table: Dict[int, int], symbol_bits: int) -> Tuple[bitarray, Dict[int, str]]:
    """
    Return the encoded tree size and structure along with symbol translation.
    """
    tree_size_field_bits = TREE_SIZE_FIELD_BITS_BY_BIT_SIMBOL[symbol_bits]
    tree_root = build_huffman_tree(freq_table)
    symbol_translation = generate_symbol_translation(tree_root)
    result = bitarray()

    # encode the tree (calc the tree size and insert in the header)
    encoded_tree = encode_huffman_tree(tree_root, symbol_bits)
    tree_size = len(encoded_tree)
    if tree_size >= (1 << tree_size_field_bits):
        raise ValueError(f"Tree too large: {tree_size} bits")
    result.extend(bitarray(f'{tree_size:0{tree_size_field_bits}b}'))
    result.extend(encoded_tree)
    return result, symbol_translation


def decode_symbols_from_tree(encoded_data: bitarray, tree_root: HuffmanNode,
                             symbol_bits: int, original_length_bits: int) -> bitarray:
    """
    Decode symbols from encoded data using the huffman tree.
    """
    result = bitarray()
    current_node = tree_root

    for bit in encoded_data:
        if bit == 0 and current_node.left:
            current_node = current_node.left
        elif bit == 1 and current_node.right:
            current_node = current_node.right

        if current_node.is_leaf():
            symbol_bits_str = f'{current_node.symbol:0{symbol_bits}b}'
            result.extend(bitarray(symbol_bits_str))
            current_node = tree_root  # Reset to root

            if len(result) >= original_length_bits:
                break

    return result


def huffman_decode(compressed_data: bitarray, symbol_bits: int) -> bitarray:
    """
    Decode Huffman-encoded data with configurable symbol size.
    """
    if len(compressed_data) == 0:
        return bitarray()

    # Read tree size and decode tree
    tree_size_bits = compressed_data[:TREE_SIZE_FIELD_BITS_BY_BIT_SIMBOL[symbol_bits]]
    tree_size = int(tree_size_bits.to01(), 2)
    tree_start = TREE_SIZE_FIELD_BITS_BY_BIT_SIMBOL[symbol_bits]
    tree_end = tree_start + tree_size
    tree_data = compressed_data[tree_start:tree_end]
    tree_root = decode_huffman_tree(tree_data, symbol_bits)

    # Read original data length in BYTES
    original_length_bits_field = compressed_data[tree_end:tree_end + LENGTH_FIELD_BITS]
    original_length_bytes = int(original_length_bits_field.to01(), 2)
    original_length_bits = original_length_bytes * 8

    # Decode the compressed content
    encoded_data = compressed_data[tree_end + LENGTH_FIELD_BITS:]
    result = decode_symbols_from_tree(encoded_data, tree_root, symbol_bits, original_length_bits)

    return result[:original_length_bits]
