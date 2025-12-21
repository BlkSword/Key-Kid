import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import anyio as _anyio

class _GenericFunc:
    def __init__(self, fn):
        self.fn = fn
    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)
    def __getitem__(self, item):
        return self.fn

if not hasattr(_anyio.create_memory_object_stream, "__getitem__"):
    _anyio.create_memory_object_stream = _GenericFunc(_anyio.create_memory_object_stream)
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from src.tools.models import BreakResult, DetectionCandidate
from src.tools.rot import rot_all
from src.tools.decode import detect_encoding, decode_common
from src.tools.xor import xor_single_break, xor_repeating_break
from src.tools.classic import caesar_break, vigenere_break, affine_break, rail_fence_break, transposition_break, playfair_break
from src.tools.rc4 import rc4_decrypt
from src.tools.number import factor_integer
from src.resources.samples import register_samples
from src.prompts.analyze import register_prompts
from src.resources.wordlist import register_wordlist
from src.tools.hash import hash_identify
from src.tools.block import aes_decrypt, des_decrypt
from src.tools.score import wordlist_score
from src.utils.scoring import english_score

mcp = FastMCP("CTF Crypto")
register_samples(mcp)
register_prompts(mcp)
register_wordlist(mcp)

@mcp.tool()
def tool_rot_all(text: str, top_k: int = 3) -> list[BreakResult]:
    """Enumerate ROT(1..25) shifts and return top plaintext candidates ranked by English score.

    Purpose: Quickly test simple shift ciphers (ROT/Caesar) and list plausible plaintexts.
    Usage: Provide `text`; optional `top_k` controls number of results (default 3).
    Returns: List of `BreakResult` with `algorithm`, `plaintext`, `key` (shift), and `confidence`.
    Related: Use `tool_caesar_break` for the single best candidate; `tool_rot_all_wordlist` adds wordlist weighting.
    """
    return rot_all(text, top_k)

@mcp.tool()
def tool_detect_encoding(text: str, top_k: int = 5) -> list[DetectionCandidate]:
    """Identify common encodings and attempt to decode, returning encoding guesses and decoded text.

    Purpose: Detect Base64/Hex/URL/Unicode Escape and other common formats and yield decoded outputs.
    Usage: Provide `text`; optional `top_k` limits candidates (default 5).
    Returns: List of `DetectionCandidate` with `name`, `decoded`, and `confidence`.
    Related: Use `tool_decode_common` for batch decoding; feed decoded text into cracking tools.
    """
    return detect_encoding(text, top_k)

@mcp.tool()
def tool_decode_common(text: str, limit: int = 10) -> list[DetectionCandidate]:
    """Batch-try common decoders on the input and quickly produce multiple candidate decodings.

    Purpose: When the encoding is unknown, try several decoders to obtain readable text.
    Usage: Provide `text`; optional `limit` caps number of results (default 10).
    Returns: List of `DetectionCandidate`; similar to `tool_detect_encoding` but for bulk probing.
    Related: Narrow candidates via `tool_detect_encoding`, then run cracking tools on promising decodings.
    """
    return decode_common(text, limit)

@mcp.tool()
def tool_xor_single_break(data: str, encoding: str = "hex", top_k: int = 3) -> list[BreakResult]:
    """Brute-force single-byte XOR ciphertext and return likely plaintexts and the key byte.

    Purpose: Crack common single-byte XOR used in CTF tasks.
    Usage: `data` is the ciphertext; `encoding` is `hex`/`b64`/`raw` (default `hex`); `top_k` controls result count.
    Returns: List of `BreakResult` with inferred key (one byte), plaintext, and score.
    Related: For multi-byte repeating keys, use `tool_xor_repeating_break`; if encoding is unknown, try `tool_detect_encoding` first.
    """
    return xor_single_break(data, encoding, top_k)

@mcp.tool()
def tool_xor_repeating_break(data: str, encoding: str = "hex", min_key: int = 2, max_key: int = 40) -> BreakResult:
    """Break repeating-key XOR (Vernam variant): estimate key length and recover key and plaintext.

    Purpose: Automate cracking of multi-byte repeating XOR ciphertexts.
    Usage: `data` is ciphertext; `encoding` is the ciphertext encoding; `min_key`/`max_key` bound key-length search.
    Returns: A single `BreakResult` containing the recovered key and plaintext.
    Related: Very short or non-English texts may score poorly; consider wordlists or manual validation.
    """
    return xor_repeating_break(data, encoding, min_key, max_key)

@mcp.tool()
def tool_caesar_break(ciphertext: str) -> BreakResult:
    """Brute-force Caesar cipher and return the highest-scoring plaintext and shift.

    Purpose: Automated cracking of classic shift cipher.
    Usage: Provide `ciphertext`; internally tries all 26 shifts and picks the best.
    Returns: A `BreakResult` with `key` (best shift), `plaintext`, and `confidence`.
    Related: Use `tool_rot_all` to view all candidates; `tool_rot_all_wordlist` adds wordlist weighting.
    """
    return caesar_break(ciphertext)

