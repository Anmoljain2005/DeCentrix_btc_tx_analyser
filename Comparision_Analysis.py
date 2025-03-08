from bitcoinrpc.authproxy import AuthServiceProxy

# Connection details
rpc_user = 'decentrix_crew'
rpc_password = 'decentrix'
rpc_host = '127.0.0.1'
rpc_port = 18443

# Connect to Bitcoin daemon
wallet_name = "DeCentrixStore"
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}/wallet/{wallet_name}")

# Load transaction IDs from files
legacy_tx_details = {}
segwit_tx_details = {}

try:
    with open("transaction_details.txt", "r") as f:
        for line in f:
            key, value = line.strip().split("=", 1)
            legacy_tx_details[key] = value
    
    with open("segwit_transaction_details.txt", "r") as f:
        for line in f:
            key, value = line.strip().split("=", 1)
            segwit_tx_details[key] = value
    
    legacy_txid = legacy_tx_details["TXID_A_TO_B"]
    segwit_txid = segwit_tx_details["TXID_A_TO_B_SEGWIT"]
    
    print(f"Loaded transaction IDs:")
    print(f"Legacy TXID: {legacy_txid}")
    print(f"SegWit TXID: {segwit_txid}")
except Exception as e:
    print(f"Error loading transaction details: {e}")
    print("Please run both sets of scripts before running this comparison.")
    exit(1)

print("\n========== TRANSACTION COMPARISON: LEGACY vs SEGWIT ==========")

# Get raw transactions
legacy_tx_raw = rpc_connection.getrawtransaction(legacy_txid)
segwit_tx_raw = rpc_connection.getrawtransaction(segwit_txid)

# Decode transactions
legacy_tx = rpc_connection.decoderawtransaction(legacy_tx_raw)
segwit_tx = rpc_connection.decoderawtransaction(segwit_tx_raw)

# Calculate sizes
legacy_size = len(legacy_tx_raw) // 2  # hex string to bytes
segwit_size = len(segwit_tx_raw) // 2  # hex string to bytes

print(f"\n1. Size Comparison:")
print(f"   Legacy transaction size: {legacy_size} bytes")
print(f"   SegWit transaction size: {segwit_size} bytes")
print(f"   Size difference: {legacy_size - segwit_size} bytes ({((legacy_size - segwit_size) / legacy_size * 100):.2f}% smaller with SegWit)")

# Analyze script structures
print("\n2. Script Structure Comparison:")

print("\n   Legacy (P2PKH) Transaction:")
print(f"   - ScriptPubKey (Locking Script): {legacy_tx['vout'][0]['scriptPubKey']['asm']}")
print(f"   - Script type: {legacy_tx['vout'][0]['scriptPubKey']['type']}")

print("\n   SegWit (P2SH-P2WPKH) Transaction:")
print(f"   - ScriptPubKey (Locking Script): {segwit_tx['vout'][0]['scriptPubKey']['asm']}")
print(f"   - Script type: {segwit_tx['vout'][0]['scriptPubKey']['type']}")

# Find signed versions of these transactions
# Get transactions in last few blocks
block_count = rpc_connection.getblockcount()
recent_blocks = []
for i in range(block_count, max(block_count - 10, 0), -1):
    block_hash = rpc_connection.getblockhash(i)
    block = rpc_connection.getblock(block_hash)
    recent_blocks.extend(block['tx'])

# Look for our transactions
legacy_signed_tx = None
segwit_signed_tx = None

for txid in recent_blocks:
    if txid != legacy_txid and txid != segwit_txid:  # Skip our original transactions
        tx_raw = rpc_connection.getrawtransaction(txid)
        tx = rpc_connection.decoderawtransaction(tx_raw)
        
        # Check inputs to see if they spend our original transactions
        for vin in tx['vin']:
            if vin.get('txid') == legacy_txid:
                legacy_signed_tx = tx
            elif vin.get('txid') == segwit_txid:
                segwit_signed_tx = tx

print("\n3. Signature and Witness Analysis:")
if legacy_signed_tx:
    print("\n   Legacy Transaction Signature:")
    print(f"   - ScriptSig (Unlocking Script): {legacy_signed_tx['vin'][0]['scriptSig']['asm']}")
    print(f"   - ScriptSig size: {len(legacy_signed_tx['vin'][0]['scriptSig']['hex']) // 2} bytes")
else:
    print("\n   Legacy Transaction Signature: Not found in recent blocks")

if segwit_signed_tx:
    print("\n   SegWit Transaction Signature:")
    
    if 'scriptSig' in segwit_signed_tx['vin'][0]:
        print(f"   - ScriptSig (Redeem Script): {segwit_signed_tx['vin'][0]['scriptSig']['asm']}")
        print(f"   - ScriptSig size: {len(segwit_signed_tx['vin'][0]['scriptSig']['hex']) // 2} bytes")
    else:
        print("   - No ScriptSig (uses witness data)")
    
    if 'txinwitness' in segwit_signed_tx['vin'][0]:
        witness_size = sum(len(item) // 2 for item in segwit_signed_tx['vin'][0]['txinwitness'])
        print(f"   - Witness data: {segwit_signed_tx['vin'][0]['txinwitness']}")
        print(f"   - Witness size: {witness_size} bytes")
else:
    print("\n   SegWit Transaction Signature: Not found in recent blocks")

print("\n4. Benefits of SegWit:")
print("   - Transaction Malleability: SegWit fixes transaction malleability by moving signatures to the witness data.")
print("   - Size Reduction: By moving signature data to the witness, which is discounted in fee calculations.")
print("   - Increased Block Capacity: Allows more transactions to fit in a block without increasing the block size.")
print("   - Future Script Versioning: Enables easier upgrades to Bitcoin's scripting capabilities.")

print("\n5. P2SH-P2WPKH vs P2PKH Explanation:")
print("   - P2PKH (Pay to Public Key Hash): Standard legacy address format.")
print("     Script: OP_DUP OP_HASH160 <PubKeyHash> OP_EQUALVERIFY OP_CHECKSIG")
print("\n   - P2SH-P2WPKH (Pay to Script Hash - Pay to Witness Public Key Hash): Backward compatible SegWit.")
print("     Outer Script: OP_HASH160 <ScriptHash> OP_EQUAL")
print("     Inner Witness Program: 0 <PubKeyHash>")
print("\n   The P2SH-P2WPKH format wraps a SegWit address in a P2SH address for backward compatibility.")
print("   This ensures that older wallets can still send to SegWit-enabled wallets.")

print("\n========== END OF COMPARISON ==========")