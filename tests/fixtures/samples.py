"""Test sample data for Key-Kid tests."""

# MCP 工具测试样本数据
SAMPLE_CIPHERTEXTS = {
    "caesar": "Uryyb Jbeyq",
    "vigenere": "Lxfopvefrnhr",
    "xor_single_hex": "3f292c2c2b",
    "base64": "SGVsbG8gd29ybGQ=",
    "hex": "48656c6c6f",
    "rail_fence": "WECRLTEERDSOEEFEAOCAIVDEN",
    "affine": "ZEBBW",
}

EXPECTED_PLAINTEXTS = {
    "caesar": "Hello World",
    "vigenere": "testingvigenere",
    "xor_single_hex": "Hello world",
    "base64": "Hello world",
    "hex": "Hello",
    "rail_fence": "WEAREDISCOVEREDFLEEATONCE",
    "affine": "ATTACK",
}

# MCP 工具参数示例
MCP_TOOL_CALLS = {
    "tool_rot_all": {"text": "Uryyb Jbeyq", "top_k": 3},
    "tool_caesar_break": {"ciphertext": "Uryyb Jbeyq"},
    "tool_xor_single_break": {"data": "3f292c2c2b", "encoding": "hex", "top_k": 3},
    "tool_vigenere_break": {"ciphertext": "Lxfopvefrnhr", "max_key_len": 8, "top_k": 1},
    "tool_affine_break": {"ciphertext": "ZEBBW", "top_k": 1},
    "tool_rail_fence_break": {
        "ciphertext": "WECRLTEERDSOEEFEAOCAIVDEN",
        "max_rails": 5,
        "top_k": 1,
    },
    "tool_detect_encoding": {"text": "SGVsbG8gd29ybGQ=", "top_k": 5},
    "tool_decode_common": {"text": "48656c6c6f", "limit": 10},
}

# 编码测试样本
ENCODING_SAMPLES = {
    "base64_valid": "SGVsbG8gd29ybGQ=",
    "base64_expected": "Hello world",
    "hex_valid": "48656c6c6f",
    "hex_expected": "Hello",
    "url_valid": "Hello%20World%21",
    "url_expected": "Hello World!",
    "unicode_escape_valid": "Hello\\u0020World",
    "unicode_escape_expected": "Hello World",
}

# XOR 测试样本
XOR_SAMPLES = {
    "single_byte_hex": "3f292c2c2b",
    "single_byte_key": "5",
    "single_byte_plaintext": "Hello world",
    "repeating_hex": "5468697320697320612074657374",
    "repeating_key": "6B6579",  # "Key" in hex
}

# 哈希识别样本
HASH_SAMPLES = {
    "md5": "5d41402abc4b2a76b9719d911017c592",
    "sha1": "356a192b7913b04c54574d18c28d46e6395428ab",
    "sha256": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
    "sha512": (
        "9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca7"
        "231c85373578ef9087f6679279735365675675675"
    ),
}

# 质数分解样本
FACTOR_SAMPLES = {
    "small": {"n": 10403, "factors": ["101", "103"]},
    "medium": {"n": 6, "factors": ["2", "3"]},
    "large_prime": {"n": 104729, "factors": ["104729"]},
}
