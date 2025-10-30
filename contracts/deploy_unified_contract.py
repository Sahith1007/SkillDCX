"""
Deploy Unified Certificate Contract

This script deploys the unified certificate contract with 3-layer verification
to Algorand TestNet and updates deployed_contracts.json
"""

import os
import json
import sys
import base64
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from pyteal import compileTeal, Mode
from unified_certificate_contract import unified_certificate_contract, clear_state_program


def compile_contract():
    """Compile the unified certificate contract"""
    print("Compiling unified certificate contract...")
    
    approval_teal = compileTeal(
        unified_certificate_contract(),
        Mode.Application,
        version=6
    )
    
    clear_teal = compileTeal(
        clear_state_program(),
        Mode.Application,
        version=6
    )
    
    return approval_teal, clear_teal


def compile_program(client, teal_source):
    """Compile TEAL source code to binary"""
    compile_response = client.compile(teal_source)
    return base64.b64decode(compile_response["result"]), compile_response["hash"]


def deploy_contract(
    client,
    private_key,
    approval_program,
    clear_program,
    global_schema,
    local_schema
):
    """Deploy the smart contract to Algorand"""
    
    sender = account.address_from_private_key(private_key)
    params = client.suggested_params()
    
    # Create application transaction
    txn = transaction.ApplicationCreateTxn(
        sender=sender,
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema=global_schema,
        local_schema=local_schema,
        extra_pages=0
    )
    
    # Sign transaction
    signed_txn = txn.sign(private_key)
    
    # Send transaction
    tx_id = client.send_transaction(signed_txn)
    print(f"Transaction sent with ID: {tx_id}")
    
    # Wait for confirmation
    print("Waiting for confirmation...")
    confirmed_txn = transaction.wait_for_confirmation(client, tx_id, 4)
    
    # Get application ID
    app_id = confirmed_txn["application-index"]
    print(f"Application deployed with ID: {app_id}")
    
    # Get application address
    app_address = f"app_{app_id}"
    
    return app_id, app_address, tx_id


def update_deployed_contracts(
    app_id,
    app_address,
    deployer_address,
    network,
    algod_address
):
    """Update deployed_contracts.json with new contract info"""
    
    contracts_file = os.path.join(
        os.path.dirname(__file__),
        "deployed_contracts.json"
    )
    
    # Load existing data
    try:
        with open(contracts_file, "r") as f:
            contracts_data = json.load(f)
    except FileNotFoundError:
        contracts_data = {}
    
    # Update with new contract info
    contracts_data.update({
        "unified_certificate_app_id": app_id,
        "unified_certificate_address": app_address,
        "network": network,
        "algod_address": algod_address,
        "deployer_address": deployer_address,
        "contract_version": "1.0.0",
        "features": [
            "3-layer verification",
            "Issuer registry",
            "AI verification",
            "IPFS verification",
            "NFT minting"
        ],
        "note": "Unified certificate contract with integrated verification layers"
    })
    
    # Save updated data
    with open(contracts_file, "w") as f:
        json.dump(contracts_data, f, indent=2)
    
    print(f"✓ Updated {contracts_file}")


def main():
    """Main deployment function"""
    
    print("=" * 60)
    print("UNIFIED CERTIFICATE CONTRACT DEPLOYMENT")
    print("=" * 60)
    
    # Check for mnemonic argument
    if len(sys.argv) < 2:
        print("\nUsage: python deploy_unified_contract.py \"your 25-word mnemonic\"")
        print("or: python deploy_unified_contract.py --use-env")
        sys.exit(1)
    
    # Get private key from mnemonic
    if sys.argv[1] == "--use-env":
        mnemonic_phrase = os.getenv("DEPLOYER_MNEMONIC")
        if not mnemonic_phrase:
            print("ERROR: DEPLOYER_MNEMONIC not found in environment")
            sys.exit(1)
    else:
        mnemonic_phrase = sys.argv[1]
    
    try:
        private_key = mnemonic.to_private_key(mnemonic_phrase)
        deployer_address = account.address_from_private_key(private_key)
        print(f"\nDeployer Address: {deployer_address}")
    except Exception as e:
        print(f"ERROR: Invalid mnemonic - {e}")
        sys.exit(1)
    
    # Connect to Algorand TestNet
    algod_token = ""
    algod_address = "https://testnet-api.algonode.cloud"
    algod_client = algod.AlgodClient(algod_token, algod_address)
    
    print(f"Connected to: {algod_address}")
    
    # Check account balance
    try:
        account_info = algod_client.account_info(deployer_address)
        balance = account_info.get("amount") / 1_000_000  # Convert microAlgos to Algos
        print(f"Account Balance: {balance} ALGO")
        
        if balance < 0.5:
            print("\nWARNING: Low balance. You may need at least 0.5 ALGO for deployment.")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(0)
    except Exception as e:
        print(f"WARNING: Could not check balance - {e}")
    
    # Compile contract
    print("\n" + "=" * 60)
    approval_teal, clear_teal = compile_contract()
    
    # Compile to bytecode
    print("Compiling to bytecode...")
    approval_program, approval_hash = compile_program(algod_client, approval_teal)
    clear_program, clear_hash = compile_program(algod_client, clear_teal)
    
    print(f"Approval Program Hash: {approval_hash}")
    print(f"Clear Program Hash: {clear_hash}")
    
    # Define state schema
    # Global state: Using dynamic keys for issuers and certificates
    # Fixed keys: admin_address, total_issuers, total_certificates, registry_enabled, ai_required
    # Dynamic keys: issuer_{addr}, name_{addr}, meta_{addr}, cert_*_{addr}
    # Max is 64 total keys, allocate 16 uint + 48 bytes for flexibility
    global_schema = transaction.StateSchema(num_uints=16, num_byte_slices=48)
    
    # Local state: Not used in this version (all data in global state)
    local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)
    
    print(f"\nGlobal Schema: {global_schema.num_uints} uints, {global_schema.num_byte_slices} bytes")
    print(f"Local Schema: {local_schema.num_uints} uints, {local_schema.num_byte_slices} bytes")
    
    # Deploy contract
    print("\n" + "=" * 60)
    print("DEPLOYING CONTRACT...")
    print("=" * 60)
    
    try:
        app_id, app_address, tx_id = deploy_contract(
            algod_client,
            private_key,
            approval_program,
            clear_program,
            global_schema,
            local_schema
        )
        
        print("\n" + "=" * 60)
        print("DEPLOYMENT SUCCESSFUL!")
        print("=" * 60)
        print(f"Application ID: {app_id}")
        print(f"Application Address: {app_address}")
        print(f"Transaction ID: {tx_id}")
        print(f"Explorer: https://testnet.algoexplorer.io/application/{app_id}")
        
        # Update deployed_contracts.json
        print("\n" + "=" * 60)
        update_deployed_contracts(
            app_id,
            app_address,
            deployer_address,
            "TestNet",
            algod_address
        )
        
        print("\n✓ Deployment complete!")
        print("\nNext steps:")
        print("1. Add authorized issuers using the 'add_issuer' method")
        print("2. Configure your backend with the app_id")
        print("3. Test certificate issuance with 3-layer verification")
        
    except Exception as e:
        print(f"\nERROR during deployment: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
