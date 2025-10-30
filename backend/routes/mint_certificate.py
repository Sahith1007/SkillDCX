from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import sys
import os

# Add parent directory to path to import service
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.certificate_minting_service import minting_service

router = APIRouter()


class MintCertificateRequest(BaseModel):
    """Request model for certificate minting"""
    issuer_private_key: str
    cert_id: str
    recipient_address: str
    certificate_metadata: Dict
    ipfs_hash: str


class MintCertificateResponse(BaseModel):
    """Response model for certificate minting"""
    success: bool
    cert_id: str
    verification_layers: Dict
    nft_asset_id: Optional[int]
    transaction_id: Optional[str]
    message: str


@router.post("/certificate", response_model=MintCertificateResponse)
async def mint_certificate(request: MintCertificateRequest):
    """
    Mint NFT certificate with 3-layer verification
    
    Flow:
    1. Verify issuer is authorized (Layer 1)
    2. Verify certificate with AI (Layer 2)
    3. Verify IPFS hash (Layer 3)
    4. Mint NFT on Algorand
    5. Record on smart contract
    
    Returns:
        MintCertificateResponse with status and verification details
    """
    
    try:
        # Execute full minting flow
        result = await minting_service.issue_certificate_full_flow(
            issuer_private_key=request.issuer_private_key,
            cert_id=request.cert_id,
            recipient_address=request.recipient_address,
            certificate_metadata=request.certificate_metadata,
            ipfs_hash=request.ipfs_hash
        )
        
        return MintCertificateResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Certificate minting error: {str(e)}"
        )


@router.get("/status/{cert_id}")
async def get_certificate_status(cert_id: str):
    """
    Get certificate minting status by cert_id
    
    This is a placeholder for tracking certificate issuance status
    """
    return {
        "cert_id": cert_id,
        "status": "pending",
        "message": "Status tracking not yet implemented"
    }


@router.post("/verify-layers")
async def verify_layers_only(request: MintCertificateRequest):
    """
    Test all 3 verification layers without minting
    
    Useful for debugging and testing the verification flow
    """
    
    try:
        from algosdk import account
        
        issuer_address = account.address_from_private_key(request.issuer_private_key)
        
        result = {
            "cert_id": request.cert_id,
            "verification_layers": {}
        }
        
        # Layer 1: Issuer verification
        issuer_authorized, issuer_msg = await minting_service.verify_issuer_authorization(
            issuer_address,
            minting_service.unified_app_id
        )
        result["verification_layers"]["issuer_registry"] = {
            "passed": issuer_authorized,
            "message": issuer_msg
        }
        
        # Layer 2: AI verification
        ai_valid, ai_confidence, ai_reason = await minting_service.verify_certificate_with_ai(
            request.cert_id,
            request.recipient_address,
            request.ipfs_hash,
            issuer_address,
            request.certificate_metadata
        )
        result["verification_layers"]["ai_verification"] = {
            "passed": ai_valid,
            "confidence": ai_confidence,
            "reason": ai_reason
        }
        
        # Layer 3: IPFS verification
        ipfs_valid, ipfs_msg, ipfs_data = await minting_service.verify_ipfs_hash(
            request.ipfs_hash
        )
        result["verification_layers"]["ipfs_verification"] = {
            "passed": ipfs_valid,
            "message": ipfs_msg,
            "data": ipfs_data
        }
        
        # Overall status
        all_passed = issuer_authorized and ai_valid and ipfs_valid
        result["all_layers_passed"] = all_passed
        result["ready_to_mint"] = all_passed
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Verification error: {str(e)}"
        )
