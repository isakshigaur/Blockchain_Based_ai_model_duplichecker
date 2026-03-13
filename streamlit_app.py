import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from web3 import Web3

from backend.model_checker import (
    bytes16_from_hex,
    compute_md5_from_bytes,
)
from backend.ipfs_cid import generate_ipfs_cid

@st.cache_data
def _compute_md5(payload: bytes) -> str:
    return compute_md5_from_bytes(payload)


@st.cache_data
def _generate_cid(payload: bytes) -> str:
    return generate_ipfs_cid(payload)

load_dotenv()

ARTIFACT_PATH = Path("artifacts/ModelRegistry.json")
DEPLOYMENT_PATH = Path("artifacts/deployment.json")


def _env(key: str, default: str = "") -> str:
    """Read config from Streamlit Cloud secrets first, then fall back to .env."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, default)

# ─── Accepted AI / ML Model File Extensions ──────────────────────────────────
MODEL_EXTENSIONS = [
    "pt", "pth", "bin", "onnx", "pkl", "pickle",
    "h5", "hdf5", "pb", "tflite", "keras",
    "safetensors", "ckpt", "mar", "joblib",
    "mlmodel", "pmml", "model", "weights",
    "caffemodel", "params", "cfg", "meta",
    "json", "tar", "gz", "zip",
]

# ─── Dark Industry-Grade CSS ─────────────────────────────────────────────────
PAGE_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

  /* ── Global ─────────────────────────────────────────── */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #e0e0e0;
  }

  .stApp {
    background: #0a0a0f;
  }

  .block-container {
    max-width: 840px;
    padding-top: 1.5rem;
  }

  #MainMenu, footer, header { visibility: hidden; }

  /* ── Hero Banner ────────────────────────────────────── */
  .hero {
    background: linear-gradient(160deg, #0d0d14 0%, #111128 40%, #0d0d14 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 2.2rem 2.5rem 1.8rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(99,102,241,0.5) 50%, transparent 100%);
  }
  .hero h1 {
    color: #ffffff;
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0 0 0.4rem 0;
    line-height: 1.35;
  }
  .hero p {
    color: rgba(255,255,255,0.5);
    font-size: 0.88rem;
    font-weight: 400;
    margin: 0;
    line-height: 1.65;
    max-width: 600px;
  }
  .hero-status {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    margin-top: 1rem;
    padding: 5px 14px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
  }
  .hero-status.online {
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.2);
    color: #22c55e;
  }
  .hero-status.offline {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.2);
    color: #ef4444;
  }
  .status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    display: inline-block;
  }
  .status-dot.on { background: #22c55e; box-shadow: 0 0 6px #22c55e; }
  .status-dot.off { background: #ef4444; box-shadow: 0 0 6px #ef4444; }

  /* ── Section Card ───────────────────────────────────── */
  .section-card {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin: 1rem 0;
  }
  .section-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #6366f1;
    margin: 0 0 1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }

  /* ── Hash / CID Display ─────────────────────────────── */
  .hash-box {
    background: #0a0a12;
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    margin: 0.5rem 0;
    border: 1px solid rgba(255,255,255,0.04);
  }
  .hash-label {
    color: rgba(255,255,255,0.3);
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    margin-bottom: 5px;
  }
  .hash-value {
    color: #22c55e;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    word-break: break-all;
  }
  .cid-value {
    color: #818cf8;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.3px;
    word-break: break-all;
  }

  /* ── Status Badges ──────────────────────────────────── */
  .status-row {
    display: flex;
    gap: 10px;
    margin: 1rem 0;
  }
  .status-badge {
    flex: 1;
    border-radius: 10px;
    padding: 1rem 1rem;
    text-align: center;
  }
  .status-ok {
    background: rgba(34,197,94,0.06);
    border: 1px solid rgba(34,197,94,0.15);
  }
  .status-ok .status-icon { font-size: 1.1rem; color: #22c55e; font-weight: 700; }
  .status-ok .status-text { color: #4ade80; font-size: 0.75rem; font-weight: 600; margin-top: 6px; }

  .status-err {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.15);
  }
  .status-err .status-icon { font-size: 1.1rem; color: #ef4444; font-weight: 700; }
  .status-err .status-text { color: #f87171; font-size: 0.75rem; font-weight: 600; margin-top: 6px; }

  /* ── File info row ──────────────────────────────────── */
  .file-info {
    display: flex;
    align-items: center;
    gap: 14px;
    background: #111118;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 0.85rem 1.3rem;
    margin: 0.8rem 0;
  }
  .file-icon-box {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    color: #fff;
    font-weight: 800;
    font-size: 0.65rem;
    letter-spacing: 0.5px;
  }
  .file-meta { flex: 1; }
  .file-name { font-weight: 600; font-size: 0.88rem; color: #e0e0e0; }
  .file-size { font-size: 0.75rem; color: #555; margin-top: 3px; }

  /* ── Record card ────────────────────────────────────── */
  .record-card {
    background: #0d0d14;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin: 0.6rem 0;
  }
  .record-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
  }
  .record-row:last-child { border-bottom: none; }
  .record-label {
    color: rgba(255,255,255,0.35);
    font-size: 0.73rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }
  .record-val {
    color: #c4c4cc;
    font-size: 0.82rem;
    font-weight: 500;
    text-align: right;
    max-width: 62%;
    word-break: break-all;
    font-family: 'JetBrains Mono', monospace;
  }

  /* IPFS CID inline card */
  .cid-inline {
    background: #0d0d14;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    margin: 0.5rem 0 0.8rem 0;
  }
  .cid-inline-label {
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: rgba(255,255,255,0.3);
    margin-bottom: 3px;
  }
  .cid-inline-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #818cf8;
    word-break: break-all;
  }

  /* ── Primary button ─────────────────────────────────── */
  .stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.72rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.3px;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.25) !important;
  }
  .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.35) !important;
  }

  /* ── Upload area ────────────────────────────────────── */
  div[data-testid="stFileUploader"] {
    border: 1.5px dashed rgba(99,102,241,0.25) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    background: rgba(99,102,241,0.02) !important;
    transition: border-color 0.3s ease;
  }
  div[data-testid="stFileUploader"]:hover {
    border-color: rgba(99,102,241,0.5) !important;
  }
  div[data-testid="stFileUploader"] label {
    color: #888 !important;
  }

  /* ── Text inputs ────────────────────────────────────── */
  .stTextInput > div > div > input {
    background: #0d0d14 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #e0e0e0 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1rem !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
  }
  .stTextInput label {
    color: rgba(255,255,255,0.45) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
  }

  /* ── Streamlit overrides for dark ───────────────────── */
  .stAlert { border-radius: 10px !important; }
  .stSpinner > div { color: #6366f1 !important; }

  /* ── Empty state ────────────────────────────────────── */
  .empty-state {
    text-align: center;
    padding: 2.5rem 1rem;
    background: #111118;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    margin: 1rem 0;
  }
  .empty-state-icon {
    width: 56px; height: 56px;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.8rem;
  }
  .empty-state-icon svg { width: 24px; height: 24px; }
  .empty-state h3 {
    color: #888;
    font-size: 0.92rem;
    font-weight: 600;
    margin: 0 0 0.3rem 0;
  }
  .empty-state p {
    color: #555;
    font-size: 0.78rem;
    margin: 0;
    line-height: 1.5;
  }

  /* ── Footer ─────────────────────────────────────────── */
  .app-footer {
    text-align: center;
    padding: 2rem 0 1rem 0;
    border-top: 1px solid rgba(255,255,255,0.04);
    margin-top: 2.5rem;
  }
  .app-footer .footer-line {
    color: #444;
    font-size: 0.72rem;
    letter-spacing: 0.3px;
  }
  .app-footer .developer {
    color: #555;
    font-size: 0.7rem;
    margin-top: 0.4rem;
    letter-spacing: 0.2px;
  }
  .app-footer .developer span {
    color: #818cf8;
    font-weight: 600;
  }
</style>
"""


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_web3() -> Web3:
    rpc = _env("RPC_URL", "http://127.0.0.1:8545")
    # Google Cloud RPC sometimes requires specific headers or timeouts
    headers = {'User-Agent': 'Mozilla/5.0 (StreamlitCloud)'}
    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={'timeout': 20, 'headers': headers}))
    return w3


