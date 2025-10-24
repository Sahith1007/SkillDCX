# SkillDCX - Complete Integration Guide

> Decentralized credential and learning platform built on Algorand

## 🎯 Project Overview

SkillDCX is a full-stack blockchain application that combines:
- **Algorand Smart Contracts** (PyTeal) for tamper-proof certificates
- **Pera Wallet** integration for secure blockchain authentication
- **AI-Powered Recommendations** for personalized learning paths
- **IPFS** for decentralized certificate storage
- **React + Next.js** frontend with modern UI components
- **FastAPI** backend with Algorand SDK integration

---

## 📁 Project Structure

```
SkillDCX/
├── frontend/                 # Next.js + React frontend
│   ├── app/                  # Next.js 13+ app directory
│   │   ├── layout.tsx        # Root layout with providers
│   │   ├── page.tsx          # Home page
│   │   ├── my-certificates/  # User certificates page
│   │   ├── ai-mentor/        # AI skill mentor page
│   │   ├── issue/            # Certificate issuance
│   │   ├── verify/           # Certificate verification
│   │   └── profile/          # User profile
│   ├── components/           # React components
│   │   ├── ConnectWalletButton.jsx
│   │   ├── SkillMentorAI.jsx
│   │   ├── MyCertificates.jsx
│   │   └── ui/               # shadcn UI components
│   ├── contexts/             # React contexts
│   │   └── wallet-context.tsx
│   ├── hooks/                # Custom hooks
│   │   └── useWallet.js
│   └── package.json
│
├── backend/                  # FastAPI backend
│   ├── main.py               # FastAPI app entry
│   ├── routes/               # API routes
│   │   ├── wallet.py         # Wallet connection endpoints
│   │   ├── contracts.py      # Smart contract interactions
│   │   ├── ai_recommender.py # AI mentor endpoints
│   │   ├── certificates.py   # Certificate management
│   │   └── verify.py         # Verification endpoints
│   └── requirements.txt
│
├── contracts/                # Algorand smart contracts
│   ├── certification_contract.py      # Certificate issuance/verification
│   ├── issuer_registry_contract.py    # Authorized issuer management
│   └── deploy_contracts.py            # Deployment script
│
└── docs/                     # Documentation
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.8+
- **Algorand Account** with TestNet funds
- **Git**

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd SkillDCX

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt

# Install contract dependencies
cd ../contracts
pip install pyteal algosdk
```

### 2. Frontend Configuration

Create `frontend/.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Algorand Configuration
NEXT_PUBLIC_ALGOD_SERVER=https://testnet-api.algonode.cloud
NEXT_PUBLIC_ALGOD_PORT=443
NEXT_PUBLIC_ALGOD_TOKEN=

# Network
NEXT_PUBLIC_NETWORK=TestNet

# IPFS Gateway
NEXT_PUBLIC_IPFS_GATEWAY=https://ipfs.io/ipfs/
```

### 3. Deploy Smart Contracts

```bash
cd contracts

# Get TestNet ALGO
# Visit: https://bank.testnet.algorand.network/
# Create account and fund it with TestNet ALGO

# Deploy contracts
python deploy_contracts.py --mnemonic "your 24 word mnemonic phrase here"

# Copy deployed contract info to backend
cp deployed_contracts.json ../backend/
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit: `http://localhost:3000`

---

## 🔗 Wallet Integration (Pera Wallet)

### Frontend Integration

The wallet integration uses the official Pera Wallet SDK:

**Key Components:**
- `ConnectWalletButton.jsx` - UI component for wallet connection
- `wallet-context.tsx` - React context managing wallet state
- `useWallet.js` - Custom hook (deprecated in favor of context)

**How It Works:**

1. **Connection Flow:**
   ```
   User clicks "Connect Wallet"
   → Pera Wallet modal opens
   → User approves connection
   → Frontend receives wallet address
   → Backend verifies on Algorand TestNet
   → Check if authorized issuer
   → Update UI state
   ```

