from mcp.server.fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    @mcp.prompt(title="AnalyzeCiphertext")
    def analyze(ciphertext: str) -> str:
        return "请先调用 detect_encoding 与 decode_common 获取可能解码，再尝试 rot_all 与 XOR 破解，必要时提供密钥线索。"
