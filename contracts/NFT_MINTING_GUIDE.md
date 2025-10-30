# SkillDCX Certificate NFT Minting System

## 🎯 Overview

This system mints certificates as NFTs on Algorand blockchain with **3-layer verification** to prevent fake certificates.

## 🏗️ Architecture

```
┌─────────────┐
│  Frontend   │ → User clicks "Mint Certificate NFT"
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Backend API   │ → POST /api/certificates/mint
└──────┬──────────┘
       │
       ├─────→ Layer 1: Check issuer in registry
       ├─────→ Layer 2: AI verification
       ├─────→ Layer 3: IPFS hash verification
       │
       ▼
┌───────────────────┐
│  Python Script    │ → mint_certificate_nft.py
└──────┬────────────┘
       │
       ├─────→ Create Algorand ASA (NFT)
       └─────→ Call smart contract's issue() method
                │
                ▼
        ┌──────────────────┐
        │ Smart Contract   │ → Unified Certificate Contract
        │  (App ID: 748842503) │
        └──────────────────┘
```

## 📦 Deployed Contract

- **Network**: Algorand TestNet
- **Application ID**: 748842503
- **Deployer Address**: HNTEOSL5NPTVES7GWQ3TXE3FFCTNT337H7ZNEIBO2EAYMZWKN2ZGUL742Q
- **Explorer**: https://testnet.algoexplorer.io/application/748842503

## 🔐 3-Layer Verification System

### Layer 1: Issuer Registry ✅
- Only whitelisted issuers can mint certificates
- Verified in smart contract: `check_issuer_authorized()`
- Status: **Deployed & Active**

### Layer 2: AI Verification ✅
- Backend validates certificate data consistency
- Checks student name, course name, metadata
- Status: **Implemented** (placeholder - integrate your AI service)

### Layer 3: IPFS Hash Verification ✅
- Confirms certificate metadata exists on IPFS
- Validates hash format and accessibility
- Status: **Implemented** (placeholder - integrate IPFS gateway)

## 🚀 Quick Start

### 1. Environment Setup

Add to `.env`:
```bash
DEPLOYER_MNEMONIC="your 25-word mnemonic phrase"
DEPLOYER_ADDRESS="HNTEOSL5NPTVES7GWQ3TXE3FFCTNT337H7ZNEIBO2EAYMZWKN2ZGUL742Q"
```

### 2. Add Authorized Issuer (if needed)

```bash
cd contracts
python add_issuer.py
```

This adds your deployer address as an authorized issuer.

### 3. Start Backend

```bash
cd backend
npm install
npm start
```

Backend will run on http://localhost:8000

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on http://localhost:3000

## 🪙 How to Mint a Certificate NFT

### Method 1: Frontend Button

Import and use the `MintCertificateButton` component:

```tsx
import MintCertificateButton from "@/components/MintCertificateButton";

export default function CertificatePage() {
  const certificateData = {
    cert_id: "CERT-2025-001",
    ipfs_hash: "QmYourIPFSHash...",
    student_name: "Alice Johnson",
    course_name: "Blockchain Development",
    recipient_address: "ALGORAND_ADDRESS_HERE",
    timestamp: new Date().toISOString()
  };

  return (
    <MintCertificateButton 
      certificateData={certificateData}
      onSuccess={(result) => {
        console.log("Minted NFT:", result.nft_asset_id);
      }}
    />
  );
}
```

### Method 2: Backend API

```bash
curl -X POST http://localhost:8000/api/certificates/mint \
  -H "Content-Type: application/json" \
  -d '{
    "cert_id": "CERT-2025-001",
    "ipfs_hash": "QmExample123...",
    "student_name": "Alice Johnson",
    "course_name": "Blockchain Development",
    "recipient_address": "ALGORAND_ADDRESS_HERE"
  }'
```

### Method 3: Python Script

```bash
cd contracts
python mint_certificate_nft.py
```

Edit the `example_cert` data in the script before running.

## 📂 File Structure

```
contracts/
├── unified_certificate_contract.py   # PyTEAL smart contract
├── deploy_unified_contract.py        # Deployment script
├── add_issuer.py                     # Add authorized issuer
├── mint_certificate_nft.py           # Mint NFT + issue certificate
└── deployed_contracts.json           # Deployment info

backend/
├── controllers/
│   └── certificateController.js      # Mint endpoint logic
└── routes/
    └── index.js                      # API routes

frontend/
└── components/
    └── MintCertificateButton.tsx     # React mint button
```

