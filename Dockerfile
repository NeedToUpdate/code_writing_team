# Dockerfile for code_writing_team MCP Agent - All-in-one container
ARG NPM_SERVER_REF=main

FROM node:20-alpine AS build_npm_mcp
ARG NPM_SERVER_REF
RUN apk add --no-cache git
WORKDIR /app

# pull the server code
RUN git clone --depth 1 --branch ${NPM_SERVER_REF} \
    https://github.com/seido/mcp_npm.git .

# 1. install EVERYTHING (prod + dev) so tsc is present
RUN npm ci

# 2. compile TypeScript to JS
RUN npm run build

# 3. strip dev deps, leaving prod-only node_modules
RUN npm prune --omit=dev

# ---------- runtime stage ----------------------------------------------


FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim AS base

# Set working directory
WORKDIR /app

# Copy the built NPM MCP server from the build stage
COPY --from=build_npm_mcp /app /mcp_npm

# Install system dependencies, upgrade pip, install NPM MCP servers globally
RUN apt-get update && apt-get install -y \
    git \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && npm install -g @modelcontextprotocol/server-filesystem @cyanheads/git-mcp-server

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code_writing_team application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    GIT_MCP_BASE_DIR="/app"

# Configure git to use environment variables
RUN git config --global user.name "${GIT_AUTHOR_NAME}" && \
    git config --global user.email "${GIT_AUTHOR_EMAIL}"

# Default command (can be overridden in docker-compose.yml), nbut its in TICKET_ID
CMD ["python", "main.py", "$TICKET_ID"]