
# Solana Wallet Checker

A modern and simple desktop utility for managing and checking Solana wallets with ease.

## Features

* Convert private keys to Solana wallet addresses
* Check wallet balances via Solana mainnet
* Clean and user-friendly interface
* Supports batch processing
* Error handling and real-time feedback

## Installation

1. Make sure Python 3.7 or higher is installed
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the app:

```bash
python solana_checker.py
```

2. The tool has two main functions:

   * **Convert Private Keys**: Load a `.txt` file containing base58-encoded private keys. Converts and shows corresponding public wallet addresses.
   * **Check Balances**: Load a `.txt` file with wallet addresses to check their SOL balances on the Solana mainnet.

## File Formats

* **Private Keys File**: Each line must contain a valid base58 private key (64 bytes when decoded)
* **Wallet Addresses File**: Each line must start with `wallet:` followed by a valid Solana address

## Security

* Your private keys are processed locally and are **never** sent anywhere.
* The tool can run offline (except for balance checking which requires internet connection to query Solana RPC).

## License

MIT License


