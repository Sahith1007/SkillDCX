# Upload & Mint Feature Setup Guide

## Overview
Complete automated certificate upload and NFT minting system with AI verification, IPFS storage, and Algorand blockchain integration.

## Architecture

```
User Upload → Backend (AI Verify) → IPFS → Algorand NFT → User Receives NFT
                ↓
              Queue (Free) or Instant (Paid)
```

## Files Created

### Backend
- `backend/controllers/uploadMintController.js` - Main upload & mint logic
- `backend/routes/upload.js` - API route definition
- `backend/services/ipfs_service.js` - Pinata IPFS integration
- `backend/.env.example` - Environment variables template

### Frontend (ui branch)
- `frontend/app/upload/page.tsx` - Upload page
- `frontend/src/components/UploadCertificateForm.tsx` - Upload form component
- `frontend/src/components/UploadCertificateForm.css` - Styles

### Contracts
- `contracts/mint_certificate_nft.py` - NFT minting script (existing)

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```powershell
cd backend
npm install multer
```

#### Configure Environment Variables
Copy `.env.example` to `.env` and fill in:
```env
PORT=5000

# Pinata IPFS (Get from https://app.pinata.cloud/)
PINATA_API_KEY=your_pinata_api_key_here
PINATA_SECRET_KEY=your_pinata_secret_api_key_here

# Algorand (existing)
DEPLOYER_MNEMONIC=your_25_word_mnemonic_here
```

#### Update Backend Server
The route is already registered in `backend/routes/index.js`:
```javascript
import uploadRoutes from "./upload.js";
router.use("/upload", uploadRoutes);
```

### 2. Frontend Setup (ui branch)

#### Switch to UI Branch
```powershell
git checkout ui
```

#### The upload page is available at:
- Route: `/upload`
- Component: `frontend/app/upload/page.tsx`
- Form: `frontend/src/components/UploadCertificateForm.tsx`

#### Add Navigation Link
Add to your main navigation (e.g., `frontend/components/Navigation.tsx`):
```tsx
<Link href="/upload">Upload Certificate</Link>
```

### 3. Test the System

#### Start Backend
```powershell
cd backend
npm run dev
```

#### Start Frontend
```powershell
cd frontend
npm run dev
```

#### Access Upload Form
Navigate to: `http://localhost:3000/upload`

## API Endpoint

### POST `/api/upload/certificate`

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `certificate`: File (PDF/PNG/JPG, max 10MB)
  - `wallet_address`: String (Algorand address)
  - `student_name`: String
  - `course_name`: String
  - `issuer_name`: String (optional)
  - `issue_date`: String (YYYY-MM-DD, optional)
  - `tier`: "free" or "fast_track"

**Response (Free Tier - Queued):**
```json
{
  "success": true,
  "type": "queued",
  "message": "Certificate uploaded successfully. Manual review in progress.",
  "queue_position": 3,
  "estimated_time": "1-2 business days",
  "metadata": {
    "cert_id": "CERT-1730269203456",
    "ipfs_hash": "QmXxx...",
    "file_ipfs": "QmYyy...",
    "ai_confidence": 0.85
  }
}
```

**Response (Fast Track - Instant):**
```json
{
  "success": true,
  "type": "instant",
  "message": "Certificate minted successfully! 🚀",
  "nft_asset_id": 123456789,
  "transaction_id": "ABCD1234...",
  "contract_app_id": 748842503,
  "explorer_urls": {
    "nft": "https://testnet.algoexplorer.io/asset/123456789",
    "transaction": "https://testnet.algoexplorer.io/tx/ABCD1234...",
    "contract": "https://testnet.algoexplorer.io/application/748842503"
  },
  "verification": {
    "ai_verified": true,
    "ai_confidence": 0.92,
    "ipfs_verified": true,
    "issuer_verified": true
  }
}
```

## Features

### AI Verification (Placeholder)
Current implementation uses basic validation. To integrate full AI:
1. Uncomment Python AI verifier call in `uploadMintController.js`
2. Use existing `contracts/ai_certificate_verifier.py`
3. Parse OCR results and confidence scores

### IPFS Storage
- Certificate file uploaded to IPFS via Pinata
- Metadata JSON uploaded to IPFS
- Returns IPFS hashes and gateway URLs

### Tiered System
- **Free Tier**: Queue for manual review (1-2 days)
- **Fast Track**: Instant AI verification + minting ($5)

### NFT Minting
Uses existing `contracts/mint_certificate_nft.py` with:
- Asset creation on Algorand
- IPFS metadata linking
- Contract state update
- Explorer URLs for verification

## Verification Flow

### Free Tier
1. Upload certificate → Backend
2. AI verification (confidence check)
3. Upload to IPFS (file + metadata)
4. Add to queue for manual review
5. Return queue position
6. (Later) Admin reviews and mints

### Fast Track
1. Upload certificate → Backend
2. AI verification (confidence check)
3. Upload to IPFS (file + metadata)
4. **Immediate minting** via Python script
5. Return NFT details and explorer links

## Security Considerations

1. **File Validation**
   - File type whitelist (PDF, PNG, JPG, JPEG)
   - Size limit (10MB)
   - Multer storage configuration

2. **API Rate Limiting**
   - TODO: Add rate limiting middleware
   - Prevent abuse of free tier

3. **Payment Integration**
   - TODO: Integrate payment gateway for fast track
   - Verify payment before instant minting

4. **Private Keys**
   - Store mnemonic in `.env`
   - Never expose in client-side code

## Testing

### Manual Test
1. Navigate to `/upload`
2. Upload a test certificate
3. Fill in required fields
4. Select "Free" tier
5. Submit and check queue response

### Fast Track Test
1. Same as above
2. Select "Fast Track" tier
3. Check for immediate NFT minting
4. Verify on Algorand TestNet explorer

## Future Enhancements

1. **Payment Integration**
   - Stripe/PayPal for fast track
   - Cryptocurrency payments

2. **Real Queue System**
   - Database for queue management
   - Admin dashboard for manual review

3. **AI Integration**
   - Full OCR + LLM verification
   - Confidence thresholds
   - Fraud detection

4. **Email Notifications**
   - Queue status updates
   - NFT minting confirmation
   - Explorer links

5. **Analytics Dashboard**
   - Upload statistics
   - Verification success rates
   - Revenue tracking

## Troubleshooting

### Backend won't start
- Check if multer is installed: `npm list multer`
- Verify PINATA_API_KEY in `.env`
- Check port 5000 is not in use

### Upload fails
- Check file size (< 10MB)
- Verify file type (PDF/PNG/JPG)
- Check CORS settings
- Inspect browser console

### IPFS upload fails
- Verify Pinata API keys
- Check Pinata account limits
- Test with Pinata API directly

### NFT minting fails
- Check DEPLOYER_MNEMONIC in `.env`
- Verify account has ALGO balance
- Check Python environment
- Verify contract APP_ID

## Support

For issues or questions:
1. Check backend logs
2. Check browser console
3. Verify all environment variables
4. Test with sample certificate

---

**Next Steps:**
1. Configure Pinata API keys
2. Test upload endpoint
3. Add payment integration
4. Deploy to production
