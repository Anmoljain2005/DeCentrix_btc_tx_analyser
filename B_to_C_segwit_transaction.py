from bitcoinrpc.authproxy import AuthServiceProxy
import subprocess  # Import subprocess to run btcdeb

# Connection details
rpc_user = 'decentrix_crew'
rpc_password = 'decentrix'
rpc_host = '127.0.0.1'
rpc_port = 18443

# Connect to Bitcoin daemon
wallet_name = "DeCentrixStore"
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}/wallet/{wallet_name}")

# Read transaction details from previous script
tx_details = {}
try:
    with open("Segwit_transaction_details.txt", "r") as f:
        for line in f:
            key, value = line.strip().split("=", 1)
            tx_details[key] = value
    
    txid_a_to_b = tx_details["TXID_A_TO_B"]
    addr_b = tx_details["ADDR_B"]
    addr_c = tx_details["ADDR_C"]
    
    print(f"Loaded transaction details from file:")
    print(f"TXID A' to B': {txid_a_to_b}")
    print(f"Address B': {addr_b}")
    print(f"Address C': {addr_c}")
except Exception as e:
    print(f"Error loading transaction details: {e}")
    print("Please run the first script (A' to B' transaction) before running this one.")
    exit(1)

# Mine a block to confirm the previous transaction if needed
mining_address = rpc_connection.getnewaddress("Mining Address", "legacy")

# List unspent transactions for address B'
unspent = rpc_connection.listunspent(1, 9999999, [addr_b])
if not unspent:
    print("No unspent outputs found for address B'! Mining another block and retrying...")
    rpc_connection.generatetoaddress(1, mining_address)
    unspent = rpc_connection.listunspent(1, 9999999, [addr_b])
    if not unspent:
        print("Still no unspent outputs for address B'. Exiting.")
        exit(1)

# Find the specific UTXO from the A' to B' transaction
utxo = None
for u in unspent:
    if u['txid'] == txid_a_to_b:
        utxo = u
        print(f"Found UTXO from A' to B' transaction: {utxo['txid']} with amount {utxo['amount']} BTC")
        break
else:
    print(f"Could not find UTXO with TXID {txid_a_to_b}. Available UTXOs:")
    for u in unspent:
        print(f"  TXID: {u['txid']}, Amount: {u['amount']} BTC")
    # Use the first available UTXO as fallback
    utxo = unspent[0]
    print(f"Using first available UTXO instead: {utxo['txid']} with amount {utxo['amount']} BTC")

# Create a raw transaction
raw_tx = rpc_connection.createrawtransaction(
    [{"txid": utxo['txid'], "vout": utxo['vout']}],
    {addr_c: float(utxo['amount'])}  # Send the full amount, let Bitcoin Core calculate the fee
)

# Fund the raw transaction (let Bitcoin Core add the fee)
funded_tx = rpc_connection.fundrawtransaction(raw_tx, {"conf_target": 6})
funded_raw_tx = funded_tx['hex']
fee_amount = funded_tx['fee']

print(f"\nEstimated fee for txconfirmtarget=6: {fee_amount} BTC")

# Decode the raw transaction to analyze it before signing
decoded_tx_before = rpc_connection.decoderawtransaction(funded_raw_tx)
print("\nDecoded Raw Transaction (before signing):")
print(f"Transaction ID: {decoded_tx_before['txid']}")
print(f"Input TXID: {decoded_tx_before['vin'][0]['txid']}")
print(f"Output address: {decoded_tx_before['vout'][0]['scriptPubKey']['address']}")
print(f"Output amount: {decoded_tx_before['vout'][0]['value']} BTC")
print(f"ScriptPubKey (Locking Script) for Address C': {decoded_tx_before['vout'][0]['scriptPubKey']['hex']}")
print(f"ScriptPubKey ASM: {decoded_tx_before['vout'][0]['scriptPubKey']['asm']}")
print(f"Script type: {decoded_tx_before['vout'][0]['scriptPubKey']['type']}")

