"""
SkillDCX Smart Contract Deployment Script

This script deploys both the Issuer Registry and Certification contracts
to Algorand TestNet and saves the deployed app IDs.

Usage:
    python deploy_contracts.py --mnemonic "your 25 word mnemonic"
    
Or set environment variable:
    DEPLOYER_MNEMONIC="your 25 word mnemonic" python deploy_contracts.py
"""

import os
import sys
import json
import argparse
from algosdk import account, mnemonic as mn, transaction
from algosdk.v2client import algod
from pyteal import compileTeal, Mode

# Import contract modules
from certification_contract import certification_contract, clear_state_program
from issuer_registry_contract import issuer_registry_contract, clear_state_program as issuer_clear_state


# Algorand TestNet configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

# Output file for deployed contract info
OUTPUT_FILE = "deployed_contracts.json"


def compile_program(client, source_code):
    """Compile PyTeal program to TEAL bytecode"""
    compile_response = client.compile(source_code)
    return compile_response['result'], compile_response['hash']


def wait_for_confirmation(client, txid, timeout=10):
    """Wait for a transaction to be confirmed"""
    last_round = client.status()['last-round']
    current_round = last_round
    
    while current_round < last_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(txid)
            if pending_txn.get('confirmed-round', 0) > 0:
                return pending_txn
        except Exception:
            pass
        
        client.status_after_block(current_round)
        current_round += 1
    
    raise Exception(f"Transaction {txid} not confirmed after {timeout} rounds")


def deploy_contract(client, sender_address, sender_private_key, approval_program, clear_program, 
                    global_schema, local_schema, app_args=None):
    """Deploy a smart contract to Algorand"""
    
    # Get network params
    params = client.suggested_params()
    
    # Compile programs
    approval_program_compiled, _ = compile_program(client, approval_program)
    clear_program_compiled, _ = compile_program(client, clear_program)
    
    # Create application transaction
    txn = transaction.ApplicationCreateTxn(
        sender=sender_address,
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval_program_compiled,
        clear_program=clear_program_compiled,
        global_schema=global_schema,
        local_schema=local_schema,
        app_args=app_args or []
    )
    
    # Sign transaction
    signed_txn = txn.sign(sender_private_key)
    
    # Send transaction
    tx_id = client.send_transaction(signed_txn)
    print(f"Transaction ID: {tx_id}")
    
    # Wait for confirmation
    confirmed_txn = wait_for_confirmation(client, tx_id)
    app_id = confirmed_txn['application-index']
    
    print(f"✓ Contract deployed successfully!")
    print(f"  App ID: {app_id}")
    print(f"  Transaction: https://testnet.algoexplorer.io/tx/{tx_id}")
    print(f"  App: https://testnet.algoexplorer.io/application/{app_id}")
    
    return app_id


