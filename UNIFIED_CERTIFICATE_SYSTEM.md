# Unified Certificate System with 3-Layer Verification

Complete smart contract system for issuing NFT certificates on Algorand with integrated verification layers.

## Overview

This system combines three existing contracts into a unified solution with three layers of verification:

1. **Issuer Registry Verification** - Ensures only authorized issuers can mint certificates
2. **AI Verification** - Validates certificate data through backend AI endpoint
3. **IPFS Verification** - Confirms metadata hash exists and is accessible

Only after all three verifications pass will the NFT certificate be minted and recorded on-chain.

## Architecture

### Smart Contracts

#### `unified_certificate_contract.py`
Main smart contract combining:
- Issuer management (from `issuer_registry_contract.py`)
- Certificate issuance logic (from `certification_contract.py`)
- NFT minting integration (from `CertificateIssuer.py`)

**Features:**
- Integrated 3-layer verification in smart contract
- Soulbound NFT certificates (non-transferable)
- Admin controls for issuer management
- Certificate revocation support
- Complete audit trail on-chain

**State Schema:**
- **Global State:** admin, total_issuers, total_certificates, verification flags
- **Local State:** 
  - Issuer data: authorized, name, metadata, registration timestamp
  - Certificate data: cert_id, ipfs_hash, issuer, recipient, timestamp, active status, metadata, ai_verified flag, nft_asset_id

### Backend Services

#### `backend/routes/ai_verification.py`
AI verification endpoint at `/ai/verifyCertificate`

**Validation Checks:**
- Certificate ID format
- IPFS hash format (CID validation)
- Algorand address validity
- Metadata completeness
- Anomaly detection

**Response:**
```json
{
  "valid": true,
  "confidence": 0.95,
  "reason": "Certificate passed all AI verification checks"
}
```

#### `backend/services/certificate_minting_service.py`
Orchestration service for complete certificate issuance flow

**Methods:**
- `verify_issuer_authorization()` - Layer 1 verification
- `verify_certificate_with_ai()` - Layer 2 verification
- `verify_ipfs_hash()` - Layer 3 verification
- `mint_nft_certificate()` - Algorand NFT minting
- `record_certificate_on_chain()` - Smart contract recording
- `issue_certificate_full_flow()` - Complete orchestration

#### `backend/routes/mint_certificate.py`
API endpoints for certificate minting

**Endpoints:**
- `POST /mint/certificate` - Mint certificate with 3-layer verification
- `POST /mint/verify-layers` - Test verification layers without minting
- `GET /mint/status/{cert_id}` - Check minting status

## Deployment

### 1. Deploy Smart Contract

```bash
cd contracts
python deploy_unified_contract.py "your 25-word mnemonic"
```

Or use environment variable:
```bash
export DEPLOYER_MNEMONIC="your 25-word mnemonic"
python deploy_unified_contract.py --use-env
```

This will:
- Compile the unified certificate contract
- Deploy to Algorand TestNet
- Update `deployed_contracts.json` with app ID and address
- Display explorer link for verification

### 2. Configure Backend

Update `.env` file:
```env
ALGOD_TOKEN=
ALGOD_ADDRESS=https://testnet-api.algonode.cloud
BACKEND_URL=http://localhost:8000
DEPLOYER_MNEMONIC=your 25-word mnemonic
PINATA_API_KEY=your_pinata_key
PINATA_API_SECRET=your_pinata_secret
```

### 3. Start Backend Server

```bash
cd backend
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

## Usage

### Step 1: Add Authorized Issuer (Admin Only)

```python
from algosdk import transaction, account
from algosdk.v2client import algod

client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
app_id = 123456  # Your deployed app ID

# Admin adds issuer
app_args = [
    "add_issuer".encode(),
    issuer_address.encode(),
    "University Name".encode(),
    "https://university.edu/metadata".encode()
]

txn = transaction.ApplicationCallTxn(
    sender=admin_address,
    sp=client.suggested_params(),
    index=app_id,
    on_complete=transaction.OnComplete.NoOpOC,
    app_args=app_args
)

signed_txn = txn.sign(admin_private_key)
tx_id = client.send_transaction(signed_txn)
```

### Step 2: Upload Certificate to IPFS

```bash
curl -X POST http://localhost:8000/issue/certificate \
  -H "Content-Type: application/json" \
  -d '{
    "courseName": "Blockchain Development",
    "studentName": "John Doe",
    "issueDate": "2025-10-30",
    "issuerName": "SkillDCX University"
  }'
```

Response:
```json
{
  "status": "success",
  "ipfs_hash": "QmX...abc123"
}
```

### Step 3: Mint Certificate with 3-Layer Verification

```bash
curl -X POST http://localhost:8000/mint/certificate \
  -H "Content-Type: application/json" \
  -d '{
    "issuer_private_key": "YOUR_ISSUER_PRIVATE_KEY",
    "cert_id": "CERT-2025-001",
    "recipient_address": "ALGORAND_ADDRESS_58_CHARS",
    "certificate_metadata": {
      "courseName": "Blockchain Development",
      "studentName": "John Doe",
      "issueDate": "2025-10-30"
    },
    "ipfs_hash": "QmX...abc123"
  }'
