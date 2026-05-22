# NilNovi Compiler - Wireless Network Signal Decoder

> 💡 **Note:** This project was originally developed in 2025 on a private school GitLab instance and has been migrated here to be made public.

A Python-based signal processing and decoding tool for extracting encrypted user data from wireless network communications using advanced modulation and forward error correction techniques.

## Overview

NilNovi Compiler is a specialized decoder designed to process complex wireless network signals transmitted over OFDM (Orthogonal Frequency-Division Multiplexing) channels. It implements multi-layered demodulation and decoding strategies to extract and decrypt user messages from encoded signal matrices.

The project demonstrates expertise in:
- **Signal Processing**: Complex matrix manipulation and signal extraction
- **Digital Modulation**: BPSK, QPSK, and QAM-16 demodulation
- **Error Correction**: Hamming(7,4) and convolutional coding decoding
- **Wireless Communications**: PBCH, PDCCH, and PDSCH channel processing
- **Data Security**: CRC validation and Caesar cipher decryption

## Project Structure

```
NilNovi-compiler/
├── reseauxsansfils/          # Main project directory
│   ├── main.py               # Core decoder logic
│   ├── imports.py            # Centralized module imports
│   ├── qam16_demod.py        # QAM-16 demodulation
│   ├── crc.py                # CRC polynomial generation and validation
│   ├── binary_transformation.py  # Bit-to-byte conversion & decryption
│   ├── tests_hamming.py      # Unit tests for Hamming decoding
│   ├── tests_modulation.py   # Unit tests for modulation schemes
│   ├── tfMatrix_*.csv        # Sample signal matrices (Time-Frequency domain)
│   ├── wirelessProject_topic.pdf # Project documentation
│   └── response.txt          # Decoded output results
```

## Key Features

### 1. Signal Decoding Pipeline
- **Time-Frequency Matrix Processing**: Loads and processes complex signal matrices from CSV files
- **OFDM Symbol Extraction**: Extracts specific subcarriers from OFDM signals
- **Multi-User Support**: Handles multiple concurrent users with individual data streams

### 2. Physical Channels
- **PBCH (Physical Broadcast Channel)**: Decodes cell and user count information
- **PDCCH (Physical Downlink Control Channel)**: Decodes per-user scheduling and modulation info
- **PDSCH (Physical Downlink Shared Channel)**: Decodes actual user payload data

### 3. Modulation Schemes
- **BPSK** (Binary Phase Shift Keying): 1 bit per symbol
- **QPSK** (Quadrature Phase Shift Keying): 2 bits per symbol
- **QAM-16** (16-Quadrature Amplitude Modulation): 4 bits per symbol

### 4. Error Correction Codes (FEC)
- **Hamming(7,4)**: Single error correction capability
- **Convolutional Codes**: Viterbi decoding for continuous bit streams
- **CRC**: Cyclic Redundancy Check validation (8, 16, 24, 32-bit)

### 5. Encryption
- **Caesar Cipher Decryption**: Per-user variable shift decryption
- **Binary-to-ASCII Conversion**: Message reconstruction and readability

## Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Dependencies Installation

```bash
cd reseauxsansfils

# Install required packages
pip install numpy
pip install matplotlib
pip install pytest
pip install scikit-dsp-comm
```

## Usage

### Basic Decoding

```python
# Run the main decoder
python main.py
```

This will:
1. Load the signal matrix from `tfMatrix_3.csv`
2. Extract and decode PBCH information (cell ID, number of users)
3. For each user:
   - Decode PDCCH (scheduling info, modulation scheme)
   - Decode PDSCH (user payload)
   - Validate with CRC
   - Decrypt message using Caesar cipher
4. Output extracted keys/messages to console and `Dic_key` dictionary

### Example Output

```
key is ABC123
user_ident: 1, message: "key is ABC123"
user_ident: 2, message: "key is XYZ789"

Dic_key = {
    1: 'ABC123',
    2: 'XYZ789'
}
```

## Core Functions

### Demodulation Functions

#### `bpsk_demod(qamSeq)`
Demodulates BPSK signals by thresholding the real component.
- **Input**: Complex signal sequence
- **Output**: Binary sequence [0, 1, ...]

#### `qpsk_demod(qamSeq)`
Demodulates QPSK signals based on real and imaginary quadrants.
- **Input**: Complex signal sequence  
- **Output**: Binary sequence [0, 0, 1, 1, ...]

#### `qam16_demod(qamSeq)` 
Demodulates QAM-16 signals (16 constellation points).
- **Input**: Complex signal sequence
- **Output**: Binary sequence (4 bits per symbol)

### Error Correction Functions

#### `hamming748_decode(seq)`
Decodes Hamming(7,4) encoded bit sequences with single error correction.
- **Input**: Bit sequence (groups of 8: 7 data + 1 parity)
- **Output**: Corrected 4-bit information bits
- **Capability**: Detects and corrects single bit errors

#### `PDSCH_fec(qamSeq, mcs)`
Applies appropriate FEC decoding based on Modulation and Coding Scheme.
- **Input**: Demodulated bits, MCS value
- **Output**: Decoded information bits
- **Supports**: Hamming(7,4) and convolutional coding

### CRC Validation

#### `PDSCH_crc(qamSeq, crcSize)`
Validates data integrity using CRC polynomial division.
- **Input**: Bit sequence, CRC check size
- **Output**: Boolean (True if valid, False if corrupted)
- **Sizes**: 8, 16, 24, or 32-bit CRC polynomials

### Channel Decoding Functions

#### `decode_pbchu()`
Extracts Physical Broadcast Channel information.
- Decodes cell ID and total number of users
- Processes individual user scheduling parameters

