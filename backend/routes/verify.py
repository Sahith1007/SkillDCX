from fastapi import APIRouter, HTTPException
import requests
import os

router = APIRouter()

PINATA_GATEWAY = "https://gateway.pinata.cloud/ipfs"

@router.get("/certificate/{ipfs_hash}")
def verify_certificate(ipfs_hash: str):
    try:
        # Fetch JSON from IPFS
        url = f"{PINATA_GATEWAY}/{ipfs_hash}"
        res = requests.get(url)

        if res.status_code != 200:
            raise HTTPException(status_code=404, detail="Certificate not found")

        data = res.json()
        return {"status": "success", "data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying: {str(e)}")