2. **Usage in Components:**
   ```tsx
   import { useWallet } from '@/contexts/wallet-context'

   function MyComponent() {
     const { 
       isConnected, 
       address, 
       balance,
       connectWallet, 
       disconnectWallet,
       isAuthorizedIssuer 
     } = useWallet()

     return (
       <div>
         {isConnected ? (
           <p>Connected: {address}</p>
         ) : (
           <button onClick={connectWallet}>Connect</button>
         )}
       </div>
     )
   }
   ```

### Backend Integration

**Wallet Routes (`backend/routes/wallet.py`):**

- `POST /wallet/connect` - Connect wallet and verify on chain
- `POST /wallet/disconnect` - Disconnect wallet session
- `GET /wallet/status/{address}` - Check wallet connection status
- `GET /wallet/contracts` - Get deployed contract information

---

## 📜 Smart Contract Architecture

### 1. Certification Contract (`certification_contract.py`)

**Features:**
- Issue certificates with IPFS hash storage
- Verify certificate authenticity
- Revoke certificates (issuer only)
- Soulbound tokens (non-transferable)

**Key Methods:**
- `issue_certificate` - Issue new certificate to recipient
- `verify_certificate` - Verify certificate authenticity
- `revoke_certificate` - Revoke issued certificate
- `get_certificate_info` - Read certificate data

**State Schema:**
- **Global State:**
  - `total_certs` (uint) - Total certificates issued
  - `issuer_registry` (uint) - Issuer registry app ID

- **Local State (per user):**
  - `ipfs_hash` (bytes) - IPFS content hash
  - `issuer` (bytes) - Issuer address
  - `timestamp` (uint) - Issue timestamp
  - `active` (uint) - Certificate active status
  - `metadata` (bytes) - Additional metadata

### 2. Issuer Registry Contract (`issuer_registry_contract.py`)

**Features:**
- Manage authorized certificate issuers
- Admin-only issuer management
- Query issuer authorization status

**Key Methods:**
- `add_issuer` - Authorize new issuer (admin only)
- `remove_issuer` - Revoke issuer authorization (admin only)
- `check_issuer` - Check if address is authorized
- `transfer_admin` - Transfer admin rights

**State Schema:**
- **Global State:**
  - `admin` (bytes) - Admin address
  - `total_issuers` (uint) - Total authorized issuers

- **Local State (per issuer):**
  - `authorized` (uint) - Authorization status
  - `name` (bytes) - Issuer name
  - `metadata` (bytes) - Issuer metadata
  - `reg_timestamp` (uint) - Registration timestamp

---

## 🤖 AI Skill Mentor

The AI recommender provides personalized course suggestions based on user skills.

### Features

- **Skill-based Recommendations** - Suggest next skills to learn
- **Course Recommendations** - Find relevant courses (Coursera, Udemy)
- **Focus Areas** - Prioritize specific learning paths
- **Knowledge Graph** - Skill progression mapping

### API Endpoints (`backend/routes/ai_recommender.py`)

1. **POST `/ai/recommend`** - Get skill recommendations
   ```json
   {
     "skills": ["python", "react"],
     "top_k": 5
   }
   ```

2. **POST `/ai/chat`** - Chat-based skill extraction
   ```json
   {
     "message": "I know Python and want to learn web3",
     "top_k": 5
   }
   ```

3. **POST `/ai/mentor`** - Get course recommendations
   ```json
   {
     "skills": ["python", "blockchain"],
     "focus_areas": ["web3", "smart contracts"]
   }
   ```

### Frontend Component (`SkillMentorAI.jsx`)

- Add current skills
- Specify focus areas (optional)
- Get personalized recommendations
- View course details with links

---

## 📱 Key Features

### 1. Connect Wallet
- **Component:** `ConnectWalletButton.jsx`
- **Route:** Navbar (always visible)
- Pera Wallet integration
- Displays balance and network
- View on block explorer