#### `PDCCHU_decode_from_user(user_ident)`
Decodes user-specific PDCCH information.
- **Input**: User identifier
- **Output**: Decoded PDCCH bits
- **Extracts**: MCS, symbol start, resource block allocation

#### `decode_PDSCHU(user_ident)`
Extracts and decodes user payload from PDSCH channel.
- **Input**: User identifier
- **Output**: Decoded and CRC-validated bits
- **Process**: Demodulation → FEC → CRC check

### Message Reconstruction

#### `PDSCHU_to_string(user_ident)`
Converts binary PDSCH payload to readable ASCII message.
- **Input**: User identifier
- **Process**: 
  1. Decode PDSCH bits
  2. Convert bits to bytes
  3. Apply Caesar cipher decryption (user-specific key)
  4. Convert to ASCII characters
- **Output**: Decrypted message string

#### `extract_key()`
Main orchestration function that processes all users and extracts their messages.
- Iterates through all users
- Handles per-user errors gracefully
- Populates `Dic_key` dictionary with results

## Data Structures

### `Dic_first_slot_PBCH`
Stores PBCH channel information:
```python
{
    "cell_user": int,      # Cell identifier
    "number_user": int     # Total number of users
}
```

### `Dic_info_user`
Stores per-user scheduling and modulation info:
```python
{
    ("user_ident", user_id): {
        "MCS_of_PDCCHU": int,          # PDCCH modulation scheme
        "Symb_start_of_PDCCHU": int,   # PDCCH symbol start position
        "RB_start_of_PDCCHU": int,     # Resource block start
        "HARQ_of_PDCCHU": int,         # HARQ process ID
        "MCS_of_PDSCHU": int,          # PDSCH modulation scheme
        "sym_start_PDSCHU": int,       # PDSCH symbol start
        "RB_start_PDSCHU": int,        # Resource block start
        "RB_size": int,                # Resource block size
        "CRC_flag": int                # CRC bits count
    }
}
```

### `Dic_key`
Final output dictionary containing decoded messages:
```python
{
    user_id: "decoded_message_string",
    ...
}
```

## Testing

### Unit Tests

```bash
# Run Hamming decoding tests
python tests_hamming.py

# Run modulation tests
python tests_modulation.py
```

### Test Coverage
- **Hamming Decoder**: Single error correction and detection
- **Modulation**: BPSK, QPSK, QAM-16 demodulation accuracy
- **CRC**: Polynomial generation and validation
- **Binary Conversion**: Bit-to-byte transformation

## Signal Processing Details

### OFDM Structure
- **Subcarriers**: 624 subcarriers per OFDM symbol
- **Useful Subcarriers**: 312 (centered within the 624)
- **Matrix Format**: Time-Frequency domain (rows = OFDM symbols, cols = subcarriers)

### Resource Allocation
- **Resource Block (RB)**: 12 consecutive subcarriers
- **Symbol Duration**: One OFDM symbol time slot
- **Channel Capacity**: Multiple simultaneous users on different RBs

### Channel Layering
1. **PBCH** (1.5 symbols, 48 bits initial): Cell identification
2. **PDCCH** (following symbols): Per-user scheduling
3. **PDSCH** (allocated resources): Per-user payload

## Performance Notes

### Computational Requirements
- Matrix loading and processing: O(n) where n = matrix size
- Per-user decoding: Linear in number of users
- FEC decoding (Viterbi): Exponential in constraint length (handled by library)

### Typical Processing
- Load time: <1 second for ~1000 symbols
- Full decoding (3-5 users): 2-5 seconds
- CRC validation: Negligible overhead

## Error Handling

The decoder implements robust error handling:
- **Single Bit Errors**: Automatically corrected by Hamming decoder
- **Double Bit Errors**: Detected but not corrected (raised as exception)
- **CRC Failures**: Exception raised, user data discarded
- **MCS Errors**: Unknown modulation schemes rejected safely

## File Formats

### Input CSV Files (tfMatrix_*.csv)
- **Format**: Semicolon-separated values
- **Structure**: Each row = OFDM symbol, columns = alternating real/imaginary parts
- **Encoding**: `[Re_0, Im_0, Re_1, Im_1, ..., Re_311, Im_311]`

### Output (response.txt)
- Decoded messages and extracted keys
- One result per line

## Limitations and Future Work

### Current Limitations
- Single PBCH/PDCCH region assumption
- Fixed subcarrier organization (624 carriers)
- Hardcoded Caesar cipher interleaver
- Limited to specific signal matrix formats

### Potential Enhancements
- Multi-PBCH region support
- Configurable OFDM parameters
- Dynamic encryption method detection
- Support for additional FEC codes (LDPC, Turbo)
- Real-time signal streaming
- GPU acceleration for large-scale processing

## References

### Standards & Algorithms
- **OFDM**: IEEE 802.11, 3GPP Specifications
- **Error Correction**: Hamming codes, Convolutional coding
- **CRC**: ITU-T polynomial standards
- **Modulation**: Digital Communication Theory (Proakis, Salehi)

### External Libraries
- **NumPy**: Numerical computing and matrix operations
- **Matplotlib**: Signal visualization
- **scikit-dsp-comm**: Digital signal processing and communications
- **pytest**: Unit testing framework

## License

[Specify your license here - e.g., MIT, GPL-3.0]

## Contact & Contribution

For questions, bug reports, or contributions, please contact the project maintainer or submit issues through the project repository.

---

**Project Name**: NilNovi Compiler  
**Version**: 1.0  
**Last Updated**: 2024  
**Status**: Active Development
