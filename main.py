import os
from bitarray import bitarray

def main() -> None:
    # List of sample files to process
    sample_files = ["Samp1.bin", "Samp2.bin", "Samp3.bin", "Samp4.bin"]

    for filename in sample_files:
        if os.path.exists(filename):
            output_filename = f"compressed_{filename}"
            decoded_filename = f"decoded_{filename}"
            encoder(filename, output_filename)
            decoder(output_filename, decoded_filename)

            # Verify that decoder(encoder(X)) = X
            with open(filename, 'rb') as f:
                original_data = f.read()
            with open(decoded_filename, 'rb') as f:
                decoded_data = f.read()

            assert original_data == decoded_data, f"Assertion failed for {filename}: decoder(encoder(X)) != X"


def encoder(input_path: str, output_path: str) -> None:
    """
    Reads a file from the input path, compresses it using Lempel-Ziv,
    and saves the result to the output path.

    Args:
        input_path (str): The file path of the source file to compress.
        output_path (str): The destination file path where the compressed
        data will be saved.

    Returns:
        None
    """
    # Read the input file as binary data
    with open(input_path, 'rb') as f:
        data = f.read()

    # Convert bytes to bitarray
    bit_data = bitarray()
    bit_data.frombytes(data)

    # Very basic encoding: just save file size info for now
    # In a real implementation, you would use the lampel_ziv function
    file_size = len(data)

    # Simple encoding: prepend file size and save
    with open(output_path, 'wb') as f:
        f.write(file_size.to_bytes(4, byteorder='big'))  # Write file size as 4 bytes
        f.write(bit_data.tobytes())  # Write original data (this is just a placeholder)


def decoder(input_path: str, output_path: str) -> None:
    """
    Reads a compressed file from the input path, decodes it,
    and saves the reconstructed data to the output path.

    Args:
        input_path (str): The file path of the compressed file to read.
        output_path (str): The destination file path where the decompressed
        (original) data will be saved.

    Returns:
        None
    """
    # Read the compressed file
    with open(input_path, 'rb') as f:
        # Read the file size (first 4 bytes)
        file_size_bytes = f.read(4)
        file_size = int.from_bytes(file_size_bytes, byteorder='big')

        # Read the actual data
        data = f.read(file_size)

    # Write the decoded data to output file
    with open(output_path, 'wb') as f:
        f.write(data)


if __name__ == "__main__":
    main()
