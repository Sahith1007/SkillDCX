from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
from routes.auth import get_current_user
from services.pinata import upload_to_ipfs  # this should exist

router = APIRouter()

certificates_db: Dict[str, dict] = {}


class CertificateRequest(BaseModel):
    student_id: str
    course: str
    grade: str


@router.post("/issue")
def issue_certificate(
    data: CertificateRequest
):
    # For MVP, allowing certificate issuance without strict auth
    # In production, enable get_current_user dependency
    # current_user: dict = Depends(get_current_user)
    # if current_user["role"] != "issuer":
    #     raise HTTPException(
    #         status_code=403, detail="Only issuers can issue certificates"
    #     )

    try:
        cert_id = f"cert_{len(certificates_db) + 1}"
        cert_data = {
            "id": cert_id,
            "student_id": data.student_id,
            "course": data.course,
            "grade": data.grade,
        }

        # Upload to IPFS
        ipfs_hash = upload_to_ipfs(cert_data)

        certificates_db[cert_id] = {**cert_data, "ipfs_hash": ipfs_hash}

        return {"status": "success", "ipfs_hash": ipfs_hash, "cert_id": cert_id}
    except Exception as e:
        print(f"Error issuing certificate: {e}")
        raise HTTPException(status_code=500, detail=f"Error issuing certificate: {str(e)}")


@router.get("")
def get_certificates():
    return list(certificates_db.values())


@router.get("/list")
async def list_certificates():
    """Return all certificates"""
    return list(certificates_db.values())
