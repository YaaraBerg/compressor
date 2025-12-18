import os
import time
import csv
from datetime import datetime
from bitarray import bitarray

# Define ALL possible config keys you might use across different experiments
# Add new keys here as you introduce new parameters
ALL_CONFIG_KEYS = ['run_name', 'method', 'notes']

RESULT_KEYS = ['run_id', 'filename', 'encode_time', 'decode_time', 'original_bits', 'compressed_bits']

# Configuration flags
SAVE_COMPRESSED = False  # Set to True if you want to save compressed/decoded files

CONFIG = {
    'run_name': 'empty_test',
    'method': 'read_write',
    'notes': 'check the runner functionality',
}


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
    Compresses a bitarray using Lempel-Ziv compression.

    Args:
        data (bitarray): The input binary data to compress.

    Returns:
        bitarray: The compressed binary data.
    """
    # Very basic encoding: just return the original data for now
    # In a real implementation, you would use the lampel_ziv function
    # from lampel_ziv import convert_binarray_to_lampel_ziv_list
    # lz_list = convert_binarray_to_lampel_ziv_list(data, search_length=CONFIG.get('search_length', 1))
    # Then encode the lz_list to bitarray using nat_encoder

    # Placeholder: return original data (no compression)
    return data.copy()


def decoder(compressed_data: bitarray) -> bitarray:
    """
    Decompresses a bitarray that was compressed with the encoder function.

    Args:
        compressed_data (bitarray): The compressed binary data.

    Returns:
        bitarray: The decompressed (original) binary data.
    """
    # Very basic decoding: just return the compressed data for now
    # In a real implementation, you would decode the nat_encoder data back to lz_list
    # Then use convert_lampel_ziv_list_to_binarray to reconstruct

    # Placeholder: return the data as-is (no decompression)
    return compressed_data.copy()


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
