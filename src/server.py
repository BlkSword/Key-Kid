from mcp.server.fastmcp import FastMCP
from src.tools.models import BreakResult, DetectionCandidate
from src.tools.rot import rot_all
from src.tools.decode import detect_encoding, decode_common
from src.tools.xor import xor_single_break, xor_repeating_break
from src.tools.classic import caesar_break, vigenere_break, affine_break, rail_fence_break, transposition_break, playfair_break
from src.tools.rc4 import rc4_decrypt
from src.resources.samples import register_samples
from src.prompts.analyze import register_prompts

mcp = FastMCP("CTF Crypto")
register_samples(mcp)
register_prompts(mcp)

@mcp.tool()
def tool_rot_all(text: str, top_k: int = 3) -> list[BreakResult]:
    return rot_all(text, top_k)

@mcp.tool()
def tool_detect_encoding(text: str, top_k: int = 5) -> list[DetectionCandidate]:
    return detect_encoding(text, top_k)

@mcp.tool()
def tool_decode_common(text: str, limit: int = 10) -> list[DetectionCandidate]:
    return decode_common(text, limit)

@mcp.tool()
def tool_xor_single_break(data: str, encoding: str = "hex", top_k: int = 3) -> list[BreakResult]:
    return xor_single_break(data, encoding, top_k)

@mcp.tool()
def tool_xor_repeating_break(data: str, encoding: str = "hex", min_key: int = 2, max_key: int = 40) -> BreakResult:
    return xor_repeating_break(data, encoding, min_key, max_key)

@mcp.tool()
def tool_caesar_break(ciphertext: str) -> BreakResult:
    return caesar_break(ciphertext)

@mcp.tool()
def tool_vigenere_break(ciphertext: str, max_key_len: int = 16, top_k: int = 3) -> list[BreakResult]:
    return vigenere_break(ciphertext, max_key_len, top_k)

@mcp.tool()
def tool_affine_break(ciphertext: str, top_k: int = 3) -> list[BreakResult]:
    return affine_break(ciphertext, top_k)

@mcp.tool()
def tool_rail_fence_break(ciphertext: str, max_rails: int = 10, top_k: int = 3) -> list[BreakResult]:
    return rail_fence_break(ciphertext, max_rails, top_k)

@mcp.tool()
def tool_transposition_break(ciphertext: str, max_key_len: int = 5, top_k: int = 3) -> list[BreakResult]:
    return transposition_break(ciphertext, max_key_len, top_k)

@mcp.tool()
def tool_playfair_break(ciphertext: str, key_hint: str | None = None, top_k: int = 1) -> list[BreakResult]:
    return playfair_break(ciphertext, key_hint, top_k)

@mcp.tool()
async def tool_rc4_decrypt(ciphertext: str, cipher_encoding: str = "hex", key: str | None = None, key_encoding: str = "raw", ctx=None) -> str:
    return await rc4_decrypt(ciphertext, cipher_encoding, key, key_encoding, ctx)

def main():
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()