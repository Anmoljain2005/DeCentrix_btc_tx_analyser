# Bitcoin Scripting Assignment

This repository contains the code and instructions for the Bitcoin Scripting Assignment, which involves creating and validating Bitcoin transactions using Legacy (P2PKH) and SegWit (P2SH-P2WPKH) address formats. The project is implemented in Python and interacts with the Bitcoin Core (`bitcoind`) using RPC calls.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setting Up Bitcoin Core](#setting-up-bitcoin-core)
3. [Configuring `bitcoin.conf`](#configuring-bitcoinconf)
4. [Running Bitcoin Core in Regtest Mode](#running-bitcoin-core-in-regtest-mode)
5. [Running the Scripts](#running-the-scripts)
6. [Script Descriptions](#script-descriptions)
7. [Report and Analysis](#report-and-analysis)
8. [Acknowledgements](#acknowledgements)

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Bitcoin Core**: Download and install Bitcoin Core from [bitcoincore.org](https://bitcoincore.org/).
- **Python 3**: Ensure Python 3 is installed on your system.
- **Python Libraries**: Install the required Python libraries using pip:
  ```bash
  pip install python-bitcoinrpc
  ```

---

## Setting Up Bitcoin Core

1. **Download Bitcoin Core**: 
   - Visit [bitcoincore.org](https://bitcoincore.org/) and download the latest version of Bitcoin Core for your operating system.
   - Follow the installation instructions for your OS.

2. **Install Bitcoin Core**:
   - After installation, ensure that `bitcoind` (Bitcoin Daemon) and `bitcoin-cli` (Bitcoin Command Line Interface) are available in your system's PATH.

---

## Configuring `bitcoin.conf`

To run Bitcoin Core in regtest mode, you need to configure the `bitcoin.conf` file. This file is usually located in the Bitcoin data directory.

1. **Locate the Bitcoin Data Directory**:
   - **Linux**: `~/.bitcoin/`
   - **macOS**: `~/Library/Application Support/Bitcoin/`
   - **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\Bitcoin\`

2. **Create or Edit `bitcoin.conf`**:
   - Create a file named `bitcoin.conf` in the Bitcoin data directory if it doesn't exist.
   - Add the following configuration to the file:

   ```ini
regtest
rpcuser=decentrix_crew
rpcpassword=decentrix
rpcport=18443
server=1
txindex=1
paytxfee=0.0001
fallbackfee=0.0002
mintxfee=0.00001
txconfirmtarget=6
   ```

   - **Explanation**:
     - `[regtest]`: Enables regtest mode (local blockchain for testing).
     - `server=1`: Allows RPC connections.
     - `rpcuser` and `rpcpassword`: Credentials for RPC authentication.
     - `rpcport=18443`: Port for RPC connections in regtest mode.
     - `rpcallowip=127.0.0.1`: Allows RPC connections from localhost.
     - `txindex=1`: Enables transaction indexing (required for some RPC calls).

---

## Running Bitcoin Core in Regtest Mode

1. **Start `bitcoind` in Regtest Mode**:
   - Open a terminal and run the following command:
     ```bash
     bitcoind -regtest -daemon
     ```
   - This will start the Bitcoin daemon in regtest mode.

2. **Check if `bitcoind` is Running**:
   - Use the following command to check if `bitcoind` is running:
     ```bash
     bitcoin-cli -regtest getblockchaininfo
     ```
   - You should see information about the regtest blockchain.

3. **Generate Blocks**:
   - In regtest mode, you need to generate blocks to get Bitcoin. Run the following command to generate 101 blocks (required to mature coinbase transactions):
     ```bash
     bitcoin-cli -regtest generatetoaddress 101 $(bitcoin-cli -regtest getnewaddress)
     ```

---

## Running the Scripts

This repository contains four Python scripts:

1. **A_to_B_legacy_transaction.py**: Creates a transaction from a Legacy (P2PKH) address A to address B.
2. **B_to_C_legacy_transaction.py**: Creates a transaction from Legacy address B to address C.
3. **A_to_B_segwit_transaction.py**: Creates a transaction from a SegWit (P2SH-P2WPKH) address A' to address B'.
4. **B_to_C_segwit_transaction.py**: Creates a transaction from SegWit address B' to address C'.

### Steps to Run the Scripts

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/your_repository_name.git
   cd your_repository_name
   ```

2. **Run the Legacy Transactions**:
   - First, run the script to create a transaction from Legacy address A to B:
     ```bash
     python A_to_B_legacy_transaction.py
     ```
   - Then, run the script to create a transaction from Legacy address B to C:
     ```bash
     python B_to_C_legacy_transaction.py
     ```

3. **Run the SegWit Transactions**:
   - First, run the script to create a transaction from SegWit address A' to B':
     ```bash
     python A_to_B_segwit_transaction.py
     ```
   - Then, run the script to create a transaction from SegWit address B' to C':
     ```bash
     python B_to_C_segwit_transaction.py
     ```

---

## Script Descriptions

### 1. **A_to_B_legacy_transaction.py**
   - Connects to `bitcoind` using RPC.
   - Creates a new wallet or loads an existing one.
   - Generates three Legacy addresses (A, B, and C).
   - Funds address A and creates a transaction from A to B.
   - Decodes and analyzes the transaction.

### 2. **B_to_C_legacy_transaction.py**
   - Loads transaction details from the previous script.
   - Creates a transaction from Legacy address B to C.
   - Decodes and analyzes the transaction, including the challenge and response scripts.

### 3. **A_to_B_segwit_transaction.py**
   - Connects to `bitcoind` using RPC.
   - Creates a new wallet or loads an existing one.
   - Generates three SegWit addresses (A', B', and C').
   - Funds address A' and creates a transaction from A' to B'.
   - Decodes and analyzes the transaction.

### 4. **B_to_C_segwit_transaction.py**
   - Loads transaction details from the previous script.
   - Creates a transaction from SegWit address B' to C'.
   - Decodes and analyzes the transaction, including the witness data.

---

## Report and Analysis

The report includes:
- A comparison of transaction sizes between Legacy (P2PKH) and SegWit (P2SH-P2WPKH) transactions.
- Analysis of the script structures and how they validate transactions.
- Screenshots of decoded scripts and Bitcoin debugger execution.

---

## Contributors

- [Anmol Jain](https://github.com/Anmoljain2005) : 230008009
- [Priyanshu Patel](https://github.com/Priyanshu7058) : 230008026
- [Mitanshu Kumawat](https://github.com/MitanshuKumawat) : 230008022

---

## Acknowledgements

This Bitcoin Scripting Assignment is a part of the course CS-216 Introduction to Blockchain under the guidance of Dr. Subhra Mazumdar.

**Happy Scripting!** 🚀
