"""Backend utilities for hashing and duplicate detection."""

from .model_checker import (  # noqa: F401
    bytes16_from_hex,
    check_local_duplicate,
    compute_md5_from_bytes,
    compute_md5_from_file,
    format_record_for_display,
    record_local_model,
)

from .ipfs_cid import generate_ipfs_cid  # noqa: F401

