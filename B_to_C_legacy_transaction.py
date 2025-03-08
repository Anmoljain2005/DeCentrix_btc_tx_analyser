from bitcoinrpc.authproxy import AuthServiceProxy
from decimal import Decimal

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
    with open("transaction_details.txt", "r") as f:
        for line in f:
            key, value = line.strip().split("=", 1)
            tx_details[key] = value
    
    txid_a_to_b = tx_details["TXID_A_TO_B"]
    addr_b = tx_details["ADDR_B"]
    addr_c = tx_details["ADDR_C"]
    
    print(f"Loaded transaction details from file:")
    print(f"TXID A to B: {txid_a_to_b}")
    print(f"Address B: {addr_b}")
    print(f"Address C: {addr_c}")
except Exception as e:
    print(f"Error loading transaction details: {e}")
    print("Please run the first script (A to B transaction) before running this one.")
    exit(1)

# Mine a block to confirm the previous transaction if needed
mining_address = rpc_connection.getnewaddress("Mining Address", "legacy")

# List unspent transactions for address B
unspent = rpc_connection.listunspent(1, 9999999, [addr_b])
if not unspent:
    print("No unspent outputs found for address B! Mining another block and retrying...")
    rpc_connection.generatetoaddress(1, mining_address)
    unspent = rpc_connection.listunspent(1, 9999999, [addr_b])
    if not unspent:
        print("Still no unspent outputs for address B. Exiting.")
        exit(1)

# Find the specific UTXO from the A to B transaction
for utxo in unspent:
    if utxo['txid'] == txid_a_to_b:
        print(f"Found UTXO from A to B transaction: {utxo['txid']} with amount {utxo['amount']} BTC")
        break
else:
    print(f"Could not find UTXO with TXID {txid_a_to_b}. Available UTXOs:")
    for utxo in unspent:
        print(f"  TXID: {utxo['txid']}, Amount: {utxo['amount']} BTC")
    # Use the first available UTXO as fallback
    utxo = unspent[0]
    print(f"Using first available UTXO instead: {utxo['txid']} with amount {utxo['amount']} BTC")

# Create a raw transaction
# Use Decimal for the fee to match the type returned by RPC
amount_to_send = utxo['amount'] - Decimal('0.0001')  # Subtract a small fee
raw_tx = rpc_connection.createrawtransaction(
    [{"txid": utxo['txid'], "vout": utxo['vout']}],
    {addr_c: float(amount_to_send)}  # Convert back to float for createrawtransaction
)

# Decode the raw transaction to analyze it before signing
decoded_tx_before = rpc_connection.decoderawtransaction(raw_tx)
print("\nDecoded Raw Transaction (before signing):")
print(f"Transaction ID: {decoded_tx_before['txid']}")
print(f"Input TXID: {decoded_tx_before['vin'][0]['txid']}")
print(f"Output address: {decoded_tx_before['vout'][0]['scriptPubKey']['address']}")
print(f"Output amount: {decoded_tx_before['vout'][0]['value']} BTC")
print(f"ScriptPubKey (Locking Script) for Address C: {decoded_tx_before['vout'][0]['scriptPubKey']['hex']}")
print(f"ScriptPubKey ASM: {decoded_tx_before['vout'][0]['scriptPubKey']['asm']}")

# Sign the transaction
signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx)
if signed_tx['complete']:
    print("\nTransaction signed successfully!")
else:
    print("\nFailed to sign transaction completely.")
    exit(1)

# Decode the signed transaction to analyze ScriptSig (unlocking script)
decoded_tx_after = rpc_connection.decoderawtransaction(signed_tx['hex'])
print("\nDecoded Signed Transaction (after signing):")
print(f"ScriptSig (Unlocking Script): {decoded_tx_after['vin'][0]['scriptSig']['hex']}")
print(f"ScriptSig ASM: {decoded_tx_after['vin'][0]['scriptSig']['asm']}")

# Get the previous transaction to extract the ScriptPubKey that we're now unlocking
prev_tx = rpc_connection.getrawtransaction(utxo['txid'], 1)
print("\nPrevious Transaction ScriptPubKey (Challenge Script):")
print(f"ScriptPubKey: {prev_tx['vout'][utxo['vout']]['scriptPubKey']['hex']}")
print(f"ScriptPubKey ASM: {prev_tx['vout'][utxo['vout']]['scriptPubKey']['asm']}")

# Compare challenge and response scripts
print("\nAnalysis of Challenge-Response Scripts:")
print(f"Challenge (ScriptPubKey): {prev_tx['vout'][utxo['vout']]['scriptPubKey']['asm']}")
print(f"Response (ScriptSig): {decoded_tx_after['vin'][0]['scriptSig']['asm']}")
print("\nIn P2PKH transactions, the challenge script expects a signature and a public key that hashes to the provided hash.")
print("The response script provides these two items needed to unlock the funds.")

# Broadcast the transaction
tx_id = rpc_connection.sendrawtransaction(signed_tx['hex'])
print(f"\nTransaction from B to C broadcasted with TXID: {tx_id}")

# Mine a block to confirm the transaction
rpc_connection.generatetoaddress(1, mining_address)
print("Mined 1 block to confirm B to C transaction")

print("\nTransaction from B to C completed successfully!")