# Sign the transaction
signed_tx = rpc_connection.signrawtransactionwithwallet(funded_raw_tx)
if signed_tx['complete']:
    print("\nTransaction signed successfully!")
else:
    print("\nFailed to sign transaction completely.")
    exit(1)

# Decode the signed transaction to analyze ScriptSig (unlocking script)
decoded_tx_after = rpc_connection.decoderawtransaction(signed_tx['hex'])
print("\nDecoded Signed Transaction (after signing):")
if 'scriptSig' in decoded_tx_after['vin'][0]:
    print(f"ScriptSig (Unlocking Script): {decoded_tx_after['vin'][0]['scriptSig']['hex']}")
    print(f"ScriptSig ASM: {decoded_tx_after['vin'][0]['scriptSig']['asm']}")
else:
    print("No ScriptSig in transaction input (this is expected for SegWit)")

# Check if there's witness data (for SegWit)
if 'txinwitness' in decoded_tx_after['vin'][0]:
    print("\nWitness data found (SegWit):")
    for i, witness_item in enumerate(decoded_tx_after['vin'][0]['txinwitness']):
        print(f"Witness item {i}: {witness_item}")

# Get the previous transaction to extract the ScriptPubKey that we're now unlocking
prev_tx = rpc_connection.getrawtransaction(utxo['txid'], 1)
print("\nPrevious Transaction ScriptPubKey (Challenge Script):")
print(f"ScriptPubKey: {prev_tx['vout'][utxo['vout']]['scriptPubKey']['hex']}")
print(f"ScriptPubKey ASM: {prev_tx['vout'][utxo['vout']]['scriptPubKey']['asm']}")
print(f"Script type: {prev_tx['vout'][utxo['vout']]['scriptPubKey']['type']}")

# Compare challenge and response scripts
print("\nAnalysis of Challenge-Response Scripts:")
print(f"Challenge (ScriptPubKey): {prev_tx['vout'][utxo['vout']]['scriptPubKey']['asm']}")
if 'scriptSig' in decoded_tx_after['vin'][0]:
    print(f"Response (ScriptSig): {decoded_tx_after['vin'][0]['scriptSig']['asm']}")
else:
    print("Response: No ScriptSig (witness data is used instead for SegWit)")

if 'txinwitness' in decoded_tx_after['vin'][0]:
    print("\nIn P2SH-P2WPKH (SegWit) transactions, the signature and public key are moved to the witness data")
    print("This reduces the transaction size and fixes transaction malleability issues")

# Get the transaction virtual size for analysis
tx_size = len(signed_tx['hex']) // 2  # hex string to bytes
print(f"\nTransaction size in bytes: {tx_size}")

# Broadcast the transaction
tx_id = rpc_connection.sendrawtransaction(signed_tx['hex'])
print(f"\nTransaction from B' to C' broadcasted with TXID: {tx_id}")

# Mine a block to confirm the transaction
rpc_connection.generatetoaddress(1, mining_address)
print("Mined 1 block to confirm B' to C' transaction")

# # Run btcdeb to debug the scripts
# print("\nRunning btcdeb to debug the scripts...")
# if 'scriptSig' in decoded_tx_after['vin'][0]:
#     combined_script = f"{decoded_tx_after['vin'][0]['scriptSig']['asm']} {prev_tx['vout'][utxo['vout']]['scriptPubKey']['asm']}"
# else:
#     # For SegWit transactions, use witness data
#     combined_script = f"{' '.join(decoded_tx_after['vin'][0]['txinwitness'])} {prev_tx['vout'][utxo['vout']]['scriptPubKey']['asm']}"

# try:
#     result = subprocess.run(["btcdeb", combined_script], capture_output=True, text=True, check=True)
#     print("btcdeb output:")
#     print(result.stdout)
# except subprocess.CalledProcessError as e:
#     print("Error running btcdeb:")
#     print(e.stderr)
#     exit(1)

print("\nTransaction from B' to C' completed successfully!")