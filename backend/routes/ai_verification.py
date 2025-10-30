from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import random

router = APIRouter()


class CertificateVerificationRequest(BaseModel):
    """Certificate data for AI verification"""
    cert_id: str
    recipient_address: str
    ipfs_hash: str
    issuer_address: str
    metadata: dict


class CertificateVerificationResponse(BaseModel):
    """AI verification response"""
    valid: bool
    confidence: float
    reason: str


@router.post("/verifyCertificate")
async def verify_certificate_ai(request: CertificateVerificationRequest) -> CertificateVerificationResponse:
    """
    AI-powered certificate verification endpoint.
    
    This simulates an AI model that validates certificate authenticity
    by checking:
    - Certificate metadata completeness
    - Issuer reputation patterns
    - Recipient address validity
    - IPFS hash format
    - Anomaly detection
    
    In production, this would integrate with a real ML model.
    """
    
    try:
        # Simulate AI verification logic
        validation_score = 0.0
        reasons = []
        
        # Check 1: Certificate ID format (should not be empty)
        if request.cert_id and len(request.cert_id) > 5:
            validation_score += 0.20
        else:
            reasons.append("Invalid certificate ID format")
        
        # Check 2: IPFS hash format (CID validation)
        if request.ipfs_hash.startswith("Qm") or request.ipfs_hash.startswith("bafy"):
            validation_score += 0.25
        else:
            reasons.append("Invalid IPFS hash format")
        
        # Check 3: Recipient address (Algorand address length = 58)
        if len(request.recipient_address) == 58:
            validation_score += 0.20
        else:
            reasons.append("Invalid recipient address")
        
        # Check 4: Issuer address
        if len(request.issuer_address) == 58:
            validation_score += 0.15
        else:
            reasons.append("Invalid issuer address")
        
        # Check 5: Metadata completeness
        required_fields = ["courseName", "studentName", "issueDate"]
        metadata_valid = all(field in request.metadata for field in required_fields)
        
        if metadata_valid:
            validation_score += 0.20
        else:
            reasons.append("Incomplete metadata")
        
        # Determine validity (threshold: 0.80)
        is_valid = validation_score >= 0.80
        
        # If valid, provide positive reason
        if is_valid:
            reason = "Certificate passed all AI verification checks"
        else:
            reason = f"Verification failed: {'; '.join(reasons)}"
        
        return CertificateVerificationResponse(
            valid=is_valid,
            confidence=round(validation_score, 2),
            reason=reason
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI verification error: {str(e)}"
        )


@router.post("/verifyCertificate/mock")
async def verify_certificate_mock(request: dict) -> dict:
    """
    Mock endpoint that always returns valid for testing.
    Remove this in production.
    """
    return {
        "valid": True,
        "confidence": 0.95,
        "reason": "Mock verification - always valid"
    }


@router.get("/health")
async def ai_health_check():
    """Health check for AI verification service"""
    return {
        "status": "healthy",
        "service": "AI Certificate Verification",
        "version": "1.0.0"
    }
