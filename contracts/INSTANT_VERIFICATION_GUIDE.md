# Instant Verification System - Complete Guide

## 🎯 Overview

The **Instant Verification System** allows users to choose between:

1. **Free Verification** (Normal) - Goes to manual verification queue (1-2 business days)
2. **Instant Verification** (Paid) - Pay 1 ALGO to mint certificate NFT immediately

## 💰 Revenue Model

When users pay for instant verification:
- **60%** → Verifier Pool
- **40%** → Platform Treasury

## 🏗️ Architecture

```
┌──────────────┐
│   Frontend   │ → User chooses verification option
└──────┬───────┘
       │
       ├─────→ Free Verification
       │       │
       │       ├─ AI Verification
       │       ├─ IPFS Verification  
       │       └─→ Add to Queue (1-2 days)
       │
       └─────→ Instant Verification (1 ALGO)
               │
               ├─ 1. Connect wallet
               ├─ 2. Pay 1 ALGO
               ├─ 3. Payment contract splits funds:
               │     • 0.6 ALGO → Verifier Pool
               │     • 0.4 ALGO → Platform Treasury
               ├─ 4. Backend verifies payment
               ├─ 5. Mark as manually verified
               └─→ 6. Mint NFT instantly 🚀
```

## 📦 New Components

### 1. Payment Smart Contract

**File**: `instant_verification_payment_contract.py`

**Features**:
- Accepts 1 ALGO payments
- Auto-splits revenue (60/40)
- Tracks payment status per user
- Admin can mark users as verified

**Methods**:
- `pay_instant` - User pays for instant verification
- `mark_verified` - Admin confirms verification complete
- `check_status` - Check if user paid and is verified
- `set_treasury` - Update treasury address
- `set_verifier_pool` - Update verifier pool address
- `update_fee` - Change instant verification fee

### 2. Updated Certificate Contract

**File**: `unified_certificate_contract.py` (updated)

**Changes**:
- Added `manual_verified_flag` parameter (8th arg)
- Requires manual verification = 1 to mint
- Stores `cert_manual_` flag in global state

**New Issue Args**: `[method, cert_id, ipfs_hash, recipient_address, metadata, ai_verified_flag, manual_verified_flag, nft_asset_id]`

### 3. Backend Verification Controller

**File**: `backend/controllers/verificationController.js`

**Endpoints**:

#### POST `/api/verification/request`
Request certificate minting (free or instant)

**Request Body**:
```json
{
  "cert_id": "CERT-2025-001",
  "ipfs_hash": "QmExample...",
  "student_name": "Alice Johnson",
  "course_name": "Blockchain Development",
  "recipient_address": "ALGORAND_ADDRESS",
  "instant_verification": false,  // or true
  "payment_tx_id": "TX_ID"  // required if instant_verification = true
}
```

**Free Response** (202):
```json
{
  "success": true,
  "type": "queued",
  "cert_id": "CERT-2025-001",
  "queue_position": 3,
  "estimated_time": "1-2 business days",
  "message": "Certificate added to verification queue..."
}
```

**Instant Response** (200):
```json
{
  "success": true,
  "type": "instant",
  "nft_asset_id": 748842600,
  "transaction_id": "ABCD1234...",
  "contract_app_id": 748842503,
  "message": "Certificate minted instantly! 🚀",
  "explorer_urls": {
    "nft": "https://testnet.algoexplorer.io/asset/748842600",
    "transaction": "https://testnet.algoexplorer.io/tx/ABCD1234..."
  }
}
```

#### GET `/api/verification/queue/:cert_id?`
Check queue status

**Response**:
```json
{
  "success": true,
  "status": "pending",
  "cert_id": "CERT-2025-001",
  "queue_position": 3,
  "created_at": "2025-01-30T00:00:00Z"
}
```

#### POST `/api/verification/manual`
Manually approve certificate (Admin only)

**Request**:
```json
{
  "cert_id": "CERT-2025-001",
  "approved": true
}
```

**Response**:
```json
{
  "success": true,
  "action": "approved_and_minted",
  "nft_asset_id": 748842601,
  "transaction_id": "XYZ789..."
}
```

#### GET `/api/verification/pricing`
Get instant verification pricing info

**Response**:
```json
{
  "success": true,
  "pricing": {
    "instant_verification_fee": 1,
    "currency": "ALGO",
    "revenue_split": {
      "verifier": "60%",
      "platform": "40%"
    },
    "benefits": [
      "Immediate minting",
      "Skip verification queue",
      "Priority support"
    ]
  }
}
```

### 4. Frontend Modal

**File**: `frontend/components/InstantVerificationModal.tsx`

**Usage**:
```tsx
import InstantVerificationModal from "@/components/InstantVerificationModal";

export default function CertificatePage() {
  const [showModal, setShowModal] = useState(false);

  const certificateData = {
    cert_id: "CERT-2025-001",
    ipfs_hash: "QmExample...",
    student_name: "Alice Johnson",
    course_name: "Blockchain Development",
    recipient_address: "ALGORAND_ADDRESS"
  };

  return (
    <>
      <button onClick={() => setShowModal(true)}>
        Mint Certificate
      </button>

      <InstantVerificationModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        certificateData={certificateData}
        onSuccess={(result) => {
          console.log("Minted:", result);
          // Update UI, send notification, etc.
        }}
      />
    </>
  );
}
```

