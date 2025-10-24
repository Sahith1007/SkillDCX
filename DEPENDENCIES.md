# SkillDCX - Dependencies Installation Guide

## 📋 Complete Dependency List

This guide covers **everything** you need to install to run SkillDCX successfully on Windows.

---

## 🖥️ System Requirements

### Operating System
- **Windows 10/11** (your current system ✓)
- **PowerShell 5.1+** (you have it ✓)

### Required Software
| Software | Minimum Version | Download Link |
|----------|----------------|---------------|
| Node.js | 18.x or higher | https://nodejs.org/ |
| Python | 3.8 or higher | https://www.python.org/downloads/ |
| Git | 2.x | https://git-scm.com/download/win |
| Pera Wallet Mobile App | Latest | iOS/Android App Store |

---

## 📦 Installation Steps

### **Step 1: Install Node.js (for Frontend)**

1. Download Node.js LTS from: https://nodejs.org/
2. Run installer (choose "Automatically install necessary tools")
3. Verify installation:
   ```powershell
   node --version
   # Should show v18.x.x or higher
   
   npm --version
   # Should show 9.x.x or higher
   ```

### **Step 2: Install Python (for Backend & Smart Contracts)**

1. Download Python from: https://www.python.org/downloads/
2. ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```powershell
   python --version
   # Should show Python 3.8.x or higher
   
   pip --version
   # Should show pip 21.x or higher
   ```

### **Step 3: Install Git (Already have it ✓)**

Your system already has Git, but if needed:
1. Download from: https://git-scm.com/download/win
2. Install with default settings
3. Verify:
   ```powershell
   git --version
   ```

### **Step 4: Install Pera Wallet Mobile App**

1. **iOS**: https://apps.apple.com/app/pera-algo-wallet/id1459898525
2. **Android**: https://play.google.com/store/apps/details?id=com.algorand.android

---

## 📚 Frontend Dependencies (Node.js/npm)

### Installation

```powershell
# Navigate to frontend directory
cd C:\Users\Sahith\OneDrive\Desktop\SkillDCX\frontend

# Install all dependencies
npm install
```

### Package List

The `package.json` already contains all required packages:

#### **Core Framework**
- `next` (^15.5.2) - Next.js framework
- `react` (^19) - React library
- `react-dom` (^19) - React DOM

#### **Blockchain/Wallet**
- `@perawallet/connect` (^1.3.4) - Pera Wallet SDK
- `algosdk` (^2.7.0) - Algorand JavaScript SDK
- `axios` (^1.6.0) - HTTP client

#### **State Management**
- `zustand` (^4.4.7) - State management

#### **UI Components (shadcn/ui + Radix)**
- `@radix-ui/react-*` (various) - Headless UI components
- `lucide-react` (^0.454.0) - Icons
- `framer-motion` (latest) - Animations

#### **Styling**
- `tailwindcss` (^4.1.9) - CSS framework
- `tailwindcss-animate` (^1.0.7) - Animations
- `tailwind-merge` (^2.5.5) - Class merging
- `class-variance-authority` (^0.7.1) - Variant utilities

#### **Forms & Validation**
- `react-hook-form` (^7.60.0) - Form handling
- `zod` (3.25.67) - Schema validation
- `@hookform/resolvers` (^3.10.0) - Form resolvers

#### **Utilities**
- `clsx` (^2.1.1) - Class names utility
- `date-fns` (4.1.0) - Date utilities
- `sonner` (^1.7.4) - Toast notifications

#### **Dev Dependencies**
- `typescript` (^5) - TypeScript
- `@types/node`, `@types/react`, `@types/react-dom` - Type definitions
- `postcss` (^8.5) - CSS processing
- `autoprefixer` (^10.4.20) - CSS vendor prefixes

### Total Size
Approximately **~500 MB** (including node_modules)

---

## 🐍 Backend Dependencies (Python/pip)

### Installation

```powershell
# Navigate to backend directory
cd C:\Users\Sahith\OneDrive\Desktop\SkillDCX\backend

# Install all dependencies
pip install -r requirements.txt
```

### Package List

From `requirements.txt`:

