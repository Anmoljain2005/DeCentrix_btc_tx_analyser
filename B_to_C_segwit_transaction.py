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
    with open("Segwit_transaction_details.txt", "r") as f:
        for line in f:
            key, value = line.strip().split("=", 1)
            tx_details[key] = value
    
    txid_a_to_b = tx_details["TXID_A_TO_B_SEGWIT"]
    addr_b = tx_details["ADDR_B_SEGWIT"]
    addr_c = tx_details["ADDR_C_SEGWIT"]
    
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
for utxo in unspent:
    if utxo['txid'] == txid_a_to_b:
        print(f"Found UTXO from A' to B' transaction: {utxo['txid']} with amount {utxo['amount']} BTC")
        break
else:
    print(f"Could not find UTXO with TXID {txid_a_to_b}. Available UTXOs:")
    for utxo in unspent:
        print(f"  TXID: {utxo['txid']}, Amount: {utxo['amount']} BTC")
    # Use the first available UTXO as fallback
    utxo = unspent[0]
    print(f"Using first available UTXO instead: {utxo['txid']} with amount {utxo['amount']} BTC")

# Define the transaction fee (from regtest parameters)
transaction_fee = Decimal('0.0001')  # paytxfee=0.0001

# Calculate amounts after deducting the fee
remaining_amount = utxo['amount'] - transaction_fee
amount_to_send_c = remaining_amount * Decimal('0.5')  # 50% to C'
amount_to_send_b = remaining_amount * Decimal('0.5')  # 50% back to B'

# Create a raw transaction
raw_tx = rpc_connection.createrawtransaction(
    [{"txid": utxo['txid'], "vout": utxo['vout']}],
    {addr_c: float(amount_to_send_c), addr_b: float(amount_to_send_b)}  # Send to C' and B'
)

# Decode the raw transaction to analyze it before signing
decoded_tx_before = rpc_connection.decoderawtransaction(raw_tx)
print("\nDecoded Raw Transaction (before signing):")
print(f"Transaction ID: {decoded_tx_before['txid']}")
print(f"Input TXID: {decoded_tx_before['vin'][0]['txid']}")
print(f"Output to Address C': {decoded_tx_before['vout'][0]['scriptPubKey']['address']}")
print(f"Output to Address C' amount: {decoded_tx_before['vout'][0]['value']} BTC")
print(f"Output to Address B': {decoded_tx_before['vout'][1]['scriptPubKey']['address']}")
print(f"Output to Address B' amount: {decoded_tx_before['vout'][1]['value']} BTC")
print(f"ScriptPubKey (Locking Script) for Address C': {decoded_tx_before['vout'][0]['scriptPubKey']['hex']}")
print(f"ScriptPubKey ASM: {decoded_tx_before['vout'][0]['scriptPubKey']['asm']}")
print(f"Script type: {decoded_tx_before['vout'][0]['scriptPubKey']['type']}")

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
tx_weight = decoded_tx_after['weight']
tx_virtual_size = (tx_weight + 3) // 4  # Virtual size formula
print(f"Transaction virtual size: {tx_virtual_size} bytes")

# Get the hex of the signed transaction
transaction_hex = signed_tx['hex']
# Get the previous transaction to extract the input hex
input_hex = prev_tx['hex']  # This is the raw hex of the previous transaction

# Print both hex values
print(f"Input Transaction Hex (previous): {input_hex}")
print(f"Current Transaction Hex (signed): {transaction_hex}")

# Broadcast the transaction
tx_id = rpc_connection.sendrawtransaction(signed_tx['hex'])
print(f"\nTransaction from B' to C' and back to B' broadcasted with TXID: {tx_id}")

# Mine a block to confirm the transaction
rpc_connection.generatetoaddress(1, mining_address)
print("Mined 1 block to confirm B' to C' and back to B' transaction")

print("\nTransaction from B' to C' and back to B' completed successfully!")