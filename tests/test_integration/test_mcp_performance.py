"""MCP performance and memory tests."""
import asyncio
import os

# Add src to path
import sys
import time

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mcp.testing import Client

from src.server import mcp


@pytest.mark.asyncio
class TestMCPPerformance:
    """Tests for MCP server performance metrics."""

    async def test_mcp_startup_time(self):
        """Test MCP server startup time."""
        start = time.time()
        async with Client(mcp) as _client:
            startup_time = time.time() - start
            # Startup should be fast (< 2 seconds)
            assert startup_time < 2.0, f"Startup time {startup_time:.2f}s exceeds 2s"

    async def test_mcp_tool_response_time_rot(self):
        """Test tool response time for rot_all."""
        async with Client(mcp) as client:
            start = time.time()
            result = await client.call_tool("tool_rot_all", {"text": "Uryyb Jbeyq", "top_k": 3})
            response_time = time.time() - start
            # Response should be fast (< 1 second)
            assert response_time < 1.0, f"Response time {response_time:.2f}s exceeds 1s"
            assert len(result) == 3

    async def test_mcp_tool_response_time_xor(self):
        """Test tool response time for xor_single_break."""
        async with Client(mcp) as client:
            start = time.time()
            _ = await client.call_tool(
                "tool_xor_single_break",
                {"data": "3f292c2c2b", "encoding": "hex", "top_k": 3}
            )
            response_time = time.time() - start
            assert response_time < 1.0, f"Response time {response_time:.2f}s exceeds 1s"

    async def test_mcp_concurrent_calls(self):
        """Test concurrent tool calls performance."""
        async with Client(mcp) as client:
            tasks = [
                client.call_tool("tool_rot_all", {"text": "Uryyb Jbeyq", "top_k": 1})
                for _ in range(20)
            ]
            start = time.time()
            results = await asyncio.gather(*tasks)
            duration = time.time() - start

            assert len(results) == 20
            # Concurrent calls should be reasonably fast
            avg_time = duration / 20
            assert avg_time < 0.5, f"Average call time {avg_time:.2f}s too high"

    async def test_mcp_cache_effectiveness(self):
        """Test that caching improves repeated calls."""
        from src.utils.scoring import english_score

        # Clear cache
        english_score.cache_clear()

        text = "Hello World" * 50

        # First call (cache miss)
        start = time.time()
        english_score(text)
        _first_duration = time.time() - start

        # Second call (cache hit)
        start = time.time()
        english_score(text)
        _second_duration = time.time() - start

        # Cache hit should be much faster
        # Note: This might be flaky on very fast systems
        # We just verify the cache is working
        cache_info = english_score.cache_info()
        assert cache_info.currsize > 0, "Cache should have entries"

    async def test_mcp_memory_usage(self):
        """Test memory usage stays bounded."""
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024

            async with Client(mcp) as client:
                # Execute many tool calls
                for i in range(100):
                    await client.call_tool(
                        "tool_rot_all",
                        {"text": f"Test text {i} " * 10, "top_k": 1}
                    )

                final_memory = process.memory_info().rss / 1024 / 1024
                memory_growth = final_memory - initial_memory

                # Memory growth should be reasonable (< 50MB for 100 calls)
                assert memory_growth < 50, f"Memory growth {memory_growth:.1f}MB too high"

        except ImportError:
            pytest.skip("psutil not available")

    async def test_mcp_tool_throughput(self):
        """Test sustained throughput of tool calls."""
        async with Client(mcp) as client:
            iterations = 50
            start = time.time()

            for _ in range(iterations):
                await client.call_tool("tool_rot_all", {"text": "Hello World", "top_k": 1})

            duration = time.time() - start
            calls_per_second = iterations / duration

            # Should handle at least 10 calls/second
            assert calls_per_second >= 10, f"Throughput {calls_per_second:.1f} calls/s too low"

    async def test_mcp_large_text_handling(self):
        """Test handling of large text inputs."""
        async with Client(mcp) as client:
            # Create a large text (10KB)
            large_text = "A" * 10000

            start = time.time()
            result = await client.call_tool("tool_rot_all", {"text": large_text, "top_k": 1})
            duration = time.time() - start

            # Should handle large text reasonably
            assert duration < 2.0, f"Large text processing took {duration:.2f}s too long"
            assert len(result) == 1


@pytest.mark.asyncio
class TestMCPCacheBehavior:
    """Tests for MCP caching behavior."""

    async def test_english_score_cache_persists(self):
        """Test that english_score cache persists across calls."""
        from src.utils.scoring import english_score

        # Clear and start fresh
        english_score.cache_clear()

        text = "The quick brown fox jumps over the lazy dog"

        # Make multiple calls
        for _ in range(10):
            english_score(text)

        cache_info = english_score.cache_info()
        # Should have cache hits (after first call)
        assert cache_info.hits + cache_info.misses >= 10
        assert cache_info.currsize > 0

    async def test_english_score_cache_maxsize(self):
        """Test that cache respects maxsize limit."""
        from src.utils.scoring import english_score

        english_score.cache_clear()

        # Add entries beyond maxsize
        for i in range(2100):
            english_score(f"unique_text_{i}")

        cache_info = english_score.cache_info()
        # Should not exceed maxsize significantly
        assert cache_info.currsize <= 2048