## 🔧 Smart Contract Methods

### `add_issuer`
- **Caller**: Admin only
- **Args**: `[method, issuer_address, name, metadata]`
- **Purpose**: Add authorized issuer

### `issue`
- **Caller**: Authorized issuer only
- **Args**: `[method, cert_id, ipfs_hash, recipient_address, metadata, ai_verified_flag, nft_asset_id]`
- **Purpose**: Issue certificate with 3-layer verification

### `verify`
- **Caller**: Anyone
- **Args**: `[method, recipient_address, expected_ipfs_hash]`
- **Purpose**: Verify certificate validity

### `revoke`
- **Caller**: Issuer or admin
- **Args**: `[method, recipient_address]`
- **Purpose**: Revoke a certificate

## 🎨 NFT Metadata Format

The NFT follows the **ARC-69** standard:

```json
{
  "standard": "arc69",
  "description": "Certificate NFT for Alice Johnson",
  "external_url": "ipfs://QmExample123...",
  "properties": {
    "course": "Blockchain Development",
    "issuer": "ISSUER_ADDRESS",
    "timestamp": "2025-01-30T00:00:00Z"
  }
}
```

## ✅ Success Response Example

```json
{
  "success": true,
  "nft_asset_id": 748842600,
  "transaction_id": "ABCD1234...",
  "contract_app_id": 748842503,
  "verification_layers": {
    "issuer_registry": true,
    "ai_verification": true,
    "ipfs_verification": true
  },
  "explorer_urls": {
    "transaction": "https://testnet.algoexplorer.io/tx/ABCD1234...",
    "nft": "https://testnet.algoexplorer.io/asset/748842600",
    "contract": "https://testnet.algoexplorer.io/application/748842503"
  }
}
```

## 🛡️ Security Features

1. **Soulbound NFTs**: No clawback address = non-transferable
2. **Issuer Registry**: Only authorized issuers can mint
3. **AI Verification**: Prevents inconsistent certificate data
4. **IPFS Verification**: Ensures metadata exists and is valid
5. **On-Chain Verification**: Immutable proof on Algorand blockchain

## 🔍 Verification Flow

Anyone can verify a certificate:

1. **Get NFT Asset ID** from certificate
2. **Check blockchain** for asset details
3. **Verify IPFS hash** matches certificate
4. **Call smart contract** verify method
5. **Confirm 3 layers** all passed

## 📊 Testing

### Test Certificate Minting

```bash
cd contracts
python mint_certificate_nft.py
```

Check the output for:
- NFT Asset ID
- Transaction ID
- Explorer URLs

### Verify on Blockchain

Visit: https://testnet.algoexplorer.io/application/748842503

Check global state for:
- `total_certificates`
- `total_issuers`
- Certificate data (prefixed with `cert_`)

## 🚨 Troubleshooting

### "Issuer not authorized" error
- Run `python add_issuer.py` to authorize your address
- Check `DEPLOYER_MNEMONIC` is set correctly

### "AI verification failed"
- Implement actual AI verification in `certificateController.js`
- Update `verifyWithAI()` function

### "IPFS hash verification failed"
- Ensure IPFS hash is valid and accessible
- Update `verifyIPFSHash()` to check actual IPFS gateway

### Network timeout
- Algorand TestNet can be slow - wait a few minutes
- Check https://algoexplorer.io/testnet for network status

## 🎓 Next Steps

1. **Integrate Real AI Verification**
   - Connect to your AI service
   - Add sophisticated certificate validation

2. **Implement IPFS Upload**
   - Upload certificate metadata to IPFS
   - Return hash for on-chain storage

3. **Add Frontend Wallet Connection**
   - Integrate Pera Wallet / MyAlgo Connect
   - Let recipients sign transactions

4. **Deploy to MainNet**
   - Test thoroughly on TestNet first
   - Update contract addresses
   - Fund deployer account with real ALGO

## 📞 Support

- Smart Contract Explorer: https://testnet.algoexplorer.io/application/748842503
- Algorand Developer Docs: https://developer.algorand.org
- PyTEAL Docs: https://pyteal.readthedocs.io

## 📄 License

MIT License - SkillDCX 2025
