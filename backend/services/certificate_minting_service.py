"""
Certificate Minting Service with 3-Layer Verification

This service orchestrates the complete certificate issuance flow:
1. Verify issuer is authorized via issuer registry
2. Validate certificate data through AI verification endpoint
3. Verify IPFS hash exists and is accessible
4. Mint NFT certificate on Algorand
5. Record transaction on smart contract
"""

import os
import json
import requests
from typing import Dict, Optional, Tuple
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from dotenv import load_dotenv

load_dotenv()


class CertificateMintingService:
    def __init__(self):
        self.algod_token = os.getenv("ALGOD_TOKEN", "")
        self.algod_address = os.getenv("ALGOD_ADDRESS", "https://testnet-api.algonode.cloud")
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)
        
        # Load contract addresses from deployed_contracts.json
        self.load_contract_addresses()
        
        # Backend API base URL
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    def load_contract_addresses(self):
        """Load deployed contract addresses"""
        try:
            contracts_path = os.path.join(
                os.path.dirname(__file__),
                "../../contracts/deployed_contracts.json"
            )
            with open(contracts_path, "r") as f:
                contracts = json.load(f)
                self.unified_app_id = contracts.get("unified_certificate_app_id", 0)
                self.issuer_registry_app_id = contracts.get("issuer_registry_app_id", 0)
        except Exception as e:
            print(f"Warning: Could not load contract addresses: {e}")
            self.unified_app_id = 0
            self.issuer_registry_app_id = 0
    
    async def verify_issuer_authorization(
        self,
        issuer_address: str,
        app_id: int
    ) -> Tuple[bool, str]:
        """
        LAYER 1: Verify issuer is authorized via smart contract
        
        Args:
            issuer_address: Algorand address of issuer
            app_id: Application ID of the unified contract
            
        Returns:
            (is_authorized, message)
        """
        try:
            # Read issuer's local state from contract
            account_info = self.algod_client.account_application_info(
                issuer_address,
                app_id
            )
            
            # Check if opted in and authorized
            if "app-local-state" not in account_info:
                return False, "Issuer not opted into contract"
            
            local_state = account_info["app-local-state"]["key-value"]
            
            # Look for 'authorized' key
            for item in local_state:
                key = item["key"]
                if key == "authorized":  # Base64 decode if needed
                    authorized = item["value"]["uint"]
                    if authorized == 1:
                        return True, "Issuer authorized"
                    else:
                        return False, "Issuer authorization revoked"
            
            return False, "Issuer not found in registry"
            
        except Exception as e:
            return False, f"Error verifying issuer: {str(e)}"
    
    async def verify_certificate_with_ai(
        self,
        cert_id: str,
        recipient_address: str,
        ipfs_hash: str,
        issuer_address: str,
        metadata: Dict
    ) -> Tuple[bool, float, str]:
        """
        LAYER 2: Verify certificate data with AI endpoint
        
        Args:
            cert_id: Certificate ID
            recipient_address: Recipient's Algorand address
            ipfs_hash: IPFS hash of certificate metadata
            issuer_address: Issuer's Algorand address
            metadata: Certificate metadata dict
            
        Returns:
            (is_valid, confidence, reason)
        """
        try:
            # Call AI verification endpoint
            response = requests.post(
                f"{self.backend_url}/ai/verifyCertificate",
                json={
                    "cert_id": cert_id,
                    "recipient_address": recipient_address,
                    "ipfs_hash": ipfs_hash,
                    "issuer_address": issuer_address,
                    "metadata": metadata
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return False, 0.0, f"AI verification failed: {response.status_code}"
            
            data = response.json()
            return data["valid"], data["confidence"], data["reason"]
            
        except Exception as e:
            return False, 0.0, f"AI verification error: {str(e)}"
    
    async def verify_ipfs_hash(self, ipfs_hash: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        LAYER 3: Verify IPFS hash exists and is accessible
        
        Args:
            ipfs_hash: IPFS CID to verify
            
        Returns:
            (exists, message, data)
        """
        try:
            # Verify via backend endpoint
            response = requests.get(
                f"{self.backend_url}/verify/certificate/{ipfs_hash}",
                timeout=10
            )
            
            if response.status_code != 200:
                return False, "IPFS hash not found or inaccessible", None
            
            data = response.json()
            if data.get("status") == "success":
                return True, "IPFS hash verified", data.get("data")
            else:
                return False, "IPFS verification failed", None
                
        except Exception as e:
            return False, f"IPFS verification error: {str(e)}", None
    
    async def mint_nft_certificate(
        self,
        issuer_private_key: str,
        recipient_address: str,
        asset_name: str,
        unit_name: str,
        ipfs_url: str,
        metadata: Dict
    ) -> Tuple[bool, Optional[int], str]:
        """
        Mint NFT certificate as Algorand ASA (Algorand Standard Asset)
        
        Args:
            issuer_private_key: Issuer's private key
            recipient_address: Recipient's address
            asset_name: Name of the certificate
            unit_name: Unit name (e.g., "CERT")
            ipfs_url: Full IPFS URL to metadata
            metadata: Certificate metadata
            
        Returns:
            (success, asset_id, message)
        """
        try:
            # Get issuer address from private key
            issuer_address = account.address_from_private_key(issuer_private_key)
            
            # Get suggested params
            params = self.algod_client.suggested_params()
            
            # Create NFT asset (total=1, decimals=0 for NFT)
            txn = transaction.AssetConfigTxn(
                sender=issuer_address,
                sp=params,
                total=1,
                default_frozen=False,
                unit_name=unit_name[:8],  # Max 8 chars
                asset_name=asset_name[:32],  # Max 32 chars
                manager=issuer_address,
                reserve=issuer_address,
                freeze=None,  # No freeze address = soulbound
                clawback=None,  # No clawback = non-transferable
                url=ipfs_url[:96],  # Max 96 chars
                decimals=0
            )
            
            # Sign transaction
            signed_txn = txn.sign(issuer_private_key)
            
            # Send transaction
            tx_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            confirmed_txn = transaction.wait_for_confirmation(
                self.algod_client,
                tx_id,
                4
            )
            
            # Get asset ID
            asset_id = confirmed_txn["asset-index"]
            
            # Transfer NFT to recipient
            transfer_success = await self._transfer_nft_to_recipient(
                issuer_private_key,
                recipient_address,
                asset_id
            )
            
            if not transfer_success:
                return False, asset_id, "NFT minted but transfer failed"
            
            return True, asset_id, f"NFT minted successfully: Asset ID {asset_id}"
            
        except Exception as e:
            return False, None, f"NFT minting error: {str(e)}"
    
    async def _transfer_nft_to_recipient(
        self,
        issuer_private_key: str,
        recipient_address: str,
        asset_id: int
    ) -> bool:
        """Transfer minted NFT to recipient"""
        try:
            issuer_address = account.address_from_private_key(issuer_private_key)
            params = self.algod_client.suggested_params()
            
            # Recipient must opt-in first (handled separately)
            # Transfer asset
            txn = transaction.AssetTransferTxn(
                sender=issuer_address,
                sp=params,
                receiver=recipient_address,
                amt=1,
                index=asset_id
            )
            
            signed_txn = txn.sign(issuer_private_key)
            tx_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            transaction.wait_for_confirmation(self.algod_client, tx_id, 4)
            
            return True
        except Exception as e:
            print(f"Transfer error: {e}")
            return False
    
    async def record_certificate_on_chain(
        self,
        issuer_private_key: str,
        cert_id: str,
        ipfs_hash: str,
        recipient_address: str,
        metadata_json: str,
        ai_verified: bool,
        nft_asset_id: int
    ) -> Tuple[bool, str]:
        """
        Record certificate on smart contract after all verifications pass
        
        Args:
            issuer_private_key: Issuer's private key
            cert_id: Certificate ID
            ipfs_hash: IPFS hash
            recipient_address: Recipient address
            metadata_json: JSON metadata string
            ai_verified: AI verification result
            nft_asset_id: Minted NFT asset ID
            
        Returns:
            (success, message)
        """
        try:
            issuer_address = account.address_from_private_key(issuer_private_key)
            params = self.algod_client.suggested_params()
            
            # Prepare app call arguments
            app_args = [
                "issue".encode(),
                cert_id.encode(),
                ipfs_hash.encode(),
                recipient_address.encode(),
                metadata_json.encode(),
                (1 if ai_verified else 0).to_bytes(8, "big"),
                str(nft_asset_id).encode()
            ]
            
            # Create application call transaction
            txn = transaction.ApplicationCallTxn(
                sender=issuer_address,
                sp=params,
                index=self.unified_app_id,
                on_complete=transaction.OnComplete.NoOpOC,
                app_args=app_args
            )
            
            # Sign and send
            signed_txn = txn.sign(issuer_private_key)
            tx_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            transaction.wait_for_confirmation(self.algod_client, tx_id, 4)
            
            return True, f"Certificate recorded on-chain: {tx_id}"
            
        except Exception as e:
            return False, f"On-chain recording error: {str(e)}"
    
    async def issue_certificate_full_flow(
        self,
        issuer_private_key: str,
        cert_id: str,
        recipient_address: str,
        certificate_metadata: Dict,
        ipfs_hash: str
    ) -> Dict:
        """
        Complete certificate issuance flow with 3-layer verification
        
        Args:
            issuer_private_key: Issuer's private key
            cert_id: Unique certificate ID
            recipient_address: Recipient's Algorand address
            certificate_metadata: Certificate metadata dict
            ipfs_hash: IPFS hash of certificate
            
        Returns:
            Result dictionary with status and details
        """
        issuer_address = account.address_from_private_key(issuer_private_key)
        
        result = {
            "success": False,
            "cert_id": cert_id,
            "verification_layers": {},
            "nft_asset_id": None,
            "transaction_id": None,
            "message": ""
        }
        
        # LAYER 1: Issuer Registry Verification
        issuer_authorized, issuer_msg = await self.verify_issuer_authorization(
            issuer_address,
            self.unified_app_id
        )
        result["verification_layers"]["issuer_registry"] = {
            "passed": issuer_authorized,
            "message": issuer_msg
        }
        
        if not issuer_authorized:
            result["message"] = f"Layer 1 failed: {issuer_msg}"
            return result
        
        # LAYER 2: AI Verification
        ai_valid, ai_confidence, ai_reason = await self.verify_certificate_with_ai(
            cert_id,
            recipient_address,
            ipfs_hash,
            issuer_address,
            certificate_metadata
        )
        result["verification_layers"]["ai_verification"] = {
            "passed": ai_valid,
            "confidence": ai_confidence,
            "reason": ai_reason
        }
        
        if not ai_valid:
            result["message"] = f"Layer 2 failed: {ai_reason}"
            return result
        
        # LAYER 3: IPFS Verification
        ipfs_valid, ipfs_msg, ipfs_data = await self.verify_ipfs_hash(ipfs_hash)
        result["verification_layers"]["ipfs_verification"] = {
            "passed": ipfs_valid,
            "message": ipfs_msg
        }
        
        if not ipfs_valid:
            result["message"] = f"Layer 3 failed: {ipfs_msg}"
            return result
        
        # All verifications passed - Mint NFT
        asset_name = certificate_metadata.get("courseName", "Certificate")[:32]
        unit_name = "CERT"
        ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
        
        nft_success, asset_id, nft_msg = await self.mint_nft_certificate(
            issuer_private_key,
            recipient_address,
            asset_name,
            unit_name,
            ipfs_url,
            certificate_metadata
        )
        
        if not nft_success:
            result["message"] = f"NFT minting failed: {nft_msg}"
            return result
        
        result["nft_asset_id"] = asset_id
        
        # Record on smart contract
        metadata_json = json.dumps(certificate_metadata)
        record_success, record_msg = await self.record_certificate_on_chain(
            issuer_private_key,
            cert_id,
            ipfs_hash,
            recipient_address,
            metadata_json,
            ai_valid,
            asset_id
        )
        
        if not record_success:
            result["message"] = f"On-chain recording failed: {record_msg}"
            return result
        
        # Success!
        result["success"] = True
        result["transaction_id"] = record_msg.split(": ")[-1]
        result["message"] = "Certificate issued successfully with 3-layer verification"
        
        return result


# Singleton instance
minting_service = CertificateMintingService()