@st.cache_resource
def _load_artifact() -> Optional[dict]:
    if not ARTIFACT_PATH.exists():
        return None
    return json.loads(ARTIFACT_PATH.read_text())


def _read_deployment_address() -> Optional[str]:
    if not DEPLOYMENT_PATH.exists():
        return None
    return json.loads(DEPLOYMENT_PATH.read_text()).get("contractAddress")


@st.cache_resource
def _load_contract(_w3: Web3):
    address = _env("CONTRACT_ADDRESS") or _read_deployment_address()
    if not address:
        return None
    artifact = _load_artifact()
    if not artifact:
        return None
    try:
        checksum = Web3.to_checksum_address(address.strip())
        return w3.eth.contract(address=checksum, abi=artifact["abi"])
    except Exception:
        return None


def _get_account(w3: Web3):
    pk = _env("DEPLOYER_PRIVATE_KEY")
    if not pk:
        return None
    try:
        return w3.eth.account.from_key(pk)
    except Exception:
        return None


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def _file_ext_label(name: str) -> str:
    ext = Path(name).suffix.upper().lstrip(".")
    return ext if ext else "FILE"


def _retry_call(fn, max_retries: int = 3, delay: float = 1.0):
    """Retry a blockchain call to work around ganache-cli checkpoint bugs."""
    last_err = None
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as exc:
            last_err = exc
            if attempt < max_retries - 1:
                time.sleep(delay)
    raise last_err


