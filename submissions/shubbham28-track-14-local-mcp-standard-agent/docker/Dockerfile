# Unified container running all MCP servers and Streamlit client
# Use Playwright base to ensure headless Chromium works
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# System settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501

WORKDIR /app

# Copy project
COPY . /app

# Install dependencies
RUN python -m pip install --upgrade pip \
    && python -m pip install -e 'mcp-agent[browser]' \
    && python -m pip install streamlit pandas \
    && playwright install chromium

# Ensure start script is executable
RUN chmod +x /app/mcp-agent/scripts/start_all.sh || true

EXPOSE 8001 8002 8003 8501

# Default entrypoint starts all MCP servers and Streamlit
CMD ["/app/mcp-agent/scripts/start_all.sh"]
