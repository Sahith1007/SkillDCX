# Quick Start Guide - Unified Certificate System

Get your 3-layer verification certificate system running in minutes!

## Prerequisites

- Python 3.8+
- Node.js (for backend)
- Algorand account with test ALGO

## Step 1: Generate Test Accounts

```bash
cd contracts
python generate_test_account.py
```

This will generate:
- **Deployer account** (for deploying contracts)
- Address and 25-word mnemonic

**Important:** Save the mnemonic securely!

## Step 2: Fund Your Account

1. Copy your address from the output
2. Visit: https://testnet.algoexplorer.io/dispenser
3. Paste your address and get test ALGO (minimum 0.5 ALGO needed)
4. Wait for confirmation (~4 seconds)

## Step 3: Deploy Smart Contract

Using mnemonic directly:
```bash
python deploy_unified_contract.py "your 25-word mnemonic phrase here"
```

Or using environment variable (recommended):
```powershell
# PowerShell (Windows)
$env:DEPLOYER_MNEMONIC="your 25-word mnemonic phrase here"
python deploy_unified_contract.py --use-env
```

```bash
# Bash (Linux/Mac)
export DEPLOYER_MNEMONIC="your 25-word mnemonic phrase here"
python deploy_unified_contract.py --use-env
```

**Output:** Application ID and contract address will be saved to `deployed_contracts.json`

## Step 4: Configure Backend

Create or update `.env` file in `backend/` directory:

```env
# Algorand Configuration
ALGOD_TOKEN=
ALGOD_ADDRESS=https://testnet-api.algonode.cloud
BACKEND_URL=http://localhost:8000

# Deployer Account (for admin operations)
DEPLOYER_MNEMONIC=your 25-word mnemonic phrase here

# IPFS Configuration
PINATA_API_KEY=your_pinata_api_key
PINATA_API_SECRET=your_pinata_secret_api_key
```

## Step 5: Install Dependencies

### Python Dependencies
```bash
pip install pyteal algosdk fastapi uvicorn pydantic requests python-dotenv
```

### Backend Setup
```bash
cd backend
# Install if needed (Node.js backend)
npm install
```

## Step 6: Start Backend Server

```bash
cd backend
uvicorn main:app --reload
```

Server will start at: http://localhost:8000

## Step 7: Test the System

### 7.1 Generate Issuer Account
```bash
cd contracts
python generate_test_account.py
```
Save this mnemonic - this will be your **issuer account**.

### 7.2 Add Issuer (Admin Operation)

Create `add_issuer.py`:

```python
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
import json

# Load deployed contract
with open("deployed_contracts.json", "r") as f:
    contracts = json.load(f)
    app_id = contracts["unified_certificate_app_id"]

# Admin credentials
admin_mnemonic = "your admin mnemonic here"
admin_private_key = mnemonic.to_private_key(admin_mnemonic)
admin_address = account.address_from_private_key(admin_private_key)

# Issuer to add
issuer_address = "ISSUER_ADDRESS_HERE"
issuer_name = "SkillDCX University"
issuer_metadata = "https://skilldcx.com/issuer-profile"

# Connect to Algorand
client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
params = client.suggested_params()

# Create app call
app_args = [
    "add_issuer".encode(),
    issuer_address.encode(),
    issuer_name.encode(),
    issuer_metadata.encode()
]

txn = transaction.ApplicationCallTxn(
    sender=admin_address,
    sp=params,
    index=app_id,
    on_complete=transaction.OnComplete.NoOpOC,
    app_args=app_args
)

# Sign and send
signed_txn = txn.sign(admin_private_key)
tx_id = client.send_transaction(signed_txn)

print(f"✓ Issuer added! Transaction ID: {tx_id}")
print(f"View on explorer: https://testnet.algoexplorer.io/tx/{tx_id}")
```

Run:
```bash
python add_issuer.py
```

### 7.3 Upload Certificate to IPFS

```bash
curl -X POST http://localhost:8000/issue/certificate \
  -H "Content-Type: application/json" \
  -d "{
    \"courseName\": \"Blockchain Development\",
    \"studentName\": \"John Doe\",
    \"issueDate\": \"2025-10-30\",
    \"issuerName\": \"SkillDCX University\",
    \"grade\": \"A+\"
  }"
```

**Save the `ipfs_hash` from the response!**

### 7.4 Generate Recipient Account

```bash
python generate_test_account.py
```
Save the **address** - this is your recipient.

### 7.5 Mint Certificate with 3-Layer Verification