# ─── App ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="AI Model Ownership Portal",
        page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg'><text y='14' font-size='14'>S</text></svg>",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown(PAGE_CSS, unsafe_allow_html=True)

    # ── Connect to blockchain silently ────────────────────────────────────────
    w3 = _get_web3()
    connected = w3.is_connected()
    contract = _load_contract(w3) if connected else None
    account = _get_account(w3) if connected else None

    is_online = connected and contract

    # ── Hero ──────────────────────────────────────────────────────────────────
    status_cls = "online" if is_online else "offline"
    dot_cls = "on" if is_online else "off"
    status_label = "Blockchain Connected" if is_online else "Blockchain Offline"

    st.markdown(
        f"""
        <div class="hero">
            <h1>AI Model Ownership &amp; Copyright Protection</h1>
            <p>
                Upload your AI / ML model file to generate a unique cryptographic
                fingerprint and IPFS CID. Verify originality against the on-chain
                registry and register immutable proof of ownership.
            </p>
            <div class="hero-status {status_cls}">
                <span class="status-dot {dot_cls}"></span>
                {status_label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not is_online:
        rpc_attempted = _env("RPC_URL", "http://127.0.0.1:8545")
        # Mask the key for security
        masked_rpc = rpc_attempted.split('?')[0] if '?' in rpc_attempted else rpc_attempted
        
        st.error(
            f"**Blockchain connection failed.**"
        )
        st.info(
            f"**Attempted RPC:** `{masked_rpc}`\n\n"
            "**Common Fixes:**\n"
            "1. If live: Ensure keys are in **Streamlit Cloud > Settings > Secrets**.\n"
            "2. If local: Ensure **Ganache** is running.\n"
            "3. Check if your Google Cloud RPC key has expired or is restricted."
        )
        _render_footer()
        st.stop()

    # ── Upload Section ────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-card">'
        '<div class="section-title">Upload Model File</div>',
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Drag and drop or click to browse",
        type=MODEL_EXTENSIONS,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if not uploaded:
        upload_icon_svg = (
            '<svg viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="1.5" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
            '<polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>'
        )
        st.markdown(
            f"""
            <div class="empty-state">
                <div class="empty-state-icon">{upload_icon_svg}</div>
                <h3>No file uploaded</h3>
                <p>
                    Accepted formats: .pt, .onnx, .pkl, .h5, .safetensors,
                    .keras, .bin, .tflite, .joblib, .ckpt and more
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _render_footer()
        return

    # ── File Info ─────────────────────────────────────────────────────────────
    payload = uploaded.read()
    ext_label = _file_ext_label(uploaded.name)

    st.markdown(
        f"""
        <div class="file-info">
            <div class="file-icon-box">{ext_label}</div>
            <div class="file-meta">
                <div class="file-name">{uploaded.name}</div>
                <div class="file-size">{_format_size(uploaded.size)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Compute Hashes ────────────────────────────────────────────────────────
    md5_hash = _compute_md5(payload)
    ipfs_cid = _generate_cid(payload)

    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">Cryptographic Fingerprints</div>
            <div class="hash-box">
                <div class="hash-label">MD5 Hash</div>
                <div class="hash-value">{md5_hash}</div>
            </div>
            <div class="hash-box" style="margin-top:8px;">
                <div class="hash-label">IPFS Content Identifier (CIDv0)</div>
                <div class="cid-value">{ipfs_cid}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Duplicate Checks ──────────────────────────────────────────────────────
    try:
        hash_bytes = bytes16_from_hex(md5_hash)
        onchain_exists = _retry_call(
            lambda: contract.functions.isRegistered(hash_bytes).call()
        )
    except Exception as exc:
        st.error(f"On-chain verification failed: {exc}")
        _render_footer()
        return

    chain_cls = "status-err" if onchain_exists else "status-ok"
    chain_icon = "REGISTERED" if onchain_exists else "CLEAR"
    chain_label = "Already Registered" if onchain_exists else "Blockchain Verification — Clear"

    st.markdown(
        f"""
        <div class="status-row">
            <div class="status-badge {chain_cls}" style="flex: 1;">
                <div class="status-icon">{chain_icon}</div>
                <div class="status-text">{chain_label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── If already registered, show existing record ───────────────────────────
    if onchain_exists:
        st.markdown(
            '<div class="section-card"><div class="section-title">Existing Registration</div>',
            unsafe_allow_html=True,
        )
        try:
            record = _retry_call(
                lambda: contract.functions.getRecord(hash_bytes).call()
            )
            ts = (
                datetime.fromtimestamp(record[3], tz=__import__('datetime').timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                if record[3] else "—"
            )
            rows = [
                ("Owner", record[0]),
                ("Model Name", record[1]),
                ("IPFS CID", record[2] or "—"),
                ("Registered At", ts),
            ]
            cards_html = ""
            for label, val in rows:
                cards_html += (
                    f'<div class="record-row">'
                    f'<span class="record-label">{label}</span>'
                    f'<span class="record-val">{val}</span>'
                    f'</div>'
                )
            st.markdown(
                f'<div class="record-card">{cards_html}</div></div>',
                unsafe_allow_html=True,
            )
        except Exception as exc:
            st.error(f"Could not fetch record: {exc}")
        _render_footer()
        return

    # ── Registration Form ─────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-card">'
        '<div class="section-title">Register This Model</div>',
        unsafe_allow_html=True,
    )

    model_name = st.text_input("Model Name", value=uploaded.name)

    st.markdown(
        f"""
        <div class="cid-inline">
            <div class="cid-inline-label">Auto-Generated IPFS CID</div>
            <div class="cid-inline-val">{ipfs_cid}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Register on Blockchain", use_container_width=True):
        if not account:
            st.error("Signer key not configured. Set DEPLOYER_PRIVATE_KEY in .env file.")
            _render_footer()
            return

        with st.spinner("Submitting transaction..."):
            try:
                nonce = w3.eth.get_transaction_count(account.address)
                txn = contract.functions.registerModel(
                    hash_bytes, model_name, ipfs_cid
                ).build_transaction(
                    {
                        "from": account.address,
                        "nonce": nonce,
                        "gasPrice": w3.eth.gas_price,
                    }
                )
                signed = account.sign_transaction(txn)
                raw_tx = (
                    getattr(signed, "rawTransaction", None)
                    or getattr(signed, "raw_transaction")
                )
                tx_hash = w3.eth.send_raw_transaction(raw_tx)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

                st.success("Model registered successfully on the blockchain.")

                receipt_data = json.loads(Web3.to_json(receipt))
                status_text = (
                    "Success" if receipt_data.get("status") == 1 else "Failed"
                )
                st.markdown(
                    f"""
                    <div class="section-card">
                        <div class="section-title">Transaction Receipt</div>
                        <div class="record-card">
                            <div class="record-row">
                                <span class="record-label">Tx Hash</span>
                                <span class="record-val">{receipt_data.get('transactionHash','')}</span>
                            </div>
                            <div class="record-row">
                                <span class="record-label">Block</span>
                                <span class="record-val">{receipt_data.get('blockNumber','')}</span>
                            </div>
                            <div class="record-row">
                                <span class="record-label">Gas Used</span>
                                <span class="record-val">{receipt_data.get('gasUsed','')}</span>
                            </div>
                            <div class="record-row">
                                <span class="record-label">Status</span>
                                <span class="record-val">{status_text}</span>
                            </div>
                            <div class="record-row">
                                <span class="record-label">IPFS CID</span>
                                <span class="record-val">{ipfs_cid}</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            except Exception as exc:
                st.error(f"Transaction failed: {exc}")

    _render_footer()


def _render_footer():
    year = datetime.now().year
    st.markdown(
        f"""
        <div class="app-footer">
            <div class="footer-line">
                AI Model Ownership Portal &middot; Blockchain-Powered &middot; {year}
            </div>
            <div class="developer">
                Developed by <span>Sakshi Gaur</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
if __name__ == "__main__":
    main()
