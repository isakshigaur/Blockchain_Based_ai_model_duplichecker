"""
Generate IPFS-compatible Content Identifiers (CIDv0) locally.

CIDv0 format:
  Base58( multihash( 0x12 || 0x20 || sha256_digest ) )

This produces the familiar "Qm..." CID string without requiring
an IPFS daemon — the CID is deterministic and content-addressed.
"""

import hashlib

# Base58 alphabet used by Bitcoin / IPFS
_B58_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _base58_encode(data: bytes) -> str:
    """Pure-Python Base58 encoder (Bitcoin alphabet)."""
    num = int.from_bytes(data, "big")
    encoded = bytearray()
    while num > 0:
        num, rem = divmod(num, 58)
        encoded.append(_B58_ALPHABET[rem])
    # Preserve leading zero-bytes
    for byte in data:
        if byte == 0:
            encoded.append(_B58_ALPHABET[0])
        else:
            break
    return bytes(reversed(encoded)).decode("ascii")


def generate_ipfs_cid(payload: bytes) -> str:
    """
    Compute a CIDv0 for the given raw bytes.

    Steps:
      1. SHA-256 hash the content.
      2. Build the multihash:  0x12 (sha2-256 fn code) | 0x20 (digest length) | digest
      3. Base58-encode the multihash.

    The resulting string starts with "Qm" — identical to what `ipfs add` produces.
    """
    sha256_digest = hashlib.sha256(payload).digest()
    # multihash:  hash-function-code  ||  digest-size  ||  digest
    multihash = bytes([0x12, 0x20]) + sha256_digest
    return _base58_encode(multihash)