```bash
curl -X POST http://localhost:8000/mint/certificate \
  -H "Content-Type: application/json" \
  -d "{
    \"issuer_private_key\": \"YOUR_ISSUER_PRIVATE_KEY\",
    \"cert_id\": \"CERT-2025-001\",
    \"recipient_address\": \"RECIPIENT_ALGORAND_ADDRESS\",
    \"certificate_metadata\": {
      \"courseName\": \"Blockchain Development\",
      \"studentName\": \"John Doe\",
      \"issueDate\": \"2025-10-30\"
    },
    \"ipfs_hash\": \"QmYourIPFSHashHere\"
  }"
```

### 7.6 Test Verification Layers Only

```bash
curl -X POST http://localhost:8000/mint/verify-layers \
  -H "Content-Type: application/json" \
  -d "{
    \"issuer_private_key\": \"YOUR_ISSUER_PRIVATE_KEY\",
    \"cert_id\": \"CERT-2025-TEST\",
    \"recipient_address\": \"RECIPIENT_ADDRESS\",
    \"certificate_metadata\": {
      \"courseName\": \"Test Course\",
      \"studentName\": \"Test Student\",
      \"issueDate\": \"2025-10-30\"
    },
    \"ipfs_hash\": \"QmTestHash\"
  }"
```

This will test all 3 layers WITHOUT minting - perfect for debugging!

## Verification Flow Overview

```
Your Request
     ↓
┌─────────────────────────────┐
│ LAYER 1: Issuer Registry   │ ✓ Checks smart contract
└─────────────────────────────┘
     ↓
┌─────────────────────────────┐
│ LAYER 2: AI Verification    │ ✓ Validates certificate data
└─────────────────────────────┘
     ↓
┌─────────────────────────────┐
│ LAYER 3: IPFS Verification  │ ✓ Confirms hash exists
└─────────────────────────────┘
     ↓
┌─────────────────────────────┐
│ NFT Minting                 │ ✓ Creates soulbound NFT
└─────────────────────────────┘
     ↓
┌─────────────────────────────┐
│ On-chain Recording          │ ✓ Stores on Algorand
└─────────────────────────────┘
     ↓
   SUCCESS!
```

## API Endpoints Reference

### Certificate Minting
- `POST /mint/certificate` - Full minting with verification
- `POST /mint/verify-layers` - Test verification only
- `GET /mint/status/{cert_id}` - Check status

### AI Verification
- `POST /ai/verifyCertificate` - AI validation
- `GET /ai/health` - Health check

### IPFS Operations
- `POST /issue/certificate` - Upload to IPFS
- `GET /verify/certificate/{ipfs_hash}` - Verify IPFS

## Troubleshooting

### "Issuer not authorized" Error
**Solution:** Run the `add_issuer.py` script to authorize your issuer address.

### "Insufficient balance" Error
**Solution:** Fund your account with more test ALGO from the dispenser.

### "IPFS hash not found" Error
**Solution:** Upload your certificate to IPFS first using `/issue/certificate` endpoint.

### "AI verification failed" Error
**Solution:** Check that:
- Certificate ID is > 5 characters
- IPFS hash starts with "Qm" or "bafy"
- Algorand addresses are 58 characters
- Metadata contains: `courseName`, `studentName`, `issueDate`

### Contract deployment fails
**Solution:** 
- Ensure account has >= 0.5 ALGO
- Check mnemonic is correct (25 words)
- Verify PyTeal is installed: `pip install pyteal`

## Next Steps

1. **Frontend Integration:** Use `deployed_contracts.json` in your frontend
2. **Batch Processing:** Modify minting service for multiple certificates
3. **Production Deployment:** Switch to MainNet (requires real ALGO)
4. **Custom AI Model:** Replace simulated AI with real ML model

## Support Resources

- Full Documentation: `UNIFIED_CERTIFICATE_SYSTEM.md`
- Contract Code: `contracts/unified_certificate_contract.py`
- Minting Service: `backend/services/certificate_minting_service.py`
- Algorand TestNet Explorer: https://testnet.algoexplorer.io
- Algorand Dispenser: https://testnet.algoexplorer.io/dispenser

## Security Reminders

⚠️ **NEVER commit mnemonics or private keys to version control!**
⚠️ **Use environment variables for sensitive data**
⚠️ **This is TestNet - do not use real funds**
⚠️ **For production, conduct a security audit**

---

**Ready to mint your first verified NFT certificate? Let's go! 🚀**
