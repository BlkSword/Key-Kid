from mcp.server.fastmcp import FastMCP

COMMON = "the\nof\nand\nto\nin\nis\nyou\nthat\nit\nfor\non\nwith\nas\nI\nthis\nbe\nat\nby\nnot\nor\nare\nfrom\n".strip()
CTF_KEYS = "flag\nkey\npassword\nadmin\nctf\nroot\nuser\nsolve\nsecret\n".strip()

def register_wordlist(mcp: FastMCP) -> None:
    @mcp.resource("wordlist://{name}")
    def wordlist(name: str) -> str:
        if name == "common":
            return COMMON
        if name == "ctf":
            return CTF_KEYS
        return ""