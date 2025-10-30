# Testing Quick Start Guide

## ✅ Current Status

- **Smart Contract**: ✅ Deployed (App ID: 748842503)
- **Backend**: ⏸️ Need to start
- **Frontend**: ⏸️ Need to start

## 🚀 Run Tests Now

### Step 1: Start Backend

```bash
cd backend
npm install  # if not already installed
npm start
```

Backend should start on **http://localhost:8000**

### Step 2: Run Test Suite

Open a new terminal:

```bash
cd contracts
python test_verification_flows.py
```

This will test:
- ✅ Backend connectivity
- ✅ Free verification (queue)
- ✅ Queue status check
- ✅ Manual approval flow
- ✅ Instant verification (paid)
- ✅ Invalid certificate rejection
- ✅ On-chain state verification
- ✅ NFT existence on blockchain

### Step 3: Manual Tests (Optional)

#### Test On-Chain State

```powershell
# Check contract exists
Invoke-RestMethod -Uri "https://testnet-api.algonode.cloud/v2/applications/748842503"

# Check deployer balance
Invoke-RestMethod -Uri "https://testnet-api.algonode.cloud/v2/accounts/HNTEOSL5NPTVES7GWQ3TXE3FFCTNT337H7ZNEIBO2EAYMZWKN2ZGUL742Q"
```

#### Test Backend Endpoints

```powershell
# Get pricing
Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/verification/pricing"

# Request free verification
$body = @{
    cert_id = "TEST-001"
    ipfs_hash = "QmTest123"
    student_name = "Test User"
    course_name = "Test Course"
    recipient_address = "HNTEOSL5NPTVES7GWQ3TXE3FFCTNT337H7ZNEIBO2EAYMZWKN2ZGUL742Q"
    instant_verification = $false
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/verification/request" -Body $body -ContentType "application/json"

# Check queue
Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/verification/queue/TEST-001"

# Approve (admin)
$approveBody = @{
    cert_id = "TEST-001"
    approved = $true
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/verification/manual" -Body $approveBody -ContentType "application/json"
```

## 📋 Test Checklist

### Backend Tests
- [ ] Backend starts without errors
- [ ] Pricing endpoint returns correct data
- [ ] Free verification adds to queue
- [ ] Queue status returns pending certificate
- [ ] Manual approval mints NFT
- [ ] Instant verification works with payment
- [ ] Invalid certificate is rejected

### Smart Contract Tests  
- [ ] Contract exists on-chain (App ID: 748842503)
- [ ] Global state has correct entries
- [ ] Can query contract state
- [ ] Issuer is authorized (if added)

### NFT Tests
- [ ] NFT is created on blockchain
- [ ] NFT has correct metadata
- [ ] NFT appears on AlgoExplorer
- [ ] NFT follows ARC-69 standard

### Frontend Tests (Manual)
- [ ] Modal opens correctly
- [ ] Can select free verification
- [ ] Can select instant verification
- [ ] Shows queue position for free
- [ ] Shows success for instant
- [ ] Links to AlgoExplorer work

## 🐛 Common Issues

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F

# Reinstall dependencies
cd backend
rm -rf node_modules
npm install
```

### Test failures
- **"Backend not running"**: Start backend first (Step 1)
- **"Contract not found"**: Check APP_ID in test file
- **"NFT not found"**: Wait a few seconds for blockchain confirmation
- **"DEPLOYER_MNEMONIC not set"**: Set environment variable

### Environment variable not persisting
```powershell
# Set for current session
$env:DEPLOYER_MNEMONIC="your 25-word mnemonic"

# Or add to test_account.txt and load in script
```

## 📊 Expected Test Output

```
╔════════════════════════════════════════════════════════════════════╗
║               INSTANT VERIFICATION TEST SUITE                      ║
╚════════════════════════════════════════════════════════════════════╝

======================================================================
TEST: Backend Connectivity Check
======================================================================
✓ PASS: Backend is running
  Instant verification fee: 1 ALGO
  Revenue split: {'verifier': '60%', 'platform': '40%'}

======================================================================
TEST: Free Verification Request (Pending Queue)
======================================================================
✓ PASS: Certificate added to queue
  Certificate ID: TEST-FREE-001
  Queue position: #1
  Estimated time: 1-2 business days

[... more tests ...]

======================================================================
TEST SUMMARY
======================================================================
Total Tests:   9
✓ Passed:      8
✗ Failed:      0
⚠ Skipped:     1
Success Rate:  88.9%
======================================================================
```

## 🔧 Debugging

### View Backend Logs
Backend will show request logs in terminal:
```
[Verification Request] Certificate TEST-001, Instant: false
[Mint NFT] Layer 1: Issuer registry check - delegated to smart contract
[Mint NFT] Layer 2: Running AI verification...
[Queue] Added certificate TEST-001 to verification queue (position 1)
```

### Check Blockchain Explorer
- Contract: https://testnet.algoexplorer.io/application/748842503
- Deployer: https://testnet.algoexplorer.io/address/HNTEOSL5NPTVES7GWQ3TXE3FFCTNT337H7ZNEIBO2EAYMZWKN2ZGUL742Q

### Query Contract State Directly
```python
from algosdk.v2client import algod
import base64

client = algod.AlgodClient('', 'https://testnet-api.algonode.cloud')
info = client.application_info(748842503)

for state in info['params']['global-state']:
    key = base64.b64decode(state['key']).decode('utf-8')
    value = state['value']
    print(f"{key}: {value}")
```

## 📞 Support

If tests fail:
1. Check backend is running on port 8000
2. Verify contract exists: App ID 748842503
3. Check deployer has enough ALGO (>0.5 ALGO)
4. Review backend logs for errors
5. Check INSTANT_VERIFICATION_GUIDE.md for details

## 🎯 Next Steps After Testing

Once all tests pass:

1. **Deploy Payment Contract**
   ```bash
   cd contracts
   python deploy_payment_contract.py
   ```

2. **Integrate Wallet**
   - Add Pera Wallet SDK to frontend
   - Update `processPayment()` function
   - Test real payments

3. **Add Authentication**
   - Protect admin endpoints
   - Add JWT middleware
   - Test unauthorized access

4. **Production Checklist**
   - [ ] All tests passing
   - [ ] Payment contract deployed
   - [ ] Wallet integration complete
   - [ ] Admin auth implemented
   - [ ] Email notifications setup
   - [ ] Database for queue (not in-memory)
   - [ ] Rate limiting added
   - [ ] Error monitoring setup
   - [ ] Deploy to MainNet
