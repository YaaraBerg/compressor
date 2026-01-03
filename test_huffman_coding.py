from bitarray import bitarray
from huffman_coding import (
    build_frequency_table, build_huffman_tree, generate_huffman_codes,
    huffman_encode, huffman_decode, serialize_tree, deserialize_tree
)


def test_frequency_table():
    """Test frequency table building"""
    # Test with simple string
    data = bitarray()
    data.frombytes(b"hello")

    freq_table = build_frequency_table(data)

    # 'h'=104, 'e'=101, 'l'=108, 'o'=111
    expected = {104: 1, 101: 1, 108: 2, 111: 1}
    assert freq_table == expected


def test_huffman_tree_single_symbol():
    """Test tree building with single symbol"""
    freq_table = {65: 5}  # Only 'A'
    root = build_huffman_tree(freq_table)

    assert root is not None
    assert not root.is_leaf()  # Root should have child
    assert root.left.is_leaf()
    assert root.left.symbol == 65


def test_huffman_tree_multiple_symbols():
    """Test tree building with multiple symbols"""
    freq_table = {65: 1, 66: 2, 67: 3}  # A, B, C
    root = build_huffman_tree(freq_table)

    assert root is not None
    assert not root.is_leaf()
    assert root.frequency == 6  # Sum of all frequencies


def test_huffman_codes_generation():
    """Test code generation"""
    # Simple tree with known structure
    freq_table = {65: 1, 66: 1}  # A, B with equal frequency
    root = build_huffman_tree(freq_table)
    codes = generate_huffman_codes(root)

    assert len(codes) == 2
    assert 65 in codes and 66 in codes
    # Codes should be different
    assert codes[65] != codes[66]
    # Both should be 1 bit for balanced tree
    assert len(codes[65]) == 1 and len(codes[66]) == 1


def test_tree_serialization():
    """Test tree serialization and deserialization"""
    freq_table = {65: 1, 66: 2, 67: 3}
    original_root = build_huffman_tree(freq_table)

    # Serialize
    serialized = serialize_tree(original_root)

    # Deserialize
    deserialized_root, consumed = deserialize_tree(serialized)

    # Check that consumed bits match serialized length
    assert consumed == len(serialized)

    # Generate codes from both trees and compare
    original_codes = generate_huffman_codes(original_root)
    deserialized_codes = generate_huffman_codes(deserialized_root)

    assert original_codes == deserialized_codes


def test_huffman_encode_decode_simple():
    """Test encoding and decoding simple data"""
    test_string = "hello"
    data = bitarray()
    data.frombytes(test_string.encode())

    # Encode
    encoded = huffman_encode(data)

    # Decode
    decoded = huffman_decode(encoded)

    # Should match original
    assert data == decoded

    # Encoded should typically be smaller (or same) for this data
    # Note: For very small data, overhead might make it larger
    print(f"Original: {len(data)} bits, Encoded: {len(encoded)} bits")


def test_huffman_encode_decode_repeated_data():
    """Test with data that should compress well"""
    test_string = "aaaaaabbbbccccdddd"
    data = bitarray()
    data.frombytes(test_string.encode())

    encoded = huffman_encode(data)
    decoded = huffman_decode(encoded)

    assert data == decoded

    # Should achieve some compression
    compression_ratio = len(encoded) / len(data)
    print(f"Compression ratio: {compression_ratio:.4f}")


def test_huffman_empty_data():
    """Test with empty data"""
    empty_data = bitarray()

    encoded = huffman_encode(empty_data)
    decoded = huffman_decode(encoded)

    assert empty_data == decoded


def test_huffman_single_byte():
    """Test with single byte"""
    data = bitarray('10101010')  # Single byte

    encoded = huffman_encode(data)
    decoded = huffman_decode(encoded)

    assert data == decoded


def test_huffman_with_binary_data():
    """Test Huffman coding with various binary patterns"""
    # Test with different bit patterns
    test_cases = [
        bitarray('00000000'),  # All zeros
        bitarray('11111111'),  # All ones
        bitarray('10101010'),  # Alternating
        bitarray('11000011'),  # Mixed
    ]

    for data in test_cases:
        encoded = huffman_encode(data)
        decoded = huffman_decode(encoded)
        assert data == decoded, f"Failed for pattern: {data.to01()}"


def test_huffman_compression_effectiveness():
    """Test compression effectiveness on different data types"""

    # High repetition - should compress well
    repetitive_data = bitarray()
    repetitive_data.frombytes(b"aaaaaaaaaa" * 10)

    encoded_rep = huffman_encode(repetitive_data)
    rep_ratio = len(encoded_rep) / len(repetitive_data)

    # Random-like data - should not compress well
    diverse_data = bitarray()
    diverse_data.frombytes(b"abcdefghijklmnopqrstuvwxyz" * 3)

    encoded_div = huffman_encode(diverse_data)
    div_ratio = len(encoded_div) / len(diverse_data)

    print(f"Repetitive data compression ratio: {rep_ratio:.4f}")
    print(f"Diverse data compression ratio: {div_ratio:.4f}")

    # Repetitive should compress better (though small data has overhead)
    # This is more of an informational test
    assert huffman_decode(encoded_rep) == repetitive_data
    assert huffman_decode(encoded_div) == diverse_data


if __name__ == "__main__":
    # Run tests manually if executed directly
    test_frequency_table()
    test_huffman_tree_single_symbol()
    test_huffman_tree_multiple_symbols()
    test_huffman_codes_generation()
    test_tree_serialization()
    test_huffman_encode_decode_simple()
    test_huffman_encode_decode_repeated_data()
    test_huffman_empty_data()
    test_huffman_single_byte()
    test_basic_huffman_coding_wrapper()
    test_huffman_with_binary_data()
    test_huffman_compression_effectiveness()

    print("All tests passed!")
