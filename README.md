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

### Developer
**Sakshi Gaur**
# Blockchain_Based_ai_model_duplichecker

https://blockchainbasedaimodelduplichecker.streamlit.app/

## Check Transaction on block 
https://sepolia.etherscan.io/