```
fastapi==0.110.0          # Web framework
uvicorn==0.29.0          # ASGI server
pydantic==2.6.1          # Data validation
databases==0.7.0         # Database support
sqlalchemy<1.5           # ORM
alembic==1.13.1          # Database migrations
python-dotenv==1.0.1     # Environment variables
algosdk==2.7.0           # Algorand Python SDK
requests==2.31.0         # HTTP library
```

### Total Size
Approximately **~200 MB** (including all packages)

---

## ⛓️ Smart Contract Dependencies (Python/pip)

### Installation

```powershell
# Navigate to contracts directory
cd C:\Users\Sahith\OneDrive\Desktop\SkillDCX\contracts

# Install PyTeal and Algorand SDK
pip install pyteal algosdk
```

### Package List

```
pyteal               # Smart contract language (PyTeal)
algosdk              # Algorand SDK (for deployment)
```

### Total Size
Approximately **~50 MB**

---

## 🔑 Environment Configuration

### Create Frontend Environment File

```powershell
# Copy example to actual .env file
cd frontend
copy .env.example .env.local
```

Edit `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ALGOD_SERVER=https://testnet-api.algonode.cloud
NEXT_PUBLIC_ALGOD_PORT=443
NEXT_PUBLIC_ALGOD_TOKEN=
NEXT_PUBLIC_NETWORK=TestNet
NEXT_PUBLIC_IPFS_GATEWAY=https://ipfs.io/ipfs/
```

### Backend Configuration
No `.env` file needed for local development! Backend reads from:
- `deployed_contracts.json` (created after contract deployment)

---

## 📱 External Services (Free)

### 1. **Algorand TestNet**
- **URL**: https://testnet-api.algonode.cloud
- **Cost**: FREE
- **Purpose**: Blockchain network
- **Setup**: No setup needed, public endpoint

### 2. **Algorand TestNet Faucet**
- **URL**: https://bank.testnet.algorand.network/
- **Cost**: FREE
- **Purpose**: Get test ALGO for transactions
- **Setup**: 
  1. Visit the URL
  2. Click "Create Account" or use existing
  3. Fund account with test ALGO

### 3. **IPFS Gateway**
- **URL**: https://ipfs.io/ipfs/
- **Cost**: FREE
- **Purpose**: View certificate files
- **Setup**: No setup needed, public gateway

### 4. **Pera Wallet**
- **Cost**: FREE
- **Purpose**: Algorand wallet for authentication
- **Setup**:
  1. Download mobile app (iOS/Android)
  2. Create new wallet or import existing
  3. Switch to TestNet in settings
  4. Fund with test ALGO from faucet

---

## 💾 Disk Space Requirements

| Component | Size |
|-----------|------|
| Node.js installation | ~50 MB |
| Python installation | ~100 MB |
| Frontend node_modules | ~500 MB |
| Backend pip packages | ~200 MB |
| Smart contract packages | ~50 MB |
| Source code | ~10 MB |
| **Total** | **~910 MB** |

**Recommended**: At least **2 GB** of free disk space

---

## 🧪 Verify Installation

Run this verification script:

```powershell
# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Cyan
node --version
npm --version

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Cyan
python --version
pip --version

# Check Git
Write-Host "`nChecking Git..." -ForegroundColor Cyan
git --version

# Check if frontend dependencies are installed
Write-Host "`nChecking Frontend Dependencies..." -ForegroundColor Cyan
if (Test-Path "frontend\node_modules") {
    Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend dependencies NOT installed" -ForegroundColor Red
    Write-Host "  Run: cd frontend && npm install" -ForegroundColor Yellow
}

# Check if backend dependencies are installed
Write-Host "`nChecking Backend Dependencies..." -ForegroundColor Cyan
python -c "import fastapi; print('✓ FastAPI installed')" 2>$null
if ($?) {
    Write-Host "✓ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Backend dependencies NOT installed" -ForegroundColor Red
    Write-Host "  Run: cd backend && pip install -r requirements.txt" -ForegroundColor Yellow
}

# Check if PyTeal is installed
Write-Host "`nChecking Smart Contract Dependencies..." -ForegroundColor Cyan
python -c "import pyteal; print('✓ PyTeal installed')" 2>$null
if ($?) {
    Write-Host "✓ Smart contract dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Smart contract dependencies NOT installed" -ForegroundColor Red
    Write-Host "  Run: pip install pyteal algosdk" -ForegroundColor Yellow
}

