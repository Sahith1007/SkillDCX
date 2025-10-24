from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os
from algosdk.v2client import algod
from algosdk import encoding, mnemonic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallet", tags=["wallet"])

# Algorand TestNet configuration
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Load deployed contract info if available
CONTRACTS_FILE = "../contracts/deployed_contracts.json"
deployed_contracts = {}

try:
    if os.path.exists(CONTRACTS_FILE):
        with open(CONTRACTS_FILE, 'r') as f:
            deployed_contracts = json.load(f)
            logger.info(f"Loaded deployed contracts: {deployed_contracts}")
except Exception as e:
    logger.warning(f"Could not load deployed contracts: {e}")

# Models
class WalletConnectionRequest(BaseModel):
    address: str
    signature: Optional[str] = None
    message: Optional[str] = None

class WalletConnectionResponse(BaseModel):
    success: bool
    address: str
    balance: float
    message: str
    contracts: Dict[str, Any]

class WalletDisconnectRequest(BaseModel):
    address: str

# In-memory session store (use Redis or database in production)
connected_wallets = {}

@router.post("/connect", response_model=WalletConnectionResponse)
async def connect_wallet(request: WalletConnectionRequest):
    """
    Connect a Pera Wallet to SkillDCX
    
    This endpoint:
    1. Validates the wallet address format
    2. Checks account balance on Algorand TestNet
    3. Stores connection session
    4. Returns contract information
    """
    try:
        # Validate Algorand address format
        if not encoding.is_valid_address(request.address):
            raise HTTPException(status_code=400, detail="Invalid Algorand address format")
        
        # Get account information from Algorand
        try:
            account_info = algod_client.account_info(request.address)
            balance = account_info['amount'] / 1e6  # Convert microAlgos to Algos
            
            logger.info(f"Wallet connected: {request.address} with balance: {balance} ALGO")
            
        except Exception as e:
            logger.error(f"Failed to fetch account info for {request.address}: {e}")
            raise HTTPException(status_code=400, detail="Could not fetch account information from Algorand")
        
        # Store wallet session
        connected_wallets[request.address] = {
            "connected_at": account_info.get('created-at-round', 0),
            "last_activity": account_info.get('round', 0),
            "balance": balance
        }
        
        # Prepare response
        response = WalletConnectionResponse(
            success=True,
            address=request.address,
            balance=balance,
            message=f"Successfully connected wallet {request.address[:8]}...{request.address[-6:]}",
            contracts=deployed_contracts
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting wallet: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during wallet connection")

@router.post("/disconnect")
async def disconnect_wallet(request: WalletDisconnectRequest):
    """
    Disconnect a wallet from SkillDCX
    """
    try:
        if request.address in connected_wallets:
            del connected_wallets[request.address]
            logger.info(f"Wallet disconnected: {request.address}")
            
        return {
            "success": True,
            "message": "Wallet disconnected successfully"
        }
        
    except Exception as e:
        logger.error(f"Error disconnecting wallet: {e}")
        raise HTTPException(status_code=500, detail="Error disconnecting wallet")

@router.get("/status/{address}")
async def get_wallet_status(address: str):
    """
    Check if a wallet is connected and get its status
    """
    try:
        if not encoding.is_valid_address(address):
            raise HTTPException(status_code=400, detail="Invalid Algorand address format")
        
        is_connected = address in connected_wallets
        
        if is_connected:
            # Refresh balance
            try:
                account_info = algod_client.account_info(address)
                balance = account_info['amount'] / 1e6
                
                # Update stored info
                connected_wallets[address]["balance"] = balance
                connected_wallets[address]["last_activity"] = account_info.get('round', 0)
                
                return {
                    "connected": True,
                    "address": address,
                    "balance": balance,
                    "session": connected_wallets[address]
                }
                
            except Exception as e:
                logger.error(f"Failed to refresh account info for {address}: {e}")
                return {
                    "connected": True,
                    "address": address,
                    "balance": connected_wallets[address].get("balance", 0),
                    "error": "Could not refresh account info"
                }
        else:
            return {
                "connected": False,
                "address": address
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking wallet status: {e}")
        raise HTTPException(status_code=500, detail="Error checking wallet status")

@router.get("/connected")
async def get_connected_wallets():
    """
    Get list of all connected wallets (for debugging/admin purposes)
    """
    return {
        "connected_wallets": list(connected_wallets.keys()),
        "total": len(connected_wallets)
    }

@router.get("/contracts")
async def get_contract_info():
    """
    Get deployed SkillDCX smart contract information
    """
    return {
        "contracts": deployed_contracts,
        "testnet_explorer": "https://testnet.algoexplorer.io/application/{app_id}",
        "available": len(deployed_contracts) > 0
    }

# Dependency to check if wallet is connected
def require_connected_wallet(address: str):
    """Dependency to ensure wallet is connected"""
    if address not in connected_wallets:
        raise HTTPException(
            status_code=401, 
            detail="Wallet not connected. Please connect your wallet first."
        )
    return connected_wallets[address]