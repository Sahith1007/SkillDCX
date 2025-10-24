from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import base64
from algosdk.v2client import algod
from algosdk import encoding, transaction
from algosdk.future.transaction import ApplicationCallTxn
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
    \"\"\"\n    Verify a certificate's authenticity using the smart contract\n    \n    This endpoint:\n    1. Calls the certification contract's verify function\n    2. Checks if the certificate exists and matches the expected IPFS hash\n    3. Returns verification result\n    \"\"\"\n    try:\n        # Get certification contract app ID\n        cert_app_id = get_contract_app_id("certification")\n        if cert_app_id == 0:\n            raise HTTPException(status_code=503, detail="Certification contract not deployed")\n        \n        # Validate addresses\n        if not encoding.is_valid_address(request.certificate_holder):\n            raise HTTPException(status_code=400, detail="Invalid certificate holder address")\n        \n        # Get account info to check if they have opted into the contract\n        try:\n            account_info = algod_client.account_info(request.certificate_holder)\n            apps_local_state = account_info.get('apps-local-state', [])\n            \n            # Check if user has opted into the certification app\n            app_state = None\n            for app in apps_local_state:\n                if app['id'] == cert_app_id:\n                    app_state = app.get('key-value', [])\n                    break\n            \n            if app_state is None:\n                return ContractCallResponse(\n                    success=False,\n                    message="Certificate holder has not opted into the certification contract",\n                    data={"opted_in": False}\n                )\n            \n            # Parse the local state to extract certificate data\n            cert_data = {}\n            for kv in app_state:\n                key = base64.b64decode(kv['key']).decode('utf-8')\n                if kv['value']['type'] == 1:  # bytes\n                    value = base64.b64decode(kv['value']['bytes']).decode('utf-8')\n                else:  # uint\n                    value = kv['value']['uint']\n                cert_data[key] = value\n            \n            # Check if certificate exists and is active\n            if 'ipfs_hash' not in cert_data or cert_data.get('active', 0) != 1:\n                return ContractCallResponse(\n                    success=False,\n                    message="No active certificate found for this address",\n                    data={"certificate_data": cert_data}\n                )\n            \n            # Verify IPFS hash matches\n            stored_hash = cert_data.get('ipfs_hash', '')\n            if stored_hash == request.expected_ipfs_hash:\n                return ContractCallResponse(\n                    success=True,\n                    message="Certificate verified successfully",\n                    data={\n                        "certificate_data": cert_data,\n                        "verified": True,\n                        "issuer": cert_data.get('issuer', ''),\n                        "timestamp": cert_data.get('timestamp', 0),\n                        "metadata": cert_data.get('metadata', '')\n                    }\n                )\n            else:\n                return ContractCallResponse(\n                    success=False,\n                    message="Certificate IPFS hash does not match expected value",\n                    data={\n                        "expected_hash": request.expected_ipfs_hash,\n                        "stored_hash": stored_hash,\n                        "certificate_data": cert_data\n                    }\n                )\n                \n        except Exception as e:\n            logger.error(f"Error reading certificate data: {e}")\n            return ContractCallResponse(\n                success=False,\n                message=f"Error reading certificate data: {str(e)}"\n            )\n            \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Unexpected error verifying certificate: {e}")\n        raise HTTPException(status_code=500, detail="Internal server error during verification")\n\n@router.get("/certificate/{address}", response_model=ContractCallResponse)\nasync def get_certificate_info(address: str):\n    \"\"\"\n    Get certificate information for a specific address\n    \"\"\"\n    try:\n        # Validate address\n        if not encoding.is_valid_address(address):\n            raise HTTPException(status_code=400, detail="Invalid Algorand address")\n        \n        # Get certification contract app ID\n        cert_app_id = get_contract_app_id("certification")\n        if cert_app_id == 0:\n            raise HTTPException(status_code=503, detail="Certification contract not deployed")\n        \n        # Get account info\n        account_info = algod_client.account_info(address)\n        apps_local_state = account_info.get('apps-local-state', [])\n        \n        # Find certificate data\n        cert_data = None\n        for app in apps_local_state:\n            if app['id'] == cert_app_id:\n                app_state = app.get('key-value', [])\n                cert_data = {}\n                for kv in app_state:\n                    key = base64.b64decode(kv['key']).decode('utf-8')\n                    if kv['value']['type'] == 1:  # bytes\n                        try:\n                            # Try to decode as string first\n                            value = base64.b64decode(kv['value']['bytes']).decode('utf-8')\n                        except:\n                            # If decoding fails, keep as base64\n                            value = kv['value']['bytes']\n                    else:  # uint\n                        value = kv['value']['uint']\n                    cert_data[key] = value\n                break\n        \n        if cert_data is None:\n            return ContractCallResponse(\n                success=False,\n                message="No certificate found for this address",\n                data={"opted_in": False}\n            )\n        \n        return ContractCallResponse(\n            success=True,\n            message="Certificate information retrieved successfully",\n            data={\n                "certificate_data": cert_data,\n                "app_id": cert_app_id,\n                "address": address\n            }\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error getting certificate info: {e}")\n        raise HTTPException(status_code=500, detail=f"Error retrieving certificate info: {str(e)}")\n\n@router.get("/certificates/{address}")\nasync def get_user_certificates(address: str):\n    \"\"\"\n    Get all certificates owned by a user\n    This would typically involve reading from multiple apps or indexing service\n    \"\"\"\n    try:\n        # For now, just get the single certificate from our main contract\n        cert_response = await get_certificate_info(address)\n        \n        if cert_response.success:\n            certificates = [{\n                "id": 1,\n                "contract_app_id": get_contract_app_id("certification"),\n                "certificate_data": cert_response.data["certificate_data"]\n            }]\n        else:\n            certificates = []\n        \n        return {\n            "success": True,\n            "address": address,\n            "certificates": certificates,\n            "total": len(certificates)\n        }\n        \n    except Exception as e:\n        logger.error(f"Error getting user certificates: {e}")\n        raise HTTPException(status_code=500, detail=f"Error retrieving certificates: {str(e)}")\n\n@router.get("/issuer/{address}/status")\nasync def check_issuer_status(address: str):\n    \"\"\"\n    Check if an address is an authorized issuer\n    \"\"\"\n    try:\n        # Validate address\n        if not encoding.is_valid_address(address):\n            raise HTTPException(status_code=400, detail="Invalid Algorand address")\n        \n        # Get issuer registry contract app ID\n        registry_app_id = get_contract_app_id("issuer_registry")\n        if registry_app_id == 0:\n            return {\n                "success": False,\n                "message": "Issuer registry contract not deployed",\n                "authorized": False\n            }\n        \n        # Get account info\n        account_info = algod_client.account_info(address)\n        apps_local_state = account_info.get('apps-local-state', [])\n        \n        # Check if address is in the issuer registry\n        issuer_data = None\n        for app in apps_local_state:\n            if app['id'] == registry_app_id:\n                app_state = app.get('key-value', [])\n                issuer_data = {}\n                for kv in app_state:\n                    key = base64.b64decode(kv['key']).decode('utf-8')\n                    if kv['value']['type'] == 1:  # bytes\n                        value = base64.b64decode(kv['value']['bytes']).decode('utf-8')\n                    else:  # uint\n                        value = kv['value']['uint']\n                    issuer_data[key] = value\n                break\n        \n        is_authorized = issuer_data is not None and issuer_data.get('authorized', 0) == 1\n        \n        return {\n            "success": True,\n            "address": address,\n            "authorized": is_authorized,\n            "issuer_data": issuer_data,\n            "registry_app_id": registry_app_id\n        }\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error checking issuer status: {e}")\n        raise HTTPException(status_code=500, detail=f"Error checking issuer status: {str(e)}")\n\n@router.get("/info")\nasync def get_contract_info():\n    \"\"\"\n    Get information about deployed contracts\n    \"\"\"\n    return {\n        "deployed_contracts": deployed_contracts,\n        "testnet_explorer": {\n            "base_url": "https://testnet.algoexplorer.io/application/",\n            "certification_contract": f"https://testnet.algoexplorer.io/application/{deployed_contracts.get('certification_app_id', 0)}",\n            "issuer_registry": f"https://testnet.algoexplorer.io/application/{deployed_contracts.get('issuer_registry_app_id', 0)}\"\n        },\n        "available": len(deployed_contracts) > 0\n    }