## 🚀 Deployment Steps

### Step 1: Deploy Payment Contract

```bash
cd contracts
python instant_verification_payment_contract.py > instant_payment.teal

# Deploy using algod
python deploy_instant_payment.py
```

Update `PAYMENT_CONTRACT_APP_ID` in `backend/controllers/verificationController.js`.

### Step 2: Update Certificate Contract (Already Done)

The main contract has been updated with `manual_verified_flag`.

To redeploy with changes:
```bash
python deploy_unified_contract.py --use-env
```

Update `APP_ID` in relevant files.

### Step 3: Configure Treasury & Verifier Addresses

Set treasury and verifier pool addresses on payment contract:

```bash
python set_payment_addresses.py \
  --treasury "TREASURY_ADDRESS" \
  --verifier-pool "VERIFIER_POOL_ADDRESS"
```

### Step 4: Start Backend

```bash
cd backend
npm install
npm start
```

Backend will expose verification endpoints on port 8000.

### Step 5: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🔄 User Flows

### Flow 1: Free Verification

1. User fills certificate form
2. Clicks "Mint Certificate"
3. Modal opens → Selects "Free Verification"
4. Backend adds to queue
5. Admin reviews and approves in 1-2 days
6. Certificate mints
7. User gets notification

### Flow 2: Instant Verification (Paid)

1. User fills certificate form
2. Clicks "Mint Certificate"
3. Modal opens → Selects "Instant Verification (1 ALGO)"
4. Wallet connection prompt
5. User approves 1 ALGO payment
6. Payment splits automatically:
   - 0.6 ALGO → Verifier Pool
   - 0.4 ALGO → Platform
7. Backend verifies payment
8. Certificate mints **immediately**
9. User sees NFT Asset ID

## 👨‍💼 Admin Dashboard (TODO)

Create admin panel to manage verification queue:

**Features**:
- View pending certificates
- Approve/Reject with one click
- See payment history
- Track revenue splits

**Example Endpoint**:
```
GET /api/admin/queue → List all pending
POST /api/admin/approve/:cert_id → Approve
POST /api/admin/reject/:cert_id → Reject
```

## 💡 Integration Checklist

- [ ] Deploy payment contract
- [ ] Deploy updated certificate contract
- [ ] Set treasury & verifier pool addresses
- [ ] Integrate Algorand wallet (Pera/MyAlgo)
- [ ] Test free verification flow
- [ ] Test instant verification + payment
- [ ] Verify revenue split works
- [ ] Add email notifications
- [ ] Create admin dashboard
- [ ] Test on TestNet thoroughly
- [ ] Deploy to MainNet

## 🧪 Testing

### Test Free Verification

```bash
curl -X POST http://localhost:8000/api/verification/request \
  -H "Content-Type: application/json" \
  -d '{
    "cert_id": "TEST-001",
    "ipfs_hash": "QmTest123",
    "student_name": "Test User",
    "course_name": "Test Course",
    "recipient_address": "ALGORAND_ADDRESS",
    "instant_verification": false
  }'
```

### Test Queue Status

```bash
curl http://localhost:8000/api/verification/queue/TEST-001
```

### Test Manual Approval

```bash
curl -X POST http://localhost:8000/api/verification/manual \
  -H "Content-Type: application/json" \
  -d '{
    "cert_id": "TEST-001",
    "approved": true
  }'
```

## 🔐 Security Considerations

1. **Payment Verification**
   - Always verify payment transaction on-chain
   - Check amount >= fee
   - Confirm receiver is payment contract
   - Validate sender matches user

2. **Admin Access**
   - Protect manual approval endpoint
   - Add authentication middleware
   - Log all admin actions

3. **Queue Management**
   - Use database instead of in-memory (production)
   - Add rate limiting
   - Prevent duplicate submissions

4. **Revenue Split**
   - Monitor payment contract balance
   - Regular audits of splits
   - Alert if balance gets too high

## 📊 Revenue Tracking

Query payment contract global state:
- `total_payments` - Number of instant verifications
- `total_verifications` - Number completed

Calculate revenue:
```
Total Revenue = total_payments × 1 ALGO
Verifier Share = Total Revenue × 60%
Platform Share = Total Revenue × 40%
```

## 🎨 UI/UX Best Practices

1. **Clear Comparison**
   - Show both options side-by-side
   - Highlight instant benefits
   - Make pricing transparent

2. **Trust Signals**
   - Show revenue split
   - Display verification stats
   - Provide examples

3. **Payment Flow**
   - Clear wallet connection
   - Show transaction progress
   - Confirm after minting

4. **Queue Updates**
   - Email when certificate ready
   - Show estimated time
   - Allow checking status

## 📞 Support

- Payment Contract: (Deploy and add link)
- Certificate Contract: https://testnet.algoexplorer.io/application/748842503
- Backend API: http://localhost:8000/api/verification
- Algorand Docs: https://developer.algorand.org

## 📄 License

MIT License - SkillDCX 2025
