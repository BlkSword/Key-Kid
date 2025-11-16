from mcp.server.fastmcp import FastMCP

def register_samples(mcp: FastMCP) -> None:
    @mcp.resource("samples://{id}")
    def samples(id: str) -> str:
        if id == "rot13_hello":
            return "Uryyb Jbeyq"
        if id == "xor_single_hex":
            return "3f292c2c2b"
        return ""