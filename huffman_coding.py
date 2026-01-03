import heapq
from typing import Dict, List, Tuple, Optional
from bitarray import bitarray
from collections import Counter

LENGTH_FIELD_BITS = 17    # Store length in BYTES
TREE_SIZE_FIELD_BITS = 16 # Tree size in bits: 2^16 = 64KB max tree # TODO maybe we can lower it
SYMBOL_BITS_FIELD = 6     # Symbol size: 2^6 = 64 max (covers 1-32 bit symbols)  
# TODO SYMBOL_BITS_FIELD only relevant if we want to run more than one param in the algo!

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


def build_frequency_table(data: bitarray, symbol_bits: int = 8) -> Dict[int, int]:
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
    # Create a min-heap with leaf nodes
    heap = []
    for symbol, freq in frequency_table.items():
        node = HuffmanNode(symbol=symbol, frequency=freq)
        heapq.heappush(heap, node)

    # Build the tree bottom-up
    while len(heap) > 1:
        # Get two nodes with the lowest frequency
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        # Create internal node
        merged_freq = left.frequency + right.frequency
        internal_node = HuffmanNode(frequency=merged_freq, left=left, right=right)

        heapq.heappush(heap, internal_node)

    return heap[0]  # tree root


def generate_huffman_codes(root: HuffmanNode) -> Dict[int, str]:
    """
    Generate Huffman codes from the tree.
    """
    if root is None:
        return {}

    codes = {}

    def traverse(node: HuffmanNode, code: str = ""):
        if node.is_leaf():
            codes[node.symbol] = code if code else "0"
        else:
            if node.left:
                traverse(node.left, code + "0")
            if node.right:
                traverse(node.right, code + "1")

    traverse(root)
    return codes


def serialize_tree(root: Optional[HuffmanNode], symbol_bits: int = 8) -> bitarray:
    """
    Serialize the Huffman tree to a bitarray for storage.
    Uses a simple format:
    - Internal node: bit 0
    - Leaf node: bit 1 followed by symbol_bits representing the symbol value
    """
    if root is None:
        return bitarray()

    result = bitarray()

    def serialize_node(node: HuffmanNode):
        if node.is_leaf():
            result.append(1)  # Leaf marker
            symbol_bits_str = f'{node.symbol:0{symbol_bits}b}'  # Add the symbol as {symbol_bits} bits
            result.extend(bitarray(symbol_bits_str))
        else:
            result.append(0)  # Internal node marker
            if node.left:
                serialize_node(node.left)
            if node.right:
                serialize_node(node.right)

    serialize_node(root)
    return result


def deserialize_tree(data: bitarray, symbol_bits: int = 8) -> Tuple[Optional[HuffmanNode], int]:
    """
    Deserialize a Huffman tree from a bitarray.
    """
    if len(data) == 0:
        return None, 0

    def deserialize_node(pos: int) -> Tuple[HuffmanNode, int]:

        if data[pos]:  # Leaf
            symbol_chunk = data[pos + 1:pos + 1 + symbol_bits]
            symbol = int(symbol_chunk.to01(), 2)
            return HuffmanNode(symbol=symbol), pos + 1 + symbol_bits
        else:  # Internal node
            left_node, new_pos = deserialize_node(pos + 1)
            right_node, final_pos = deserialize_node(new_pos)
            return HuffmanNode(left=left_node, right=right_node), final_pos

    root, consumed = deserialize_node(0)
    return root, consumed


def huffman_encode(data: bitarray, symbol_bits: int = 8) -> bitarray:
    """
    Encode data using Huffman coding with configurable symbol size.

    File format:
    [Symbol_bits: 8 bits][Tree_size: 24 bits][Tree_data][Original_length_bytes: 20 bits][Encoded_data]
    """
    if len(data) == 0:
        return bitarray()

    freq_table = build_frequency_table(data, symbol_bits)
    tree_root = build_huffman_tree(freq_table)
    codes = generate_huffman_codes(tree_root)
    result = bitarray()

    # Store symbol_bits
    result.extend(bitarray(f'{symbol_bits:0{SYMBOL_BITS_FIELD}b}'))

    # Serialize the tree (calc the tree size and insert in the header)
    serialized_tree = serialize_tree(tree_root, symbol_bits)
    tree_size = len(serialized_tree)
    if tree_size >= (1 << TREE_SIZE_FIELD_BITS):
        raise ValueError(f"Tree too large: {tree_size} bits")
    result.extend(bitarray(f'{tree_size:0{TREE_SIZE_FIELD_BITS}b}'))
    result.extend(serialized_tree)

    # Store original data length in BYTES
    original_length_bytes = len(data) // 8
    result.extend(bitarray(f'{original_length_bytes:0{LENGTH_FIELD_BITS}b}'))

    # Encode the data
    for i in range(0, len(data), symbol_bits):
        symbol_chunk = data[i:i + symbol_bits]
        symbol_value = int(symbol_chunk.to01(), 2)
        if symbol_value in codes:
            result.extend(bitarray(codes[symbol_value]))

    return result


def huffman_decode(compressed_data: bitarray) -> bitarray:
    """
    Decode Huffman-encoded data with configurable symbol size.
    """
    if len(compressed_data) == 0:
        return bitarray()

    # read symbol_bits param
    symbol_bits_data = compressed_data[:SYMBOL_BITS_FIELD]
    symbol_bits = int(symbol_bits_data.to01(), 2)

    # Read tree size and serialized tree
    tree_size_bits = compressed_data[SYMBOL_BITS_FIELD:SYMBOL_BITS_FIELD + TREE_SIZE_FIELD_BITS]
    tree_size = int(tree_size_bits.to01(), 2)
    tree_start = SYMBOL_BITS_FIELD + TREE_SIZE_FIELD_BITS
    tree_end = tree_start + tree_size
    tree_data = compressed_data[tree_start:tree_end]
    tree_root, _ = deserialize_tree(tree_data, symbol_bits)

    # Read original data length in BYTES
    original_length_bits_field = compressed_data[tree_end:tree_end + LENGTH_FIELD_BITS]
    original_length_bytes = int(original_length_bits_field.to01(), 2)
    original_length_bits = original_length_bytes * 8

    # Decode the compressed content
    encoded_data = compressed_data[tree_end + LENGTH_FIELD_BITS:]

    if tree_root is None:
        return bitarray()

    # Decode using the tree
    result = bitarray()
    current_node = tree_root

    for bit in encoded_data:
        # Traverse the tree
        if bit == 0 and current_node.left:
            current_node = current_node.left
        elif bit == 1 and current_node.right:
            current_node = current_node.right

        # Check if we reached a leaf
        if current_node.is_leaf():
            symbol_bits_str = f'{current_node.symbol:0{symbol_bits}b}'
            result.extend(bitarray(symbol_bits_str))
            current_node = tree_root  # Reset to root

            # Stop if we've decoded enough bits
            if len(result) >= original_length_bits:
                break

    return result[:original_length_bits]
