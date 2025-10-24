# SkillDCX - Quick Reference Card

## 🚀 Start Application

```powershell
# Quick start (recommended)
.\start.ps1

# Manual start
# Terminal 1 - Backend:
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend:
cd frontend
npm run dev
```

## 📍 URLs

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- TestNet Faucet: https://bank.testnet.algorand.network/

## 🔧 Setup Commands

```powershell
# Install frontend
cd frontend
npm install

# Install backend
cd backend
pip install -r requirements.txt

# Create .env
cd frontend
copy .env.example .env.local
```

## 📜 Deploy Contracts

```powershell
cd contracts

# Get TestNet ALGO first from faucet!

# Deploy
python deploy_contracts.py --mnemonic "your 24 words..."

# Copy to backend
copy deployed_contracts.json ..\backend\
```

## 🎯 Key Features

### Navigation
- **Home** - `/` - Dashboard and overview
- **My Certificates** - `/my-certificates` - View your certificates
- **AI Mentor** - `/ai-mentor` - Get skill recommendations
- **Issue** - `/issue` - Issue certificates (requires auth)
- **Verify** - `/verify` - Verify certificates
- **Profile** - `/profile` - User profile

### Wallet
- Connect: Click "Connect Wallet" in navbar
- View: Shows address, balance, network
- Disconnect: Click dropdown → Disconnect

### AI Mentor
1. Add skills (e.g., python, react, blockchain)
2. Add focus areas (optional)
3. Click "Get AI Recommendations"
4. View personalized courses

## 🔌 API Endpoints

### Wallet
- `POST /wallet/connect` - Connect wallet
- `POST /wallet/disconnect` - Disconnect wallet
- `GET /wallet/status/{address}` - Get status

### Contracts
- `POST /contracts/verify` - Verify certificate
- `GET /contracts/certificate/{address}` - Get certificate info
- `GET /contracts/certificates/{address}` - Get all certificates
- `GET /contracts/issuer/{address}/status` - Check issuer status

### AI
- `POST /ai/recommend` - Get skill recommendations
- `POST /ai/chat` - Chat-based recommendations
- `POST /ai/mentor` - Get course recommendations

## 🐛 Quick Fixes

### "Connection failed"
- Check backend is running
- Verify .env.local has correct URL

### "Wallet not connecting"
- Install Pera Wallet mobile app
- Switch to TestNet in app
- Scan QR code

### "No certificates"
- You may not have any yet
- Deploy contracts first
- Issue test certificate

### "Contract not found"
- Deploy contracts
- Copy deployed_contracts.json to backend
- Restart backend

## 📁 Important Files

### Frontend
- `frontend/.env.local` - Environment config
- `frontend/contexts/wallet-context.tsx` - Wallet state
- `frontend/components/ConnectWalletButton.jsx` - Wallet UI

### Backend
- `backend/main.py` - FastAPI app
- `backend/routes/wallet.py` - Wallet endpoints
- `backend/routes/contracts.py` - Contract endpoints
- `backend/routes/ai_recommender.py` - AI endpoints
- `backend/deployed_contracts.json` - Contract addresses

### Contracts
- `contracts/certification_contract.py` - Certificate contract
- `contracts/issuer_registry_contract.py` - Issuer registry
- `contracts/deploy_contracts.py` - Deployment script

## 💡 Pro Tips

1. Always use TestNet for development
2. Keep Pera Wallet app open during connection
3. Check browser console for errors
4. Use backend API docs for testing
5. Deploy contracts before testing frontend
6. Restart backend after contract deployment

## 🔑 Environment Variables

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ALGOD_SERVER=https://testnet-api.algonode.cloud
NEXT_PUBLIC_NETWORK=TestNet
```

## 📊 Tech Stack

- **Frontend**: Next.js 15, React 19, TailwindCSS
- **Backend**: FastAPI, Python 3.8+
- **Blockchain**: Algorand TestNet, PyTeal
- **Wallet**: Pera Wallet SDK
- **UI**: shadcn/ui, Framer Motion

## 🆘 Need Help?

1. Check `INTEGRATION_GUIDE.md` for detailed setup
2. Read `PROJECT_SUMMARY.md` for overview
3. Visit Algorand Discord: https://discord.gg/algorand
4. Check API docs: http://localhost:8000/docs

---

**Quick Start in 3 Steps:**
1. Run `.\start.ps1`
2. Visit http://localhost:3000
3. Click "Connect Wallet"

**That's it!** 🚀
