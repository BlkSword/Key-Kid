"""Pytest configuration and fixtures for Key-Kid tests."""
import pytest
from pathlib import Path


@pytest.fixture
def sample_ciphertexts():
    """Provide standard test sample ciphertexts."""
    return {
        "caesar": "Uryyb Jbeyq",
        "vigenere": "Lxfopvefrnhr",
        "xor_single_hex": "3f292c2c2b",
        "base64": "SGVsbG8gd29ybGQ=",
        "hex": "48656c6c6f",
        "rail_fence": "WECRLTEERDSOEEFEAOCAIVDEN",
        "affine": "ZEBBW",
    }


@pytest.fixture
def expected_plaintexts():
    """Provide expected plaintext results."""
    return {
        "caesar": "Hello World",
        "vigenere": "testingvigenere",
        "xor_single_hex": "Hello world",
        "base64": "Hello world",
        "hex": "Hello",
        "rail_fence": "WEAREDISCOVEREDFLEEATONCE",
        "affine": "ATTACK",
    }


@pytest.fixture
def mcp_server():
    """Provide MCP server instance for integration tests."""
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from src.server import mcp
    return mcp


@pytest.fixture
def temp_output_dir(tmp_path: Path):
    """Provide temporary directory for test outputs."""
    return tmp_path / "output"
