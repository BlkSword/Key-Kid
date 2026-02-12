"""MCP protocol integration tests."""

import os
import sys

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mcp.testing import Client

from src.server import mcp


@pytest.mark.asyncio
class TestMCPProtocol:
    """Tests for MCP protocol compliance."""

    async def test_mcp_tool_list(self):
        """Test MCP tool listing."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            assert len(tools) >= 18
            tool_names = [t.name for t in tools]
            # Check key tools exist
            assert "tool_rot_all" in tool_names
            assert "tool_caesar_break" in tool_names
            assert "tool_xor_single_break" in tool_names
            assert "tool_vigenere_break" in tool_names

    async def test_mcp_tool_call_rot_all(self):
        """Test MCP tool call for rot_all."""
        async with Client(mcp) as client:
            result = await client.call_tool("tool_rot_all", {"text": "Uryyb Jbeyq", "top_k": 1})
            assert len(result) == 1
            # Result should be a list of BreakResult
            assert "plaintext" in result[0] or len(result[0]) > 0

    async def test_mcp_tool_call_caesar_break(self):
        """Test MCP tool call for caesar_break."""
        async with Client(mcp) as client:
            result = await client.call_tool("tool_caesar_break", {"ciphertext": "Uryyb Jbeyq"})
            assert len(result) == 1

    async def test_mcp_tool_call_xor_single_break(self):
        """Test MCP tool call for xor_single_break."""
        async with Client(mcp) as client:
            result = await client.call_tool(
                "tool_xor_single_break", {"data": "3f292c2c2b", "encoding": "hex", "top_k": 1}
            )
            assert len(result) >= 1

    async def test_mcp_tool_call_detect_encoding(self):
        """Test MCP tool call for detect_encoding."""
        async with Client(mcp) as client:
            result = await client.call_tool(
                "tool_detect_encoding", {"text": "SGVsbG8gd29ybGQ=", "top_k": 5}
            )
            assert len(result) >= 1

    async def test_mcp_resources(self):
        """Test MCP resource access."""
        async with Client(mcp) as client:
            resources = await client.list_resources()
            assert len(resources) > 0
            # Check for wordlist resources
            resource_names = [r.uri for r in resources]
            assert any("wordlist" in uri for uri in resource_names)

    async def test_mcp_prompts(self):
        """Test MCP prompt templates."""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            assert len(prompts) > 0

    async def test_mcp_resource_read_wordlist(self):
        """Test reading wordlist resource."""
        async with Client(mcp) as client:
            # Try to read the common wordlist
            result = await client.read_resource("wordlist://common")
            assert result is not None
            assert len(result.contents) > 0

    async def test_mcp_concurrent_tool_calls(self):
        """Test concurrent tool calls."""
        import asyncio

        async with Client(mcp) as client:
            tasks = [
                client.call_tool("tool_rot_all", {"text": "Uryyb Jbeyq", "top_k": 1})
                for _ in range(5)
            ]
            results = await asyncio.gather(*tasks)
            assert len(results) == 5

    async def test_mcp_tool_error_handling(self):
        """Test MCP tool handles invalid input gracefully."""
        async with Client(mcp) as client:
            # Should not raise exception, but handle gracefully
            result = await client.call_tool("tool_rot_all", {"text": "", "top_k": 1})
            # Should return results even for empty input
            assert result is not None

    async def test_mcp_tool_vigenere_break(self):
        """Test MCP tool call for vigenere_break."""
        async with Client(mcp) as client:
            result = await client.call_tool(
                "tool_vigenere_break", {"ciphertext": "Lxfopvefrnhr", "max_key_len": 8, "top_k": 1}
            )
            assert len(result) >= 1

    async def test_mcp_tool_affine_break(self):
        """Test MCP tool call for affine_break."""
        async with Client(mcp) as client:
            result = await client.call_tool(
                "tool_affine_break", {"ciphertext": "ZEBBW", "top_k": 1}
            )
            assert len(result) >= 1

    async def test_mcp_tool_rail_fence_break(self):
        """Test MCP tool call for rail_fence_break."""
        async with Client(mcp) as client:
            result = await client.call_tool(
                "tool_rail_fence_break",
                {"ciphertext": "WECRLTEERDSOEEFEAOCAIVDEN", "max_rails": 5, "top_k": 1},
            )
            assert len(result) >= 1
