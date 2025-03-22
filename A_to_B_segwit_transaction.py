from bitcoinrpc.authproxy import AuthServiceProxy
from decimal import Decimal

# Connection details
rpc_user = 'decentrix_crew'
rpc_password = 'decentrix'
rpc_host = '127.0.0.1'
rpc_port = 18443

# Connect to Bitcoin daemon
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}")

# Load wallet
wallet_name = "DeCentrixStore"
try:
    rpc_connection.loadwallet(wallet_name)
    print(f"Wallet {wallet_name} loaded successfully.")
except Exception as e:
    print(f"Error loading wallet: {e}")
    exit(1)

# Switch to the wallet
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}/wallet/{wallet_name}")

# Generate three P2SH-SegWit addresses
# Using "p2sh-segwit" address type which is P2SH-P2WPKH
addr_a_segwit = rpc_connection.getnewaddress("Address A SegWit", "p2sh-segwit")
addr_b_segwit = rpc_connection.getnewaddress("Address B SegWit", "p2sh-segwit")
addr_c_segwit = rpc_connection.getnewaddress("Address C SegWit", "p2sh-segwit")

print(f"Address A' (P2SH-SegWit): {addr_a_segwit}")
print(f"Address B' (P2SH-SegWit): {addr_b_segwit}")
print(f"Address C' (P2SH-SegWit): {addr_c_segwit}")

# Get a mining address for block generation
mining_address = rpc_connection.getnewaddress("Mining Address", "legacy")

# Fund address A'
funding_amount = 1.0  # BTC
txid_fund = rpc_connection.sendtoaddress(addr_a_segwit, funding_amount)
print(f"Funded Address A' with {funding_amount} BTC, TXID: {txid_fund}")

# Mine a block to confirm the funding transaction
rpc_connection.generatetoaddress(1, mining_address)
print("Mined 1 block to confirm funding transaction")

# List unspent transactions for address A'
unspent = rpc_connection.listunspent(1, 9999999, [addr_a_segwit])
if not unspent:
    print("No unspent outputs found for address A'!")
    exit(1)

# Select the UTXO from address A'
utxo = unspent[0]
print(f"Using UTXO: {utxo['txid']} with amount {utxo['amount']} BTC")

# Define the transaction fee (from regtest parameters)
transaction_fee = Decimal('0.0001')  # paytxfee=0.0001

# Calculate amounts after deducting the fee
remaining_amount = utxo['amount'] - transaction_fee
amount_to_send_b = remaining_amount * Decimal('0.7')  # 70% to B'
amount_to_send_a = remaining_amount * Decimal('0.3')  # 30% back to A'

# Create a raw transaction
raw_tx = rpc_connection.createrawtransaction(
    [{"txid": utxo['txid'], "vout": utxo['vout']}],
    {addr_b_segwit: float(amount_to_send_b), addr_a_segwit: float(amount_to_send_a)}  # Send to B' and A'
)

# Decode the raw transaction to analyze it
decoded_tx = rpc_connection.decoderawtransaction(raw_tx)
print("\nDecoded Raw Transaction:")
print(f"Transaction ID: {decoded_tx['txid']}")
print(f"Input TXID: {decoded_tx['vin'][0]['txid']}")
print(f"Output to Address B': {decoded_tx['vout'][0]['scriptPubKey']['address']}")
print(f"Output to Address B' amount: {decoded_tx['vout'][0]['value']} BTC")
print(f"Output to Address A': {decoded_tx['vout'][1]['scriptPubKey']['address']}")
print(f"Output to Address A' amount: {decoded_tx['vout'][1]['value']} BTC")
print(f"ScriptPubKey (Locking Script) for Address B': {decoded_tx['vout'][0]['scriptPubKey']['hex']}")
print(f"ScriptPubKey ASM: {decoded_tx['vout'][0]['scriptPubKey']['asm']}")
print(f"Script type: {decoded_tx['vout'][0]['scriptPubKey']['type']}")

# Sign the transaction
signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx)
if signed_tx['complete']:
    print("\nTransaction signed successfully!")
else:
    print("\nFailed to sign transaction completely.")
    exit(1)

# Broadcast the transaction
tx_id = rpc_connection.sendrawtransaction(signed_tx['hex'])
print(f"\nTransaction from A' to B' and back to A' broadcasted with TXID: {tx_id}")

# Mine a block to confirm the transaction
rpc_connection.generatetoaddress(1, mining_address)
print("Mined 1 block to confirm A' to B' and back to A' transaction")

# Save transaction details for use in the next script
with open("Segwit_transaction_details.txt", "w") as f:
    f.write(f"TXID_A_TO_B_SEGWIT={tx_id}\n")
    f.write(f"ADDR_B_SEGWIT={addr_b_segwit}\n")
    f.write(f"ADDR_C_SEGWIT={addr_c_segwit}\n")

print("\nTransaction details saved to Segwit_transaction_details.txt")
print("\nTransaction from A' to B' and back to A' completed successfully!")