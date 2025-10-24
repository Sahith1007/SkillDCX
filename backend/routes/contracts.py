from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import base64
from algosdk.v2client import algod
from algosdk import encoding, transaction
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contracts", tags=["contracts"])

# Algorand TestNet configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Load deployed contract info
CONTRACTS_FILE = "../contracts/deployed_contracts.json"
deployed_contracts = {}

try:
    if os.path.exists(CONTRACTS_FILE):
        with open(CONTRACTS_FILE, 'r') as f:
            deployed_contracts = json.load(f)
except Exception as e:
    logger.warning(f"Could not load deployed contracts: {e}")

# Models
class CertificateIssueRequest(BaseModel):
    issuer_address: str
    receiver_address: str
    ipfs_hash: str
    metadata: str
    private_key: Optional[str] = None  # For demo purposes - use proper signing in production

class CertificateVerifyRequest(BaseModel):
    certificate_holder: str
    expected_ipfs_hash: str

class CertificateRevokeRequest(BaseModel):
    issuer_address: str
    certificate_holder: str
    private_key: Optional[str] = None

class CertificateInfo(BaseModel):
    ipfs_hash: str
    issuer: str
    timestamp: int
    active: bool
    metadata: str

class ContractCallResponse(BaseModel):
    success: bool
    transaction_id: Optional[str]
    message: str
    data: Optional[Dict[str, Any]] = None

def get_contract_app_id(contract_name: str) -> int:
    """Get application ID for a contract"""
    if contract_name == "certification":
        return deployed_contracts.get("certification_app_id", 0)
    elif contract_name == "issuer_registry":
        return deployed_contracts.get("issuer_registry_app_id", 0)
    else:
        raise ValueError(f"Unknown contract: {contract_name}")

@router.post("/verify", response_model=ContractCallResponse)
async def verify_certificate(request: CertificateVerifyRequest):
    """
    Verify a certificate's authenticity using the smart contract
    
    This endpoint:
    1. Calls the certification contract's verify function
    2. Checks if the certificate exists and matches the expected IPFS hash
    3. Returns verification result
    """
    try:
        # Get certification contract app ID
        cert_app_id = get_contract_app_id("certification")
        if cert_app_id == 0:
            raise HTTPException(status_code=503, detail="Certification contract not deployed")
        
        # Validate addresses
        if not encoding.is_valid_address(request.certificate_holder):
            raise HTTPException(status_code=400, detail="Invalid certificate holder address")
        
        # Get account info to check if they have opted into the contract
        try:
            account_info = algod_client.account_info(request.certificate_holder)
            apps_local_state = account_info.get('apps-local-state', [])
            
            # Check if user has opted into the certification app
            app_state = None
            for app in apps_local_state:
                if app['id'] == cert_app_id:
                    app_state = app.get('key-value', [])
                    break
            
            if app_state is None:
                return ContractCallResponse(
                    success=False,
                    message="Certificate holder has not opted into the certification contract",
                    data={"opted_in": False}
                )
            
            # Parse the local state to extract certificate data
            cert_data = {}
            for kv in app_state:
                key = base64.b64decode(kv['key']).decode('utf-8')
                if kv['value']['type'] == 1:  # bytes
                    value = base64.b64decode(kv['value']['bytes']).decode('utf-8')
                else:  # uint
                    value = kv['value']['uint']
                cert_data[key] = value
            
            # Check if certificate exists and is active
            if 'ipfs_hash' not in cert_data or cert_data.get('active', 0) != 1:
                return ContractCallResponse(
                    success=False,
                    message="No active certificate found for this address",
                    data={"certificate_data": cert_data}
                )
            
            # Verify IPFS hash matches
            stored_hash = cert_data.get('ipfs_hash', '')
            if stored_hash == request.expected_ipfs_hash:
                return ContractCallResponse(
                    success=True,
                    message="Certificate verified successfully",
                    data={
                        "certificate_data": cert_data,
                        "verified": True,
                        "issuer": cert_data.get('issuer', ''),
                        "timestamp": cert_data.get('timestamp', 0),
                        "metadata": cert_data.get('metadata', '')
                    }
                )
            else:
                return ContractCallResponse(
                    success=False,
                    message="Certificate IPFS hash does not match expected value",
                    data={
                        "expected_hash": request.expected_ipfs_hash,
                        "stored_hash": stored_hash,
                        "certificate_data": cert_data
                    }
                )
                
        except Exception as e:
            logger.error(f"Error reading certificate data: {e}")
            return ContractCallResponse(
                success=False,
                message=f"Error reading certificate data: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error verifying certificate: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during verification")

