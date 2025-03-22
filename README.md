# Bitcoin Scripting Assignment

This repository contains the code and instructions for the Bitcoin Scripting Assignment, which involves creating and validating Bitcoin transactions using **Legacy (P2PKH)** and **SegWit (P2SH-P2WPKH)** address formats. The project is implemented in **Python** and interacts with **Bitcoin Core** (`bitcoind`) using RPC calls.

---

## Table of Contents

1. [Prerequisites](#prerequisites)  
2. [Setting Up Bitcoin Core](#setting-up-bitcoin-core)  
3. [Configuring `bitcoin.conf`](#configuring-bitcoinconf)  
4. [Running Bitcoin Core in Regtest Mode](#running-bitcoin-core-in-regtest-mode)  
5. [Running the Scripts](#running-the-scripts)  
6. [Script Descriptions](#script-descriptions)  
7. [Validating Scripts Using Bitcoin Debugger (`btcdeb`)](#validating-scripts-using-bitcoin-debugger-btcdeb)  
8. [Report and Analysis](#report-and-analysis)  
9. [Contributors](#contributors)  
10. [Acknowledgements](#acknowledgements)  

---

## Prerequisites

Ensure the following dependencies are installed:

- **Bitcoin Core** – Download from [bitcoincore.org](https://bitcoincore.org/).  
- **Python 3** – Ensure Python 3 is installed on your system.  
- **Python Libraries** – Install the required Python libraries using pip:  

```bash
pip install python-bitcoinrpc
```

---

## Setting Up Bitcoin Core

### 1. Download Bitcoin Core  
- Download the latest version of Bitcoin Core from [bitcoincore.org](https://bitcoincore.org/).  
- Follow the installation instructions for your operating system.  

### 2. Install Bitcoin Core  
- After installation, ensure `bitcoind` (Bitcoin Daemon) and `bitcoin-cli` (Bitcoin Command Line Interface) are available in your system's PATH.  

---

## Configuring `bitcoin.conf`

To run Bitcoin Core in regtest mode, configure the `bitcoin.conf` file:

### 1. Locate the Bitcoin Data Directory  
- **Linux**: `~/.bitcoin/`  
- **macOS**: `~/Library/Application Support/Bitcoin/`  
- **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\Bitcoin\`  

### 2. Create or Edit `bitcoin.conf`  
Create a file named `bitcoin.conf` if it doesn’t exist, and add the following configuration:

```ini
[regtest]
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

**Explanation**:  
- `[regtest]` – Enables regtest mode (local blockchain for testing).  
- `server=1` – Allows RPC connections.  
- `rpcuser`, `rpcpassword` – Credentials for RPC authentication.  
- `rpcport=18443` – Port for RPC connections in regtest mode.  
- `rpcallowip=127.0.0.1` – Allows RPC connections from localhost.  
- `txindex=1` – Enables transaction indexing (required for some RPC calls).  

---

## Running Bitcoin Core in Regtest Mode (On Windows)
 
### Open Command Prompt or PowerShell and `cd` into the installed directory. 

```bash
cd "C:/Program Files/Bitcoin/daemon"
``` 

### Start the daemon by entering , 

```bash
.\bitcoind -regtest
```

Now your bitcoin node is running in regtest mode.   

---

## Running the Scripts

This repository contains four Python scripts:

1. **A_to_B_legacy_transaction.py** – Creates a transaction from a Legacy (P2PKH) address A to address B.  
2. **B_to_C_legacy_transaction.py** – Creates a transaction from Legacy address B to address C.  
3. **A_to_B_segwit_transaction.py** – Creates a transaction from a SegWit (P2SH-P2WPKH) address A' to address B'.  
4. **B_to_C_segwit_transaction.py** – Creates a transaction from SegWit address B' to address C'.  

### Steps to Run the Scripts

1. **Clone the Repository**  

```bash
git clone https://github.com/Anmoljain2005/DeCentrix_btc_tx_analyser.git
cd DeCentrix_btc_tx_analyser
```

2. **Run Legacy Transactions**  

- Transaction from Legacy address A to B:  
```bash
python A_to_B_legacy_transaction.py
```

- Transaction from Legacy address B to C:  
```bash
python B_to_C_legacy_transaction.py
```

3. **Run SegWit Transactions**  

- **Restart regtest mode** before running SegWit transactions:  

```bash
cd "C:/Program Files/Bitcoin/daemon"
.\bitcoind -regtest
```

- Transaction from SegWit address A' to B':  
```bash
python A_to_B_segwit_transaction.py
```

- Transaction from SegWit address B' to C':  
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

## Validating Scripts Using Bitcoin Debugger (`btcdeb`)

To validate the correctness of the **challenge and response scripts**, you can use the **Bitcoin Debugger (`btcdeb`)**. The debugger allows you to step through the execution of Bitcoin scripts and verify their behavior.

### Steps to Use `btcdeb`

1. **Access the Debugger**  
   - For Linux users, log in to the server using the following credentials:  
     ```bash
     ssh -x guest@10.206.4.201
     ```
     Password: `root1234`  

2. **Run `btcdeb`**  
   - Once logged in, use the `btcdeb` command to debug your scripts.  
   - For **Legacy (P2PKH)** transactions:  
     ```bash
     btcdeb -v ['<unlocking_script> <locking_script>']
     ```  
     Example:  
     ```bash
     btcdeb -v ['304402203e7768e344e2afdad63f48d13501b8f9f8104d9e3dbeadff8b580ad2b1fae251022039fae209ffebf64f4adbddec8196b5760518e8edb0132dbccbaf8013544acbfb01 031434c9e53065a36ab1b41ea6abb4c554568b0204e5a6de90bdf8959002f849aa OP_DUP OP_HASH160 2a42ffdb7d2bffb06d66932a0aa3968fd8194d44 OP_EQUALVERIFY OP_CHECKSIG']
     ```  

   - For **SegWit (P2SH-P2WPKH)** transactions:  
     ```bash
     btcdeb -v ['<witness_item_0> <witness_item_1> <locking_script>']
     ```  
     Example:  
     ```bash
     btcdeb -v ['304402200c5c2c9b18dd6e5498f47fa82f717f13ce58b04b7af7bc52b3d8fd93d9e4cb4f02204c93d603ee397fc454217bde303be28f1e7ce1da687e566b2ac7c6e6c64e141601 0363d2aa56275c96dec54bcc34ee0b60b7e0383d4f0037966a17388f45ecc97fbc OP_HASH160 a149328683048f0e38d3b94c71e2895c363d315f OP_EQUAL']
     ```  

3. **Analyze the Output**  
   - The debugger will simulate the execution of the script step by step.  
   - If the script is valid, the final stack will contain `1` (true).  
   - If the script is invalid, the debugger will highlight the error.  

---

## Report and Analysis

The report includes:  
- A comparison of transaction sizes between Legacy (P2PKH) and SegWit (P2SH-P2WPKH) transactions.  
- Analysis of the script structures and how they validate transactions.  
- Screenshots of decoded scripts and Bitcoin debugger execution.  

---

## Contributors

| Name | GitHub | Roll Number |  
|-------|--------|-------------|  
| **Anmol Jain** | [Anmol Jain](https://github.com/Anmoljain2005) | 230008009 |  
| **Priyanshu Patel** | [Priyanshu Patel](https://github.com/Priyanshu7058) | 230008026 |  
| **Mitanshu Kumawat** | [Mitanshu Kumawat](https://github.com/MitanshuKumawat) | 230008022 |  

---

## Acknowledgements

This Bitcoin Scripting Assignment is part of the course **CS-216: Introduction to Blockchain** under the guidance of **Dr. Subhra Mazumdar**.

---

**Happy Scripting!** 🚀  