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
    data: CertificateRequest, current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "issuer":
        raise HTTPException(
            status_code=403, detail="Only issuers can issue certificates"
        )

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

    return {"status": "success", "ipfs_hash": ipfs_hash}


@router.get("")
def get_certificates():
    return list(certificates_db.values())


certificates_db = [
    {"id": 1, "name": "Blockchain Basics", "issuer": "SkillDCX University"},
    {"id": 2, "name": "Advanced AI", "issuer": "SkillDCX Labs"},
]


@router.get("/certificates")
async def list_certificates():
    return certificates_db
