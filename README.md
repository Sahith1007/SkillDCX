# SkillDCX Start Application

# Quick start (recommended)
.\start.ps1

# Manual start
# Terminal 1 - Backend:
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend:
cd frontend
npm run dev
📍 URLs
Frontend: http://localhost:3000
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs
TestNet Faucet: https://bank.testnet.algorand.network/
🔧 Setup Commands
# Install frontend
cd frontend
npm install

# Install backend
cd backend
pip install -r requirements.txt

# Create .env
cd frontend
copy .env.example .env.local
📜 Deploy Contracts
cd contracts

# Get TestNet ALGO first from faucet!

# Deploy
python deploy_contracts.py --mnemonic "your 24 words..."

# Copy to backend
copy deployed_contracts.json ..\backend\
# Key Features
# Navigation
Home - / - Dashboard and overview
My Certificates - /my-certificates - View your certificates
AI Mentor - /ai-mentor - Get skill recommendations
Issue - /issue - Issue certificates (requires auth)
Verify - /verify - Verify certificates
Profile - /profile - User profile
# Wallet
Connect: Click "Connect Wallet" in navbar
View: Shows address, balance, network
Disconnect: Click dropdown → Disconnect
# AI Mentor
Add skills (e.g., python, react, blockchain)
Add focus areas (optional)
Click "Get AI Recommendations"
View personalized courses
# API Endpoints
Wallet
POST /wallet/connect - Connect wallet
POST /wallet/disconnect - Disconnect wallet
GET /wallet/status/{address} - Get status
# Contracts
POST /contracts/verify - Verify certificate
GET /contracts/certificate/{address} - Get certificate info
GET /contracts/certificates/{address} - Get all certificates
GET /contracts/issuer/{address}/status - Check issuer status
# AI
POST /ai/recommend - Get skill recommendations
POST /ai/chat - Chat-based recommendations
POST /ai/mentor - Get course recommendations
# Quick Fixes
"Connection failed"
Check backend is running
Verify .env.local has correct URL
"Wallet not connecting"
Install Pera Wallet mobile app
Switch to TestNet in app
Scan QR code
"No certificates"
You may not have any yet
Deploy contracts first
Issue test certificate
"Contract not found"
Deploy contracts
Copy deployed_contracts.json to backend
Restart backend
# 💡 Pro Tips
Always use TestNet for development
Keep Pera Wallet app open during connection
Check browser console for errors
Use backend API docs for testing
Deploy contracts before testing frontend
Restart backend after contract deployment
# Tech Stack
Frontend: Next.js 15, React 19, TailwindCSS
Backend: FastAPI, Python 3.8+
Blockchain: Algorand TestNet, PyTeal
Wallet: Pera Wallet SDK
UI: shadcn/ui, Framer Motion

# Quick Start in 3 Steps:
Run .\start.ps1
Visit http://localhost:3000
Click "Connect Wallet"
That's it! 🚀
# Workflow

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
