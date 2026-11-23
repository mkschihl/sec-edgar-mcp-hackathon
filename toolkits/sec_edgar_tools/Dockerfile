# syntax=docker/dockerfile:1
# Dockerfile for the sec_edgar_tools MCP server — remote streamable-HTTP deployment.
#
# Targets:
#   IBM Code Engine  (port 8080, injected as $PORT)
#   Any OCI-compliant container host
#
# Transport: MCP over streamable-HTTP at  :8080/mcp
# Health:    :8080/health   (built-in FastMCP health route)
#
# Build:
#   podman build -t sec-edgar-tools:latest -f toolkits/sec_edgar_tools/Dockerfile \
#                toolkits/sec_edgar_tools
#
# Run locally:
#   podman run --rm -p 8080:8080 sec-edgar-tools:latest
#   curl http://localhost:8080/health

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Code Engine injects PORT; we default to 8080 so local runs also work.
ENV PORT=8080

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code.
COPY server.py app.py xbrl_concepts_data.py ./

EXPOSE 8080

# app.py detects PORT and runs streamable-HTTP on 0.0.0.0:PORT.
CMD ["python", "app.py"]
