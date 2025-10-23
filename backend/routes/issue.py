from fastapi import APIRouter, HTTPException
import os
import requests
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")


@router.post("/certificate")
def issue_certificate_to_ipfs(data: dict):
    # Debug print - helps us see if keys are being read
    print("Using Pinata Key:", PINATA_API_KEY)
    print("Using Pinata Secret:", PINATA_API_SECRET)

    if not PINATA_API_KEY or not PINATA_API_SECRET:
        raise HTTPException(status_code=500, detail="Pinata keys not set")

    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_API_SECRET,
        "Content-Type": "application/json",
    }

    res = requests.post(url, headers=headers, json=data)

    if res.status_code != 200:
        print("Pinata response:", res.text)
        raise HTTPException(status_code=500, detail="Failed to upload to IPFS")

    ipfs_hash = res.json()["IpfsHash"]
    return {"status": "success", "ipfs_hash": ipfs_hash}