def deploy_all_contracts(deployer_mnemonic):
    """Deploy all SkillDCX contracts"""
    
    print("=" * 60)
    print("SkillDCX Smart Contract Deployment")
    print("=" * 60)
    print()
    
    # Initialize algod client
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    
    # Get deployer account from mnemonic
    deployer_private_key = mn.to_private_key(deployer_mnemonic)
    deployer_address = account.address_from_private_key(deployer_private_key)
    
    print(f"Deployer Address: {deployer_address}")
    
    # Check account balance
    account_info = algod_client.account_info(deployer_address)
    balance = account_info['amount'] / 1e6  # Convert microAlgos to Algos
    print(f"Account Balance: {balance:.6f} ALGO")
    
    if balance < 0.5:
        print("\n⚠️  Warning: Low balance! You need at least 0.5 ALGO for deployment.")
        print(f"   Get TestNet ALGO from: https://bank.testnet.algorand.network/")
        print(f"   Send to: {deployer_address}")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print()
    deployed_apps = {}
    
    # 1. Deploy Issuer Registry Contract
    print("-" * 60)
    print("1. Deploying Issuer Registry Contract...")
    print("-" * 60)
    
    issuer_approval = compileTeal(issuer_registry_contract(), Mode.Application, version=6)
    issuer_clear = compileTeal(issuer_clear_state(), Mode.Application, version=6)
    
    # Global schema: admin (bytes), total_issuers (uint)
    issuer_global_schema = transaction.StateSchema(num_uints=1, num_byte_slices=1)
    # Local schema: authorized (uint), name (bytes), metadata (bytes), reg_timestamp (uint)
    issuer_local_schema = transaction.StateSchema(num_uints=2, num_byte_slices=2)
    
    issuer_app_id = deploy_contract(
        algod_client,
        deployer_address,
        deployer_private_key,
        issuer_approval,
        issuer_clear,
        issuer_global_schema,
        issuer_local_schema
    )
    
    deployed_apps['issuer_registry_app_id'] = issuer_app_id
    deployed_apps['issuer_registry_address'] = deployer_address
    
    print()
    
    # 2. Deploy Certification Contract
    print("-" * 60)
    print("2. Deploying Certification Contract...")
    print("-" * 60)
    
    cert_approval = compileTeal(certification_contract(), Mode.Application, version=6)
    cert_clear = compileTeal(clear_state_program(), Mode.Application, version=6)
    
    # Global schema: total_certs (uint), issuer_registry (uint)
    cert_global_schema = transaction.StateSchema(num_uints=2, num_byte_slices=0)
    # Local schema: ipfs_hash (bytes), issuer (bytes), timestamp (uint), active (uint), metadata (bytes)
    cert_local_schema = transaction.StateSchema(num_uints=2, num_byte_slices=3)
    
    # Pass issuer registry app ID as application argument during creation
    cert_app_id = deploy_contract(
        algod_client,
        deployer_address,
        deployer_private_key,
        cert_approval,
        cert_clear,
        cert_global_schema,
        cert_local_schema,
        app_args=[issuer_app_id.to_bytes(8, 'big')]
    )
    
    deployed_apps['certification_app_id'] = cert_app_id
    deployed_apps['certification_address'] = deployer_address
    
    print()
    
    # Save deployment info
    print("-" * 60)
    print("Saving Deployment Information...")
    print("-" * 60)
    
    deployed_apps['network'] = 'TestNet'
    deployed_apps['algod_address'] = ALGOD_ADDRESS
    deployed_apps['deployer_address'] = deployer_address
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(deployed_apps, f, indent=2)
    
    print(f"✓ Deployment info saved to: {OUTPUT_FILE}")
    print()
    
    # Summary
    print("=" * 60)
    print("Deployment Summary")
    print("=" * 60)
    print(f"\n📝 Issuer Registry App ID: {issuer_app_id}")
    print(f"   https://testnet.algoexplorer.io/application/{issuer_app_id}")
    print(f"\n📜 Certification App ID: {cert_app_id}")
    print(f"   https://testnet.algoexplorer.io/application/{cert_app_id}")
    print(f"\n💼 Deployer Address: {deployer_address}")
    print()
    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("\n1. Copy deployed_contracts.json to backend directory:")
    print(f"   cp {OUTPUT_FILE} ../backend/")
    print("\n2. Update frontend .env file with contract addresses")
    print("\n3. Test the contracts:")
    print("   - Add authorized issuers via issuer registry")
    print("   - Issue test certificates")
    print("   - Verify certificates work correctly")
    print()
    
    return deployed_apps


def main():
    parser = argparse.ArgumentParser(
        description='Deploy SkillDCX smart contracts to Algorand TestNet'
    )
    parser.add_argument(
        '--mnemonic',
        type=str,
        help='25-word mnemonic phrase for deployer account',
        default=os.environ.get('DEPLOYER_MNEMONIC')
    )
    
    args = parser.parse_args()
    
    if not args.mnemonic:
        print("Error: Deployer mnemonic required!")
        print("\nProvide via:")
        print("  1. Command line: --mnemonic \"your 25 words...\"")
        print("  2. Environment: DEPLOYER_MNEMONIC=\"your 25 words...\"")
        print("\nTo create a new TestNet account:")
        print("  1. Visit: https://bank.testnet.algorand.network/")
        print("  2. Click 'Create Account'")
        print("  3. Save the mnemonic phrase")
        print("  4. Fund the account with TestNet ALGO")
        sys.exit(1)
    
    try:
        deployed_apps = deploy_all_contracts(args.mnemonic)
        print("\n✅ All contracts deployed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
