import json
import requests

PINATA_API_KEY = "ea4c8fdad5bc8f231e49"
PINATA_SECRET_API_KEY = "f24a66e6ea330adb4df4b6fd7c6b839e92e89cdd362260202b76f74762a0d386"

def upload_to_ipfs(data: dict) -> str:
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()

    ipfs_hash = response.json()["IpfsHash"]
    return ipfs_hash
