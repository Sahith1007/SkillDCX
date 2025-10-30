"""
Add Authorized Issuer to Unified Certificate Contract

This script adds the deployer as an authorized issuer in the contract.
"""

import os
import sys
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from algosdk.encoding import decode_address

# Contract details
APP_ID = 748842503
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

def add_issuer(private_key, issuer_address, issuer_name, issuer_metadata="SkillDCX Official Issuer"):
    """Add an authorized issuer to the contract"""
    
    sender = account.address_from_private_key(private_key)
    client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    
    print(f"Adding issuer: {issuer_address}")
    print(f"Issuer name: {issuer_name}")
    print(f"Caller (Admin): {sender}")
    
    # Get suggested params
    params = client.suggested_params()
    
    # Encode issuer address as bytes
    issuer_addr_bytes = decode_address(issuer_address)
    
    # Create application call transaction
    # Args: [method, issuer_address, name, metadata]
    txn = transaction.ApplicationNoOpTxn(
        sender=sender,
        sp=params,
        index=APP_ID,
        app_args=[
            b"add_issuer",
            issuer_addr_bytes,
            issuer_name.encode(),
            issuer_metadata.encode()
        ]
    )
    
    # Sign transaction
    signed_txn = txn.sign(private_key)
    
    # Send transaction
    tx_id = client.send_transaction(signed_txn)
    print(f"Transaction sent: {tx_id}")
    
    # Wait for confirmation
    print("Waiting for confirmation...")
    confirmed_txn = transaction.wait_for_confirmation(client, tx_id, 4)
    
    print(f"✓ Issuer added successfully!")
    print(f"Transaction confirmed in round: {confirmed_txn['confirmed-round']}")
    
    return tx_id


def main():
    """Main function"""
    
    print("=" * 60)
    print("ADD AUTHORIZED ISSUER")
    print("=" * 60)
    
    # Get mnemonic from environment
    mnemonic_phrase = os.getenv("DEPLOYER_MNEMONIC")
    if not mnemonic_phrase:
        print("ERROR: DEPLOYER_MNEMONIC not found in environment")
        print("Run: $env:DEPLOYER_MNEMONIC=\"your mnemonic phrase\"")
        sys.exit(1)
    
    try:
        private_key = mnemonic.to_private_key(mnemonic_phrase)
        deployer_address = account.address_from_private_key(private_key)
    except Exception as e:
        print(f"ERROR: Invalid mnemonic - {e}")
        sys.exit(1)
    
    # Add self as issuer
    issuer_name = "SkillDCX"
    
    print(f"\nAdding {deployer_address} as authorized issuer...")
    
    try:
        tx_id = add_issuer(
            private_key,
            deployer_address,
            issuer_name
        )
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"Issuer: {deployer_address}")
        print(f"Name: {issuer_name}")
        print(f"Transaction: https://testnet.algoexplorer.io/tx/{tx_id}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
