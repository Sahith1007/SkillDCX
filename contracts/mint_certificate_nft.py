"""
Mint Certificate NFT

This script creates an Algorand Standard Asset (NFT) for a certificate
and calls the unified contract's issue method with 3-layer verification.
"""

import os
import sys
import json
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from algosdk.encoding import decode_address

# Contract details
APP_ID = 748842503
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""


def create_nft(client, private_key, cert_data):
    """Create an Algorand ASA (NFT) for the certificate"""
    
    sender = account.address_from_private_key(private_key)
    params = client.suggested_params()
    
    # NFT parameters
    asset_name = f"Certificate-{cert_data['cert_id'][:8]}"
    unit_name = "CERT"
    total = 1  # NFT is unique
    decimals = 0  # NFT is indivisible
    default_frozen = False
    
    # Metadata URL pointing to IPFS
    asset_url = f"ipfs://{cert_data['ipfs_hash']}"
    
    # Create ASA transaction
    txn = transaction.AssetConfigTxn(
        sender=sender,
        sp=params,
        total=total,
        default_frozen=default_frozen,
        unit_name=unit_name,
        asset_name=asset_name,
        manager=sender,
        reserve=None,
        freeze=None,
        clawback=None,  # Make it soulbound (non-transferable) by removing clawback
        url=asset_url,
        decimals=decimals,
        note=json.dumps({
            "standard": "arc69",
            "description": f"Certificate NFT for {cert_data['student_name']}",
            "external_url": f"ipfs://{cert_data['ipfs_hash']}",
            "properties": {
                "course": cert_data['course_name'],
                "issuer": cert_data['issuer_address'],
                "timestamp": cert_data['timestamp']
            }
        }).encode()
    )
    
    # Sign and send
    signed_txn = txn.sign(private_key)
    tx_id = client.send_transaction(signed_txn)
    
    print(f"NFT creation transaction sent: {tx_id}")
    
    # Wait for confirmation
    confirmed_txn = transaction.wait_for_confirmation(client, tx_id, 4)
    asset_id = confirmed_txn["asset-index"]
    
    print(f"✓ NFT created with Asset ID: {asset_id}")
    
    return asset_id


def issue_certificate_on_contract(client, private_key, cert_data, nft_asset_id, ai_verified=True):
    """Call the unified contract's issue method"""
    
    sender = account.address_from_private_key(private_key)
    params = client.suggested_params()
    
    # Encode recipient address
    recipient_addr_bytes = decode_address(cert_data['recipient_address'])
    
    # Create application call
    # Args: [method, cert_id, ipfs_hash, recipient_address, metadata, ai_verified_flag, nft_asset_id]
    txn = transaction.ApplicationNoOpTxn(
        sender=sender,
        sp=params,
        index=APP_ID,
        app_args=[
            b"issue",
            cert_data['cert_id'].encode(),
            cert_data['ipfs_hash'].encode(),
            recipient_addr_bytes,
            json.dumps({
                "student_name": cert_data['student_name'],
                "course_name": cert_data['course_name'],
                "timestamp": cert_data['timestamp']
            }).encode(),
            (1 if ai_verified else 0).to_bytes(1, 'big'),
            str(nft_asset_id).encode()
        ]
    )
    
    # Sign and send
    signed_txn = txn.sign(private_key)
    tx_id = client.send_transaction(signed_txn)
    
    print(f"Certificate issuance transaction sent: {tx_id}")
    
    # Wait for confirmation
    confirmed_txn = transaction.wait_for_confirmation(client, tx_id, 4)
    
    print(f"✓ Certificate issued on-chain!")
    print(f"Transaction confirmed in round: {confirmed_txn['confirmed-round']}")
    
    return tx_id


def mint_certificate(cert_data, ai_verified=True):
    """
    Main function to mint a certificate NFT with 3-layer verification
    
    Args:
        cert_data: Dictionary with:
            - cert_id: Unique certificate ID
            - ipfs_hash: IPFS hash of certificate metadata
            - student_name: Name of recipient
            - course_name: Course name
            - issuer_address: Address of issuer
            - recipient_address: Address of certificate recipient
            - timestamp: Unix timestamp
        ai_verified: Boolean indicating if AI verification passed
    """
    
    print("=" * 60)
    print("MINT CERTIFICATE NFT")
    print("=" * 60)
    
    # Get mnemonic
    mnemonic_phrase = os.getenv("DEPLOYER_MNEMONIC")
    if not mnemonic_phrase:
        print("ERROR: DEPLOYER_MNEMONIC not found in environment")
        sys.exit(1)
    
    try:
        private_key = mnemonic.to_private_key(mnemonic_phrase)
        issuer_address = account.address_from_private_key(private_key)
    except Exception as e:
        print(f"ERROR: Invalid mnemonic - {e}")
        sys.exit(1)
    
    # Connect to Algorand
    client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    
    print(f"\nIssuer: {issuer_address}")
    print(f"Certificate ID: {cert_data['cert_id']}")
    print(f"Recipient: {cert_data['recipient_address']}")
    print(f"IPFS Hash: {cert_data['ipfs_hash']}")
    print(f"AI Verified: {ai_verified}")
    
    try:
        # Step 1: Create NFT
        print("\n" + "=" * 60)
        print("STEP 1: Creating NFT...")
        print("=" * 60)
        nft_asset_id = create_nft(client, private_key, cert_data)
        
        # Step 2: Issue on contract with 3-layer verification
        print("\n" + "=" * 60)
        print("STEP 2: Issuing certificate on-chain...")
        print("=" * 60)
        tx_id = issue_certificate_on_contract(
            client,
            private_key,
            cert_data,
            nft_asset_id,
            ai_verified
        )
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"NFT Asset ID: {nft_asset_id}")
        print(f"Transaction: https://testnet.algoexplorer.io/tx/{tx_id}")
        print(f"NFT Explorer: https://testnet.algoexplorer.io/asset/{nft_asset_id}")
        
        return {
            "nft_asset_id": nft_asset_id,
            "transaction_id": tx_id,
            "contract_app_id": APP_ID
        }
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Example usage
    example_cert = {
        "cert_id": "CERT-2025-001",
        "ipfs_hash": "QmExample123456789",
        "student_name": "Alice Johnson",
        "course_name": "Blockchain Development",
        "issuer_address": "HNTEOSL5NPTVES7GWQ3TXE3FFCTNT337H7ZNEIBO2EAYMZWKN2ZGUL742Q",
        "recipient_address": "HNTEOSL5NPTVES7GWQ3TXE3FFCTNT337H7ZNEIBO2EAYMZWKN2ZGUL742Q",  # Replace with actual recipient
        "timestamp": "2025-01-30T00:00:00Z"
    }
    
    mint_certificate(example_cert, ai_verified=True)