@mcp.tool()
def tool_vigenere_break(ciphertext: str, max_key_len: int = 16, top_k: int = 3) -> list[BreakResult]:
    """Break Vigenère: estimate key length, recover key and plaintext, and return multiple candidates.

    Purpose: Automate common Vigenère cracking workflows.
    Usage: `ciphertext`; `max_key_len` caps maximum key length (default 16); `top_k` controls number of results.
    Returns: List of `BreakResult` with inferred key, plaintext, and score.
    Related: Very short or non-English text may score low; use wordlists or context to filter.
    """
    return vigenere_break(ciphertext, max_key_len, top_k)

@mcp.tool()
def tool_affine_break(ciphertext: str, top_k: int = 3) -> list[BreakResult]:
    """Break affine cipher: enumerate parameters (a,b) and return top candidates by English score.

    Purpose: Quickly crack alphabet-based affine mapping encryption.
    Usage: Provide `ciphertext`; `top_k` controls number of results (default 3).
    Returns: List of `BreakResult`; `key` is parameter pair like "a,b", with plaintext and score.
    Related: Often confused with Caesar/transposition; cross-check with other tools when needed.
    """
    return affine_break(ciphertext, top_k)

@mcp.tool()
def tool_rail_fence_break(ciphertext: str, max_rails: int = 10, top_k: int = 3) -> list[BreakResult]:
    """Break Rail Fence cipher: enumerate rail counts and return the top plaintext candidates by score.

    Purpose: Handle zig-zag write/read transposition encryption.
    Usage: `ciphertext`; `max_rails` caps rails to try (default 10); `top_k` controls number of results.
    Returns: List of `BreakResult`; `key` is rail count, with plaintext and score.
    Related: Large rail ranges increase search space; constrain based on hints if possible.
    """
    return rail_fence_break(ciphertext, max_rails, top_k)

@mcp.tool()
def tool_transposition_break(ciphertext: str, max_key_len: int = 5, top_k: int = 3) -> list[BreakResult]:
    """Break columnar transposition: small-scale enumeration of key length and permutation, returning candidates.

    Purpose: Useful for short ciphertexts common in CTF.
    Usage: `ciphertext`; `max_key_len` caps key length to try (default 5); `top_k` controls number of candidates.
    Returns: List of `BreakResult`; `key` encodes the permutation; includes plaintext and score.
    Related: Inefficient for long texts or large keys; narrow the range using problem hints.
    """
    return transposition_break(ciphertext, max_key_len, top_k)

@mcp.tool()
def tool_playfair_break(ciphertext: str, key_hint: str | None = None, top_k: int = 1) -> list[BreakResult]:
    """Decrypt Playfair using the provided key hint and score the result; return candidate plaintexts.

    Purpose: Use a given/guessed keyword to decrypt Playfair.
    Usage: Provide `key_hint`; if missing, returns an empty candidate. `top_k` defaults to 1.
    Returns: List of `BreakResult`; `key` is the keyword; includes plaintext and score.
    Related: Without a keyword, brute-force is expensive; rely on puzzle hints or wordlists.
    """
    return playfair_break(ciphertext, key_hint, top_k)

@mcp.tool()
async def tool_rc4_decrypt(ciphertext: str, cipher_encoding: str = "hex", key: str | None = None, key_encoding: str = "raw", ctx=None) -> str:
    """RC4 stream-cipher decryption. Supports interactive elicitation when the key is missing.

    Purpose: Quickly decrypt RC4 ciphertext commonly seen in stream cipher tasks.
    Usage: `ciphertext` and `cipher_encoding` (`hex`/`b64`/`raw`); `key` and `key_encoding` for the key.
           If `key` is absent and `ctx` is provided, a parameter form will be elicited.
    Returns: The decrypted plaintext string (invalid bytes are ignored).
    Related: Unlike XOR, RC4 generates a keystream; if plaintext looks garbled, verify encoding or try a different key.
    """
    return await rc4_decrypt(ciphertext, cipher_encoding, key, key_encoding, ctx)

@mcp.tool()
async def tool_factor_integer(n: str, prefer_yafu: bool = True, timeout: int = 10, ctx: Context[ServerSession, None] | None = None) -> dict:
    r"""Factor large integers. Prefer local `yafu` if available, otherwise fall back to built-in methods.

    Purpose: Factor composites commonly encountered in CTF (e.g., testing RSA moduli).
    Usage: `n` can be decimal or a string with base prefix (e.g., `0x..`);
           `prefer_yafu` selects the system `yafu` solver first; `timeout` is the external solver time limit in seconds.
    Returns: Dict `{ "n": original n string, "factors": [string factors...] }`; returning `[n]` means factoring failed.
    Related: On Windows, ensure `yafu` is on `PATH` (e.g., `D:\yafu-1.34`); increase `timeout` for large numbers.
    """
    if ctx is not None:
        await ctx.info(f"Factoring {n}")
        await ctx.report_progress(progress=0.1, total=1.0, message="Starting")
    try:
        parsed = int(n, 0)
    except Exception:
        parsed = n
    r = factor_integer(parsed, prefer_yafu, timeout)
    if ctx is not None:
        await ctx.report_progress(progress=1.0, total=1.0, message="Done")
    return {"n": r.n, "factors": r.factors}