### 2. My Certificates
- **Component:** `MyCertificates.jsx`
- **Route:** `/my-certificates`
- View all owned certificates
- Verify certificate authenticity
- View on IPFS and block explorer
- Refresh certificate list

### 3. AI Skill Mentor
- **Component:** `SkillMentorAI.jsx`
- **Route:** `/ai-mentor`
- Add current skills
- Set learning goals
- Get personalized recommendations
- Direct links to courses

### 4. Issue Certificate
- **Route:** `/issue`
- **Requires:** Authorized issuer role
- Upload certificate to IPFS
- Issue on-chain certificate
- Specify recipient and metadata

### 5. Verify Certificate
- **Route:** `/verify`
- Enter wallet address
- View all certificates
- Verify on-chain authenticity
- Check issuer and timestamp

---

## 🧪 Testing

### Test Wallet Connection

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Test endpoint
curl -X POST http://localhost:8000/wallet/connect \
  -H "Content-Type: application/json" \
  -d '{"address": "YOUR_ALGO_ADDRESS"}'
```

### Test AI Mentor

```bash
# Test the AI endpoint
python test_mentor_endpoint.py
```

### Test Smart Contracts

1. Deploy contracts (see deployment section)
2. Use Algorand TestNet explorer
3. Test issue/verify flow via frontend
4. Check transaction history

---

## 🔧 Troubleshooting

### Wallet Connection Issues

**Problem:** "Failed to connect wallet"
**Solution:**
- Ensure Pera Wallet app is installed
- Check if TestNet is selected
- Verify backend is running
- Check browser console for errors

### Smart Contract Issues

**Problem:** "Contract not deployed"
**Solution:**
- Run deployment script
- Verify `deployed_contracts.json` exists
- Copy file to backend directory
- Restart backend server

### AI Recommendations Not Working

**Problem:** No recommendations returned
**Solution:**
- Check backend logs
- Verify skills are in knowledge graph
- Try different skill names (lowercase)
- Check API endpoint in browser DevTools

---

## 📚 Additional Resources

### Algorand
- [Algorand Developer Docs](https://developer.algorand.org/)
- [PyTeal Documentation](https://pyteal.readthedocs.io/)
- [Algorand TestNet Faucet](https://bank.testnet.algorand.network/)

### Pera Wallet
- [Pera Wallet Connect Docs](https://github.com/perawallet/connect)
- [Integration Guide](https://docs.perawallet.app/)

### Frontend
- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [TailwindCSS](https://tailwindcss.com/)

### Backend
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Algorand Python SDK](https://py-algorand-sdk.readthedocs.io/)

---

## 🎨 UI/UX Design

The application uses:
- **Dark theme** with futuristic gradient accents
- **TailwindCSS** for styling
- **shadcn/ui** for components
- **Framer Motion** for animations
- **Lucide React** for icons

Color scheme:
- Primary: Blue (#3B82F6) to Purple (#A855F7) gradients
- Background: Dark gray
- Accents: Neon blue, purple highlights
- Text: White/gray hierarchy

---

## 🚀 Deployment

### Frontend (Vercel)

```bash
cd frontend
npm run build
vercel deploy
```

### Backend (Railway/Render)

```bash
cd backend
# Add Procfile:
# web: uvicorn main:app --host 0.0.0.0 --port $PORT
railway up
```

### Smart Contracts

Already deployed on TestNet. For MainNet:
1. Update `ALGOD_ADDRESS` to MainNet
2. Fund MainNet account
3. Run deployment script
4. Update backend config

---

## 🔐 Security Notes

- **Never commit** private keys or mnemonics
- Use `.env` files for sensitive data
- Add `.env` to `.gitignore`
- Use environment variables in production
- Validate all user inputs
- Implement rate limiting on API
- Use HTTPS in production

---

## 📝 License

MIT License - see LICENSE file

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review Algorand developer forums

---

**Built with ❤️ using Algorand, React, and FastAPI**
