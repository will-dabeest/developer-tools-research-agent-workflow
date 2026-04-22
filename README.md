# Advanced Agent

CLI agent and MCP server for researching developer tools using Firecrawl + LangGraph + Ollama.

It takes a user query (for example, `vector databases`), finds relevant tools, scrapes key pages, runs structured analysis, and prints concise recommendations. It can run as a standalone CLI or be exposed as an MCP tool for use with Claude and other MCP clients.

## Requirements

- Python `>=3.11,<3.14`
- `uv` installed
- Node.js and `npx` (used to run the Firecrawl MCP server)
- Firecrawl API key
- Ollama running locally

## Quick Start

1. Install dependencies:

```bash
uv sync
```

2. Create env file:

```bash
cp .env.example .env
```

3. Set required values in `.env`:

- `FIRECRAWL_API_KEY` (required)
- `OLLAMA_MODEL` and `OLLAMA_BASE_URL` (defaults are usually fine)

4. Start Ollama and ensure the model exists:

```bash
ollama serve
ollama pull qwen2.5:1.5b
```

5. Run the app:

```bash
uv run .\main.py
```

Type your query at the prompt. Use `exit` or `quit` to stop.

## How It Works

1. Extract likely tool names from search content
2. Research each tool's official pages
3. Analyze results into structured fields (pricing, OSS, APIs, integrations)
4. Generate a short recommendation summary

## Run as MCP Server

The workflow is also exposed as an MCP tool (`research_dev_tools`) via `server.py`. To use it with Claude Desktop or another MCP client, add this to your MCP client config:

```json
{
  "mcpServers": {
    "dev-tools-researcher": {
      "command": "uv",
      "args": ["run", "research-mcp-server"],
      "env": {
        "FIRECRAWL_API_KEY": "<your-key>"
      }
    }
  }
}
```

Or run directly:

```bash
uv run research-mcp-server
```

## Project Structure

- `main.py` — CLI loop and output formatting
- `server.py` — MCP server exposing the workflow as a `research_dev_tools` tool
- `src/workflow.py` — LangGraph workflow orchestration
- `src/firecrawl.py` — Firecrawl MCP client (search/scrape via `npx firecrawl-mcp`)
- `src/models.py` — Pydantic state/result models
- `src/prompts.py` — Prompt templates

## Run with Docker (Local)

Build image locally:

```bash
docker build -t advanced-agent:local .
```

Run interactively with env vars:

```bash
docker run --rm -it --env-file .env advanced-agent:local
```

## Run Tests

Install dev dependencies and run tests:

```bash
uv sync --dev
uv run pytest -q
```

## Publish with GitHub Actions (GHCR)

This repo includes [.github/workflows/docker.yml](.github/workflows/docker.yml).

- On pull requests: runs tests, then builds image only (no push)
- On `main`/`master` push: builds and pushes to GHCR
- On version tag push (for example `v1.2.3`): publishes semver tags (`1.2.3`, `1.2`, `1`)
- On manual trigger: builds and pushes

Example:

```bash
git tag v1.2.3
git push origin v1.2.3
```

Published image name:

```text
ghcr.io/<owner>/<repo>:latest
```

After first push, make sure the GHCR package visibility is set as desired (public/private).

Run published image anywhere locally:

```bash
docker run --rm -it \
  --env-file .env \
  ghcr.io/<owner>/<repo>:latest
```

## Common Issues

- **`FIRECRAWL_API_KEY is required...`**
  - Add a valid key to `.env`.

- **`npx: command not found` or Firecrawl MCP errors**
  - Install Node.js (which includes `npx`). The Firecrawl MCP server is launched automatically via `npx firecrawl-mcp`.

- **Ollama connection/model errors**
  - Start Ollama (`ollama serve`) and pull the configured model.

- **Python/import warnings in editor**
  - Make sure VS Code is using this project's interpreter: `advanced-agent/.venv`.

- **Container exits or fails on startup**
  - Confirm `.env` includes valid `FIRECRAWL_API_KEY` and Ollama settings.
  - If using local Ollama from inside Docker, set `OLLAMA_BASE_URL` to a host-reachable address (for example `http://host.docker.internal:11434`).
