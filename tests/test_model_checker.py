import pytest

from backend import model_checker


def test_compute_md5_from_bytes():
    payload = b"hello world"
    assert model_checker.compute_md5_from_bytes(payload) == "5eb63bbbe01eeed093cb22bb8f5acdc3"


def test_bytes16_from_hex_validates_length():
    with pytest.raises(ValueError):
        model_checker.bytes16_from_hex("1234")


def test_local_index_roundtrip(tmp_path):
    path = tmp_path / "index.json"
    hash_hex = "5eb63bbbe01eeed093cb22bb8f5acdc3"
    model_checker.record_local_model(hash_hex, {"name": "demo"}, path)
    assert model_checker.check_local_duplicate(hash_hex, path) is True

