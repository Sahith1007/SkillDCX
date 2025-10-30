# SkillDCX Deployment Guide

## Current Issue: Certificates Not Loading

The certificate loading error occurs because the **smart contracts have not been deployed yet** to Algorand TestNet.

### Error Details
- **Error**: "Error retrieving certificates: 503: Certification contract not deployed"
- **Cause**: Missing deployed contract information in `contracts/deployed_contracts.json`
- **Impact**: Cannot load, verify, or issue certificates

---

## Solution: Deploy Smart Contracts

### Prerequisites
1. **Python 3.8+** with dependencies:
   ```bash
   cd contracts
   pip install -r requirements.txt
   ```

2. **Algorand TestNet Account**:
   - Visit: https://bank.testnet.algorand.network/
   - Click "Create Account"
   - Save the 24-word mnemonic phrase
   - Fund the account with TestNet ALGO (minimum 0.5 ALGO)

### Deployment Steps

1. **Navigate to contracts directory**:
   ```bash
   cd C:\Users\Sahith\OneDrive\Desktop\SkillDCX\contracts
   ```

2. **Deploy contracts**:
   ```bash
   python deploy_contracts.py --mnemonic "your 24 word mnemonic phrase here"
   ```

   Or use environment variable:
   ```bash
   set DEPLOYER_MNEMONIC="your 24 word mnemonic phrase"
   python deploy_contracts.py
   ```

3. **Verify deployment**:
   - Check that `deployed_contracts.json` was created
   - Verify it contains non-zero app IDs
   - Note the TestNet explorer links in the output

4. **Restart backend**:
   ```bash
   cd ../backend
   # Stop current backend if running
   # Then restart:
   uvicorn main:app --reload --port 8000
   ```

5. **Test the frontend**:
   - Refresh the browser
   - Connect wallet
   - Navigate to "My Certificates"
   - Error should be resolved

---

## What Gets Deployed

The deployment script creates two smart contracts:

1. **Issuer Registry Contract**
   - Manages authorized certificate issuers
   - Stores issuer information
   - Controls who can issue certificates

2. **Certification Contract**
   - Issues certificates to users
   - Stores certificate data on-chain
   - Handles verification and revocation

---

## Temporary Workaround

A template `deployed_contracts.json` file has been created with placeholder values. This prevents backend crashes, but **certificates still won't work** until actual contracts are deployed.

---

## Next Steps After Deployment

1. **Add Authorized Issuers**:
   - Use issuer registry to authorize accounts
   - Only authorized issuers can issue certificates

2. **Issue Test Certificate**:
   - Test certificate issuance flow
   - Verify IPFS integration works

3. **Verify Certificates**:
   - Test verification endpoint
   - Check certificate display in UI

---

## Troubleshooting

### "Low balance" error
- Get more TestNet ALGO from https://bank.testnet.algorand.network/
- Send to your deployer address

### "Transaction failed" error
- Check network connectivity
- Verify mnemonic is correct
- Ensure account has sufficient ALGO

### Backend still shows 503
- Verify `deployed_contracts.json` exists in `contracts/` directory
- Check file contains non-zero app IDs
- Restart backend server

---

## File Locations

- Deployment script: `contracts/deploy_contracts.py`
- Contract definitions: `contracts/certification_contract.py`, `contracts/issuer_registry_contract.py`
- Deployment output: `contracts/deployed_contracts.json`
- Backend config: `backend/routes/contracts.py`
