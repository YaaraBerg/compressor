import os
import time
import csv
from datetime import datetime
from bitarray import bitarray
from lampel_ziv import basic_lempel_ziv, convert_lampel_ziv_list_to_binarray
from nat_encoder import encode_number, decode_number

# PAY ATTENTION: add new config keys at the end of this list
ALL_CONFIG_KEYS = ['run_name', 'method', 'notes', 'search_length', 'match_length']

CONFIG = {
    'run_name': 'basic search 256 back with match 32',
    'method': 'basic_lempel_ziv',
    'search_length': 256,
    'match_length': 32,
    'notes': '',
}

RESULT_KEYS = ['run_id', 'filename', 'encode_time', 'decode_time', 'original_bits', 'compressed_bits']

SAVE_COMPRESSED = False  # Set to True if you want to save the decoded files


def main() -> None:
    # Generate unique run ID based on timestamp
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save configuration for this run
    save_config(run_id, CONFIG)

    # List of sample files to process
    sample_files = ["Samp1.bin", "Samp2.bin", "Samp3.bin", "Samp4.bin"]

    results = []

    for filename in sample_files:
        if os.path.exists(filename):
            print(f"Processing {filename}...")

            # Read original file and convert to bitarray
            with open(filename, 'rb') as f:
                original_data = f.read()

            original_bitarray = bitarray()
            original_bitarray.frombytes(original_data)
            original_bits = len(original_bitarray)

            # Time the encoding process
            start_time = time.time()
            compressed_bitarray = encoder(original_bitarray)
            encode_time = time.time() - start_time
            compressed_bits = len(compressed_bitarray)

            # Time the decoding process
            start_time = time.time()
            decoded_bitarray = decoder(compressed_bitarray)
            decode_time = time.time() - start_time

            # Verify that decoder(encoder(X)) = X
            assert original_bitarray == decoded_bitarray, f"Assertion failed for {filename}: decoder(encoder(X)) != X"

            # Optional: Save compressed and decoded files for inspection
            if SAVE_COMPRESSED:
                output_filename = f"compressed_{filename}"
                decoded_filename = f"decoded_{filename}"

                with open(output_filename, 'wb') as f:
                    f.write(compressed_bitarray.tobytes())

                with open(decoded_filename, 'wb') as f:
                    f.write(decoded_bitarray.tobytes())

            # Store results
            result = {
                'run_id': run_id,
                'filename': filename,
                'encode_time': encode_time,
                'decode_time': decode_time,
                'original_bits': original_bits,
                'compressed_bits': compressed_bits
            }
            results.append(result)

            print(f"  Encoded in {encode_time:.4f}s, decoded in {decode_time:.4f}s")
            print(f"  Original: {original_bits} bits, Compressed: {compressed_bits} bits")

    # Save results
    save_results(results)
    print(f"\nRun {run_id} completed. Results saved to results.csv and configs.csv")


def encoder(data: bitarray) -> bitarray:
    """
    Compresses a bitarray using Lempel-Ziv compression with nat encoder.

    Args:
        data (bitarray): The input binary data to compress.

    Returns:
        bitarray: The compressed binary data.
    """
    if len(data) == 0:
        return bitarray()

    lz_list = basic_lempel_ziv(data, **CONFIG)
    result = bitarray()
    for offset, length, next_symbol in lz_list:
        encode_number(result, offset)
        encode_number(result, length)
        result.append(next_symbol)

    return result


def decoder(compressed_data: bitarray) -> bitarray:
    """
    Decompresses a bitarray that was compressed with the encoder function.

    Args:
        compressed_data (bitarray): The compressed binary data.

    Returns:
        bitarray: The decompressed (original) binary data.
    """
    if len(compressed_data) == 0:
        return bitarray()

    lz_list = []
    data_copy = compressed_data.copy()
    while len(data_copy) > 0:
        offset = decode_number(data_copy)
        length = decode_number(data_copy)
        next_symbol = int(data_copy[0])
        del data_copy[0]
        lz_list.append((offset, length, next_symbol))

    return convert_lampel_ziv_list_to_binarray(lz_list)


def save_config(run_id: str, config: dict) -> None:
    """Save configuration details for this run to configs.csv"""
    config_file = 'configs.csv'

    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(config_file)

    with open(config_file, 'a', newline='') as csvfile:
        fieldnames = ['run_id', 'timestamp'] + ALL_CONFIG_KEYS
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header if file is new
        if not file_exists:
            writer.writeheader()

        # Create row with all fields (missing ones will be empty)
        row = {'run_id': run_id, 'timestamp': datetime.now().isoformat()}
        for key in ALL_CONFIG_KEYS:
            row[key] = config.get(key, '')  # Empty string if key not present
        writer.writerow(row)


def save_results(results: list) -> None:
    """Save performance results to results.csv"""
    results_file = 'results.csv'

    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(results_file)

    with open(results_file, 'a', newline='') as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=RESULT_KEYS)

        # Write header if file is new
        if not file_exists:
            writer.writeheader()

        # Write all results for this run
        for result in results:
            writer.writerow(result)


if __name__ == "__main__":
    main()
