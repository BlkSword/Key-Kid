# Standard Key-Kid image without SageMath.
# For the SageMath-enabled variant, see Dockerfile.sagemath.
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the package in editable mode with dev extras for testing.
COPY pyproject.toml .
COPY src ./src
COPY tests ./tests
COPY scripts ./scripts
RUN pip install --no-cache-dir -e ".[dev]"

# Default to stdio transport; override with MCP_TRANSPORT if desired.
ENV MCP_TRANSPORT=stdio
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "src/server.py"]
