# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Add MCP server name label for registry validation
LABEL io.modelcontextprotocol.server.name="mcp-reddit"
LABEL org.opencontainers.image.title="Reddit MCP Server"
LABEL org.opencontainers.image.description="Model Context Protocol server for Reddit integration"
LABEL org.opencontainers.image.source="https://github.com/KrishnaRandad2023/mcp-reddit"
LABEL org.opencontainers.image.licenses="MIT"

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy source code
COPY src/ .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Set Python path
ENV PYTHONPATH=/app

# Set environment variables for MCP
ENV MCP_TRANSPORT=stdio

# Run the server
ENTRYPOINT ["python", "server.py"]