Write-Host "`n" -NoNewline
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Verification Complete" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
```

---

## 🚀 Quick Install Script

Save this as `install_dependencies.ps1` and run it:

```powershell
Write-Host "Installing SkillDCX Dependencies..." -ForegroundColor Cyan
Write-Host ""

# Install Frontend Dependencies
Write-Host "1. Installing Frontend Dependencies..." -ForegroundColor Yellow
cd frontend
npm install
if ($?) {
    Write-Host "✓ Frontend dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend installation failed" -ForegroundColor Red
    exit 1
}
cd ..

# Install Backend Dependencies
Write-Host "`n2. Installing Backend Dependencies..." -ForegroundColor Yellow
cd backend
pip install -r requirements.txt
if ($?) {
    Write-Host "✓ Backend dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Backend installation failed" -ForegroundColor Red
    exit 1
}
cd ..

# Install Smart Contract Dependencies
Write-Host "`n3. Installing Smart Contract Dependencies..." -ForegroundColor Yellow
pip install pyteal algosdk
if ($?) {
    Write-Host "✓ Smart contract dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Smart contract installation failed" -ForegroundColor Red
    exit 1
}

# Create .env file
Write-Host "`n4. Creating Environment Configuration..." -ForegroundColor Yellow
if (-Not (Test-Path "frontend\.env.local")) {
    Copy-Item "frontend\.env.example" "frontend\.env.local"
    Write-Host "✓ Created frontend\.env.local" -ForegroundColor Green
} else {
    Write-Host "! frontend\.env.local already exists" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Installation Complete! 🎉" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Get TestNet ALGO from: https://bank.testnet.algorand.network/" -ForegroundColor White
Write-Host "2. Deploy contracts: cd contracts && python deploy_contracts.py --mnemonic 'your phrase'" -ForegroundColor White
Write-Host "3. Start app: .\start.ps1" -ForegroundColor White
Write-Host ""
```

---

## 🐛 Common Issues & Solutions

### **Issue: "node is not recognized"**
**Solution:**
- Node.js not in PATH
- Reinstall Node.js with "Add to PATH" checked
- Restart PowerShell after installation

### **Issue: "python is not recognized"**
**Solution:**
- Python not in PATH
- Reinstall Python with "Add Python to PATH" checked
- Or add manually: `C:\Users\Sahith\AppData\Local\Programs\Python\Python3xx`

### **Issue: "npm install fails with EACCES"**
**Solution:**
```powershell
# Run as Administrator or clear cache
npm cache clean --force
npm install
```

### **Issue: "pip install fails with SSL error"**
**Solution:**
```powershell
# Use trusted host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### **Issue: "Module not found: Can't resolve '@perawallet/connect'"**
**Solution:**
```powershell
# Reinstall frontend dependencies
cd frontend
rm -r node_modules
rm package-lock.json
npm install
```

---

## 📊 Installation Time Estimates

| Step | Time |
|------|------|
| Node.js download & install | 5 minutes |
| Python download & install | 5 minutes |
| Frontend npm install | 3-5 minutes |
| Backend pip install | 2-3 minutes |
| Smart contract pip install | 1 minute |
| **Total** | **15-20 minutes** |

*(Times depend on internet speed)*

---

## ✅ Final Checklist

Before running the app, ensure:

- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Git installed (`git --version`)
- [ ] Frontend dependencies installed (`frontend/node_modules` exists)
- [ ] Backend dependencies installed (can `import fastapi` in Python)
- [ ] PyTeal installed (can `import pyteal` in Python)
- [ ] `.env.local` file created in frontend
- [ ] Pera Wallet mobile app installed
- [ ] TestNet account created and funded

---

## 🎯 You're Ready!

Once all dependencies are installed, run:

```powershell
.\start.ps1
```

Visit http://localhost:3000 and start building! 🚀

---

**Need Help?**
- Check `QUICK_REFERENCE.md` for commands
- Read `INTEGRATION_GUIDE.md` for detailed setup
- Visit `PROJECT_SUMMARY.md` for overview
