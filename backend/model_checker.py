import hashlib
import json
from pathlib import Path
from typing import Dict, Optional

DEFAULT_INDEX_PATH = Path("data/model_index.json")

def compute_md5_from_bytes(payload: bytes) -> str:
    """Return the hex MD5 digest for the provided payload."""
    digest = hashlib.md5()
    digest.update(payload)
    return digest.hexdigest()

def compute_md5_from_file(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Stream the file so large models don't overflow memory."""
    digest = hashlib.md5()
    with file_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()

def load_local_index(path: Path = DEFAULT_INDEX_PATH) -> Dict[str, Dict]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def persist_local_index(index: Dict[str, Dict], path: Path = DEFAULT_INDEX_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2)

def check_local_duplicate(hash_hex: str, path: Path = DEFAULT_INDEX_PATH) -> bool:
    index = load_local_index(path)
    return hash_hex in index

def record_local_model(
    hash_hex: str,
    metadata: Dict,
    path: Path = DEFAULT_INDEX_PATH,
) -> None:
    index = load_local_index(path)
    index[hash_hex] = metadata
    persist_local_index(index, path)

def bytes16_from_hex(hash_hex: str) -> bytes:
    """Convert a 32-char MD5 hex string to the 16-byte representation expected by Solidity."""
    hash_hex = hash_hex.lower()
    if len(hash_hex) != 32:
        raise ValueError("MD5 hex must be 32 characters long")
    return bytes.fromhex(hash_hex)

def format_record_for_display(record: Optional[Dict]) -> str:
    if not record:
        return "No on-chain record found."
    owner = record.get("owner")
    name = record.get("name")
    ipfs = record.get("ipfsCid")
    ts = record.get("registeredAt")
    return (
        f"Owner: {owner}\n"
        f"Name: {name}\n"
        f"IPFS CID: {ipfs or '—'}\n"
        f"Registered At: {ts}"
    )