@mcp.tool()
def tool_hash_identify(text: str) -> list[str]:
    """Heuristically identify possible hash/encoding types by length and character set.

    Purpose: Quickly suggest whether a string looks like MD5/SHA family or Base64-like.
    Usage: Provide `text`; no other parameters required.
    Returns: List of strings such as `MD5`, `SHA256`, `Base64-like`; heuristic, not definitive.
    Related: Use results to guide decoding or collision attempts; often paired with `tool_decode_common`.
    """
    return hash_identify(text)

@mcp.tool()
async def tool_aes_decrypt(ciphertext: str, cipher_encoding: str = "hex", key: str | None = None, key_encoding: str = "hex", iv: str | None = None, iv_encoding: str = "hex", mode: str = "CBC", ctx=None) -> str:
    """AES decryption (ECB/CBC) using `pycryptodome` or `cryptography` backends; supports interactive elicitation when parameters are missing.

    Purpose: Decrypt common AES tasks in CTF.
    Usage: `ciphertext` and `cipher_encoding` specify the ciphertext and its encoding; `key`/`iv` may be omitted and elicited if `ctx` is provided.
           `mode` supports `ECB`/`CBC`; plaintext is PKCS7-unpadded and returned as a string.
    Returns: Decrypted plaintext string; returns empty string if backends are unavailable or parameters are insufficient.
    Related: Ensure key/IV sizes match the mode; specify hex/Base64 encodings correctly.
    """
    return await aes_decrypt(ciphertext, cipher_encoding, key, key_encoding, iv, iv_encoding, mode, ctx)

@mcp.tool()
async def tool_des_decrypt(ciphertext: str, cipher_encoding: str = "hex", key: str | None = None, key_encoding: str = "hex", iv: str | None = None, iv_encoding: str = "hex", mode: str = "CBC", ctx=None) -> str:
    """DES decryption (ECB/CBC) using `pycryptodome` or `cryptography` backends; supports interactive elicitation.

    Purpose: Decrypt common DES tasks.
    Usage: Parameters mirror `tool_aes_decrypt`; `mode` supports `ECB`/`CBC`; returns PKCS7-unpadded plaintext.
    Returns: Plaintext string or empty string (if parameters/backends are insufficient).
    Related: DES key/IV sizes differ from AES; ensure correct mode and encoding.
    """
    return await des_decrypt(ciphertext, cipher_encoding, key, key_encoding, iv, iv_encoding, mode, ctx)

@mcp.tool()
async def tool_rot_all_wordlist(text: str, top_k: int = 3, wordlist_name: str = "common", ctx: Context[ServerSession, None] | None = None) -> list[BreakResult]:
    """Enumerate ROT and rank by a weighted score combining English frequency and wordlist matches.

    Purpose: Improve ranking when English scoring alone is insufficient.
    Usage: `text`; `wordlist_name` is a resource (e.g., `common`/`ctf`); requires `ctx` to read the wordlist resource.
    Returns: List of `BreakResult`; `confidence` is a combined score (English + wordlist hits).
    Related: Wordlists are provided via `wordlist://{name}`; use with `tool_rot_all`/`tool_caesar_break` for better results.
    """
    cands = rot_all(text, 25)
    words: list[str] = []
    if ctx is not None:
        res = await ctx.read_resource(f"wordlist://{wordlist_name}")
        try:
            # res.contents[0] is TextContent in MCP client; here assume text payload
            from mcp.types import TextContent
            if res.contents and isinstance(res.contents[0], TextContent):
                words = [x.strip() for x in res.contents[0].text.splitlines() if x.strip()]
        except Exception:
            pass
    scored = []
    for br in cands:
        ws = wordlist_score(br.plaintext, words) if words else 0.0
        es = english_score(br.plaintext)
        combined = 0.7 * es + 0.3 * ws
        scored.append(BreakResult(algorithm=br.algorithm, plaintext=br.plaintext, key=br.key, confidence=combined))
    scored.sort(key=lambda x: x.confidence, reverse=True)
    return scored[:top_k]

def main():
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        host = os.environ.get("MCP_HOST", "127.0.0.1")
        port = int(os.environ.get("MCP_PORT", "8000"))
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport="streamable-http")
    else:
        mcp.run()

if __name__ == "__main__":
    main()
