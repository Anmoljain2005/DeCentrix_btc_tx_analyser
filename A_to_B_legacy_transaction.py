from bitcoinrpc.authproxy import AuthServiceProxy

# Connection details
rpc_user = 'decentrix_crew'
rpc_password = 'decentrix'
rpc_host = '127.0.0.1'
rpc_port = 18443

# Connect to Bitcoin daemon
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}")

# Create or load wallet
wallet_name = "DeCentrixStore"
try:
    rpc_connection.createwallet(wallet_name)
    print(f"Created new wallet: {wallet_name}")
except Exception as e:
    if "already exists" in str(e):
        print(f"Wallet {wallet_name} already exists, loading it...")
        rpc_connection.loadwallet(wallet_name)
    else:
        print(f"Error: {e}")

# Switch to the wallet
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}/wallet/{wallet_name}")

# Generate three legacy addresses
addr_a = rpc_connection.getnewaddress("Address A", "legacy")
addr_b = rpc_connection.getnewaddress("Address B", "legacy")
addr_c = rpc_connection.getnewaddress("Address C", "legacy")

print(f"Address A (Legacy): {addr_a}")
print(f"Address B (Legacy): {addr_b}")
print(f"Address C (Legacy): {addr_c}")

# Generate some blocks to get coins (only in regtest)
if rpc_connection.getblockchaininfo()['chain'] == 'regtest':
    mining_address = rpc_connection.getnewaddress("Mining Address", "legacy")
    rpc_connection.generatetoaddress(101, mining_address)
    print(f"Generated 101 blocks to {mining_address}")

# Fund address A
funding_amount = 1.0  # BTC
txid_fund = rpc_connection.sendtoaddress(addr_a, funding_amount)
print(f"Funded Address A with {funding_amount} BTC, TXID: {txid_fund}")

# Mine a block to confirm the funding transaction
rpc_connection.generatetoaddress(1, mining_address)
print("Mined 1 block to confirm funding transaction")

# List unspent transactions for address A
unspent = rpc_connection.listunspent(1, 9999999, [addr_a])
if not unspent:
    print("No unspent outputs found for address A!")
    exit(1)

# Select the UTXO from address A
utxo = unspent[0]
print(f"Using UTXO: {utxo['txid']} with amount {utxo['amount']} BTC")

# Create a raw transaction
raw_tx = rpc_connection.createrawtransaction(
    [{"txid": utxo['txid'], "vout": utxo['vout']}],
    {addr_b: float(utxo['amount'])}  # Send the full amount, let Bitcoin Core calculate the fee
)

# Fund the raw transaction (let Bitcoin Core add the fee)
funded_tx = rpc_connection.fundrawtransaction(raw_tx, {"conf_target": 6})
raw_tx_funded = funded_tx['hex']
fee_amount = funded_tx['fee']

print(f"\nEstimated fee for txconfirmtarget=6: {fee_amount} BTC")

# Decode the funded raw transaction
decoded_tx = rpc_connection.decoderawtransaction(raw_tx_funded)
print("\nDecoded Funded Raw Transaction:")
print(f"Transaction ID: {decoded_tx['txid']}")
print(f"Input TXID: {decoded_tx['vin'][0]['txid']}")
print(f"Output address: {decoded_tx['vout'][0]['scriptPubKey']['address']}")
print(f"Output amount: {decoded_tx['vout'][0]['value']} BTC")

# Sign the transaction
signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx_funded)
if signed_tx['complete']:
    print("\nTransaction signed successfully!")
else:
    print("\nFailed to sign transaction completely.")
    exit(1)

# Broadcast the transaction
tx_id = rpc_connection.sendrawtransaction(signed_tx['hex'])
print(f"\nTransaction from A to B broadcasted with TXID: {tx_id}")

# Mine a block to confirm the transaction
rpc_connection.generatetoaddress(1, mining_address)
print("Mined 1 block to confirm A to B transaction")

# Save transaction details
with open("Legacy_transaction_details.txt", "w") as f:
    f.write(f"TXID_A_TO_B={tx_id}\n")
    f.write(f"ADDR_B={addr_b}\n")
    f.write(f"ADDR_C={addr_c}\n")

print("\nTransaction details saved to Legacy_transaction_details.txt")
print("\nTransaction from A to B completed successfully!")