#!/usr/bin/env python3
"""
SkillDCX Smart Contract Deployment Script for Algorand TestNet

This script deploys both the Issuer Registry and Certification contracts
to Algorand TestNet and saves the application IDs for use in the backend.
"""

import base64
import json
from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk.future import transaction
from algosdk.encoding import decode_address
from certification_contract import certification_contract, clear_state_program as cert_clear
from issuer_registry_contract import issuer_registry_contract, clear_state_program as registry_clear
from pyteal import compileTeal, Mode

# TestNet configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # No token needed for public endpoints

# Contract configuration
GLOBAL_SCHEMA = transaction.StateSchema(num_uints=10, num_byte_slices=10)
LOCAL_SCHEMA = transaction.StateSchema(num_uints=5, num_byte_slices=10)

class AlgorandContractDeployer:
    def __init__(self):
        self.algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
        self.private_key = None
        self.address = None
        
    def setup_account(self, mnemonic_phrase=None):
        """Setup deployer account from mnemonic or generate new one"""
        if mnemonic_phrase:
            self.private_key = mnemonic.to_private_key(mnemonic_phrase)
            self.address = account.address_from_private_key(self.private_key)
        else:
            self.private_key, self.address = account.generate_account()
            print(f"Generated new account: {self.address}")
            print(f"Mnemonic: {mnemonic.from_private_key(self.private_key)}")
            print("⚠️  Fund this account on TestNet: https://testnet.algoexplorer.io/dispenser")
            
    def compile_program(self, source_code):
        """Compile PyTeal to TEAL"""
        compile_response = self.algod_client.compile(source_code)
        return base64.b64decode(compile_response['result'])
        
    def deploy_contract(self, approval_program, clear_program, app_args=None):
        """Deploy a smart contract to Algorand"""
        # Compile programs
        approval_binary = self.compile_program(approval_program)
        clear_binary = self.compile_program(clear_program)
        
        # Get network params
        params = self.algod_client.suggested_params()
        
        # Create application transaction
        txn = transaction.ApplicationCreateTxn(
            sender=self.address,
            sp=params,
            on_complete=transaction.OnComplete.NoOpOC,
            approval_program=approval_binary,
            clear_program=clear_binary,
            global_schema=GLOBAL_SCHEMA,
            local_schema=LOCAL_SCHEMA,
            app_args=app_args or []
        )
        
        # Sign and send transaction
        signed_txn = txn.sign(self.private_key)
        tx_id = self.algod_client.send_transaction(signed_txn)
        
        # Wait for confirmation
        result = transaction.wait_for_confirmation(self.algod_client, tx_id, 4)
        app_id = result['application-index']
        
        print(f"✅ Contract deployed with Application ID: {app_id}")
        return app_id
        
    def deploy_skilldcx_contracts(self):
        """Deploy both SkillDCX contracts"""
        print("🚀 Deploying SkillDCX Smart Contracts to TestNet...")
        
        # Check account balance
        account_info = self.algod_client.account_info(self.address)
        balance = account_info['amount'] / 1e6  # Convert microAlgos to Algos
        print(f"💰 Account balance: {balance} ALGO")
        
        if balance < 0.5:
            print("❌ Insufficient balance. Please fund your account with TestNet Algos.")
            return None, None
            
        try:
            # 1. Deploy Issuer Registry Contract
            print("\n📋 Deploying Issuer Registry Contract...")
            registry_approval = compileTeal(issuer_registry_contract(), Mode.Application, version=6)
            registry_clear = compileTeal(registry_clear(), Mode.Application, version=6)
            
            registry_app_id = self.deploy_contract(registry_approval, registry_clear)
            
            # 2. Deploy Certification Contract (with registry app ID)
            print("\n🎓 Deploying Certification Contract...")
            cert_approval = compileTeal(certification_contract(), Mode.Application, version=6)
            cert_clear_prog = compileTeal(cert_clear(), Mode.Application, version=6)
            
            # Pass registry app ID to certification contract
            cert_app_args = [registry_app_id.to_bytes(8, 'big')]
            cert_app_id = self.deploy_contract(cert_approval, cert_clear_prog, cert_app_args)
            
            # Save contract information
            contract_info = {
                "network": "testnet",
                "deployer_address": self.address,
                "issuer_registry_app_id": registry_app_id,
                "certification_app_id": cert_app_id,
                "deployed_at": transaction.wait_for_confirmation(self.algod_client, "", 1)['confirmed-round']
            }
            
            with open("deployed_contracts.json", "w") as f:
                json.dump(contract_info, f, indent=2)
                
            print("\n🎉 Deployment Complete!")
            print(f"📋 Issuer Registry App ID: {registry_app_id}")
            print(f"🎓 Certification App ID: {cert_app_id}")
            print("💾 Contract info saved to deployed_contracts.json")
            
            return registry_app_id, cert_app_id
            
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
            return None, None

def main():
    """Main deployment function"""
    deployer = AlgorandContractDeployer()
    
    # Option 1: Use existing account (recommended for production)
    mnemonic_phrase = input("Enter your mnemonic (or press Enter to generate new account): ").strip()
    
    if mnemonic_phrase:
        try:
            deployer.setup_account(mnemonic_phrase)
            print(f"✅ Using account: {deployer.address}")
        except Exception as e:
            print(f"❌ Invalid mnemonic: {e}")
            return
    else:
        deployer.setup_account()
        input("\n⏸️  Fund the generated account and press Enter to continue...")
    
    # Deploy contracts
    registry_id, cert_id = deployer.deploy_skilldcx_contracts()
    
    if registry_id and cert_id:
        print("\n🔗 Next steps:")
        print("1. Update your backend configuration with the new App IDs")
        print("2. Test the contracts using the provided scripts")
        print("3. Add authorized issuers to the registry")

if __name__ == "__main__":
    main()