```

Response:
```json
{
  "success": true,
  "cert_id": "CERT-2025-001",
  "verification_layers": {
    "issuer_registry": {
      "passed": true,
      "message": "Issuer authorized"
    },
    "ai_verification": {
      "passed": true,
      "confidence": 0.95,
      "reason": "Certificate passed all AI verification checks"
    },
    "ipfs_verification": {
      "passed": true,
      "message": "IPFS hash verified"
    }
  },
  "nft_asset_id": 789012,
  "transaction_id": "ABC123...",
  "message": "Certificate issued successfully with 3-layer verification"
}
```

### Step 4: Test Verification Layers

```bash
curl -X POST http://localhost:8000/mint/verify-layers \
  -H "Content-Type: application/json" \
  -d '{
    "issuer_private_key": "YOUR_ISSUER_PRIVATE_KEY",
    "cert_id": "CERT-2025-001",
    "recipient_address": "ALGORAND_ADDRESS",
    "certificate_metadata": {...},
    "ipfs_hash": "QmX...abc123"
  }'
```

This tests all layers WITHOUT minting - useful for debugging.

## Verification Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Certificate Issuance                      │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Issuer Registry Verification                       │
│  - Check if issuer is authorized in smart contract          │
│  - Read issuer's local state                                │
│  - Verify authorization flag = 1                            │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼ (if authorized)
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: AI Verification                                    │
│  - POST to /ai/verifyCertificate                            │
│  - Validate cert_id, addresses, IPFS hash, metadata         │
│  - Check for anomalies and completeness                     │
│  - Return confidence score                                   │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼ (if valid)
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: IPFS Verification                                  │
│  - GET /verify/certificate/{ipfs_hash}                      │
│  - Verify hash exists on IPFS                               │
│  - Confirm metadata is accessible                           │
│  - Return certificate data                                   │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼ (if verified)
┌─────────────────────────────────────────────────────────────┐
│  NFT MINTING                                                 │
│  - Create Algorand Standard Asset (ASA)                     │
│  - Set total=1, decimals=0 (NFT)                            │
│  - Freeze=None, Clawback=None (Soulbound)                   │
│  - Transfer to recipient                                     │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼ (if minted)
┌─────────────────────────────────────────────────────────────┐
│  SMART CONTRACT RECORDING                                    │
│  - Call unified_certificate_contract                         │
│  - Store all certificate data on-chain                      │
│  - Record NFT asset ID                                       │
│  - Mark AI verification flag                                 │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                        ✓ COMPLETE
```

## Smart Contract Methods

### Admin Methods
- `add_issuer` - Add authorized issuer (admin only)
- `remove_issuer` - Revoke issuer authorization (admin only)
- `transfer_admin` - Transfer admin rights (admin only)
- `toggle_ai` - Toggle AI verification requirement (admin only)

### Issuer Methods
- `issue` - Issue certificate with all verifications
- `revoke` - Revoke certificate (issuer or admin)

### Query Methods
- `check_issuer` - Check if address is authorized issuer
- `verify` - Verify certificate authenticity
- `get_info` - Get certificate information

## Frontend Integration

The `deployed_contracts.json` file contains all contract addresses needed for frontend integration:

```json
{
  "unified_certificate_app_id": 123456,
  "unified_certificate_address": "app_123456",
  "network": "TestNet",
  "algod_address": "https://testnet-api.algonode.cloud",
  "deployer_address": "ALGORAND_ADDRESS...",
  "contract_version": "1.0.0",
  "features": [
    "3-layer verification",
    "Issuer registry",
    "AI verification",
    "IPFS verification",
    "NFT minting"
  ]
}
```

## API Endpoints Summary

### Certificate Issuance
- `POST /issue/certificate` - Upload to IPFS
- `POST /mint/certificate` - Mint with 3-layer verification
- `POST /mint/verify-layers` - Test verification without minting
- `GET /mint/status/{cert_id}` - Check status

### AI Verification
- `POST /ai/verifyCertificate` - AI validation
- `POST /ai/verifyCertificate/mock` - Mock endpoint (testing)
- `GET /ai/health` - Health check

### Certificate Verification
- `GET /verify/certificate/{ipfs_hash}` - Verify IPFS hash

## Security Features

1. **Issuer Authorization**: Only admin-approved issuers can mint
2. **AI Validation**: ML-based anomaly detection and validation
3. **IPFS Verification**: Ensures metadata integrity
4. **Soulbound NFTs**: Non-transferable certificates
5. **On-chain Audit Trail**: All actions recorded on Algorand
6. **Multi-signature Support**: Admin operations can require multiple signatures

## Testing

Run the test script:
```bash
python test_unified_system.py
```

This will:
- Test all 3 verification layers
- Simulate certificate minting
- Verify smart contract interactions
- Generate test reports

## Troubleshooting

### Contract Deployment Fails
- Check account balance (need ~0.5 ALGO)
- Verify mnemonic is correct (25 words)
- Ensure PyTeal is installed: `pip install pyteal`

### Verification Layer Fails
- **Layer 1**: Ensure issuer is added via `add_issuer` method
- **Layer 2**: Check AI endpoint is running at `/ai/verifyCertificate`
- **Layer 3**: Verify IPFS hash exists and is accessible

### NFT Minting Fails
- Recipient must opt-in to receive asset
- Check issuer has sufficient ALGO balance
- Verify asset name/unit name within character limits

## Future Enhancements

- [ ] Multi-chain support (Ethereum, Polygon)
- [ ] Real ML model integration for AI verification
- [ ] Batch certificate issuance
- [ ] Certificate templates system
- [ ] QR code generation for verification
- [ ] Mobile app integration
- [ ] Analytics dashboard

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- GitHub Issues: [Your Repo]
- Documentation: [Your Docs]
- Discord: [Your Community]