@router.get("/certificate/{address}", response_model=ContractCallResponse)
async def get_certificate_info(address: str):
    """
    Get certificate information for a specific address
    """
    try:
        # Validate address
        if not encoding.is_valid_address(address):
            raise HTTPException(status_code=400, detail="Invalid Algorand address")
        
        # Get certification contract app ID
        cert_app_id = get_contract_app_id("certification")
        if cert_app_id == 0:
            raise HTTPException(status_code=503, detail="Certification contract not deployed")
        
        # Get account info
        account_info = algod_client.account_info(address)
        apps_local_state = account_info.get('apps-local-state', [])
        
        # Find certificate data
        cert_data = None
        for app in apps_local_state:
            if app['id'] == cert_app_id:
                app_state = app.get('key-value', [])
                cert_data = {}
                for kv in app_state:
                    key = base64.b64decode(kv['key']).decode('utf-8')
                    if kv['value']['type'] == 1:  # bytes
                        try:
                            # Try to decode as string first
                            value = base64.b64decode(kv['value']['bytes']).decode('utf-8')
                        except:
                            # If decoding fails, keep as base64
                            value = kv['value']['bytes']
                    else:  # uint
                        value = kv['value']['uint']
                    cert_data[key] = value
                break
        
        if cert_data is None:
            return ContractCallResponse(
                success=False,
                message="No certificate found for this address",
                data={"opted_in": False}
            )
        
        return ContractCallResponse(
            success=True,
            message="Certificate information retrieved successfully",
            data={
                "certificate_data": cert_data,
                "app_id": cert_app_id,
                "address": address
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting certificate info: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving certificate info: {str(e)}")

@router.get("/certificates/{address}")
async def get_user_certificates(address: str):
    """
    Get all certificates owned by a user
    This would typically involve reading from multiple apps or indexing service
    """
    try:
        # For now, just get the single certificate from our main contract
        cert_response = await get_certificate_info(address)
        
        if cert_response.success:
            certificates = [{
                "id": 1,
                "contract_app_id": get_contract_app_id("certification"),
                "certificate_data": cert_response.data["certificate_data"]
            }]
        else:
            certificates = []
        
        return {
            "success": True,
            "address": address,
            "certificates": certificates,
            "total": len(certificates)
        }
        
    except Exception as e:
        logger.error(f"Error getting user certificates: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving certificates: {str(e)}")

@router.get("/issuer/{address}/status")
async def check_issuer_status(address: str):
    """
    Check if an address is an authorized issuer
    """
    try:
        # Validate address
        if not encoding.is_valid_address(address):
            raise HTTPException(status_code=400, detail="Invalid Algorand address")
        
        # Get issuer registry contract app ID
        registry_app_id = get_contract_app_id("issuer_registry")
        if registry_app_id == 0:
            return {
                "success": False,
                "message": "Issuer registry contract not deployed",
                "authorized": False
            }
        
        # Get account info
        account_info = algod_client.account_info(address)
        apps_local_state = account_info.get('apps-local-state', [])
        
        # Check if address is in the issuer registry
        issuer_data = None
        for app in apps_local_state:
            if app['id'] == registry_app_id:
                app_state = app.get('key-value', [])
                issuer_data = {}
                for kv in app_state:
                    key = base64.b64decode(kv['key']).decode('utf-8')
                    if kv['value']['type'] == 1:  # bytes
                        value = base64.b64decode(kv['value']['bytes']).decode('utf-8')
                    else:  # uint
                        value = kv['value']['uint']
                    issuer_data[key] = value
                break
        
        is_authorized = issuer_data is not None and issuer_data.get('authorized', 0) == 1
        
        return {
            "success": True,
            "address": address,
            "authorized": is_authorized,
            "issuer_data": issuer_data,
            "registry_app_id": registry_app_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking issuer status: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking issuer status: {str(e)}")

@router.get("/info")
async def get_contract_info():
    """
    Get information about deployed contracts
    """
    return {
        "deployed_contracts": deployed_contracts,
        "testnet_explorer": {
            "base_url": "https://testnet.algoexplorer.io/application/",
            "certification_contract": f"https://testnet.algoexplorer.io/application/{deployed_contracts.get('certification_app_id', 0)}",
            "issuer_registry": f"https://testnet.algoexplorer.io/application/{deployed_contracts.get('issuer_registry_app_id', 0)}"
        },
        "available": len(deployed_contracts) > 0
    }
