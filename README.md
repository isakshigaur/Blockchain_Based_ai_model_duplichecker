## Blockchain-Based AI Model Ownership & Copyright Protection

Upload AI model files to verify uniqueness via cryptographic fingerprinting (MD5 + IPFS CID), check for duplicates against an on-chain smart contract registry, and register immutable proof of ownership on the Ethereum blockchain.

### Features
- Upload AI model files (30+ formats supported: .pt, .onnx, .pkl, .h5, .safetensors, .bin, etc.)
- Automatic MD5 fingerprint and IPFS CID (CIDv0) generation
- On-chain duplicate detection via Solidity smart contract
- One-click blockchain registration with transaction receipt
- Dark, industry-grade UI built with Streamlit
- Retry logic for reliable blockchain interactions

### Tech Stack
- **Frontend:** Streamlit (Python) with custom dark-theme CSS
- **Smart Contract:** Solidity 0.8.21 (`paris` EVM target)
- **Blockchain:** Ethereum (Sepolia Testnet for live / Ganache for local)
- **RPC Provider:** Alchemy (free tier)
- **Hashing:** MD5 (hashlib) + SHA-256 based IPFS CIDv0
- **Hosting:** Streamlit Community Cloud (free)

---

## Quick Start (Local Development)

```bash
# One-command launch
./start.sh
```

Or manually:

```bash
# Terminal 1 — Start blockchain
npx ganache-cli --chainId 1337 --port 8545 --deterministic

# Terminal 2 — Deploy & launch
python scripts/deploy.py
streamlit run streamlit_app.py
```

---

## Deploy Live on the Internet (FREE)

Follow these 5 steps to make the portal accessible to everyone:

### Step 1: Create a MetaMask Wallet

1. Install [MetaMask](https://metamask.io/) browser extension
2. Create a new wallet (save your recovery phrase securely)
3. Switch network to **Sepolia Testnet**:
   - Click the network dropdown in MetaMask
   - Enable "Show test networks" in Settings > Advanced
   - Select "Sepolia"
4. **Export your private key**:
   - Click the three dots on your account → Account Details → Export Private Key
   - Copy the key (keep it secret!)

### Step 2: Get a Free Alchemy RPC URL

1. Go to [alchemy.com](https://www.alchemy.com/) and sign up (free, no credit card)
2. Click **"Create New App"**
3. Set:
   - Name: `AI Model Registry`
   - Chain: `Ethereum`
   - Network: `Sepolia`
4. Click **Create App**
5. On the app dashboard, click **"API Key"** and copy the full HTTPS URL:
   ```
   https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY_HERE
   ```

### Step 3: Get Free Sepolia Test ETH

1. Go to: [Google Cloud Sepolia Faucet](https://cloud.google.com/application/web3/faucet/ethereum/sepolia)
2. Paste your MetaMask wallet address
3. Request free Sepolia ETH (you'll get ~0.05 ETH — enough for 50+ contract operations)
4. Wait 1-2 minutes for it to arrive

### Step 4: Deploy the Smart Contract to Sepolia

Update your `.env` file with Sepolia settings:

```env
RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY_HERE
CHAIN_ID=11155111
DEPLOYER_PRIVATE_KEY=YOUR_METAMASK_PRIVATE_KEY
CONTRACT_ADDRESS=
```

Then deploy:

```bash
python scripts/deploy.py
```

You'll see output like:
```
Deployer account: 0xYourAddress...
Account balance: 0.05 ETH
Chain ID: 11155111
Contract deployed to: 0xAbCdEf...
```

**Copy the contract address** — you'll need it for the next step.

Now update `.env` with the deployed contract address:
```env
CONTRACT_ADDRESS=0xAbCdEf_YOUR_DEPLOYED_ADDRESS
```

### Step 5: Deploy to Streamlit Community Cloud (FREE)

1. **Push your project to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "AI Model Ownership Portal"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Go to** [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub

3. Click **"New app"** → Select your repository

4. Set **Main file path** to: `streamlit_app.py`

5. **Before clicking Deploy**, click **"Advanced settings"** and add these secrets:
   ```toml
   RPC_URL = "https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY"
   CHAIN_ID = "11155111"
   DEPLOYER_PRIVATE_KEY = "YOUR_METAMASK_PRIVATE_KEY"
   CONTRACT_ADDRESS = "0xYOUR_DEPLOYED_CONTRACT_ADDRESS"
   ```

6. Click **Deploy!**

Your portal will be live at:
```
https://YOUR_APP_NAME.streamlit.app
```

---

### Project Layout
```
contracts/ModelRegistry.sol     Solidity smart contract
backend/model_checker.py        Hashing & duplicate detection
backend/ipfs_cid.py             IPFS CID generation (pure Python)
scripts/deploy.py               Contract compilation & deployment
streamlit_app.py                Main portal UI
start.sh                        One-command local launcher
tests/                          Unit tests
artifacts/                      Compiled ABI & deployment info
data/                           Local model index
.streamlit/                     Streamlit config & theme
```

### Testing
```bash
pytest
```

### Developer
**Sakshi Gaur**
# Blockchain_Based_ai_model_duplichecker
