# AI-powered Chat System with multiple MCP servers,

## Overview

MCP is a powerful client-server architecture that enables host applications to connect with multiple AI servers seamlessly.

## General Architecture

At its core, MCP follows a client-server architecture where a host application can connect to multiple servers:

<img width="737" alt="MCP Architecture Diagram" src="https://github.com/user-attachments/assets/6800d38e-3e46-42a8-bd22-479a0b6accca" />

## Getting Started! 🚀

### Prerequisites

You need to install `uv` to run this project.

```bash
brew install uv
```

### Setup

1. Clone the repository.

```bash
git clone https://github.com/megmogmog1965/example-mcp-client.git
cd mcp-chat-bot
```

2. Create a `.env` file with your API keys:

```bash
# Create the .env file
touch .env

# Add your API credentials
# ANTHROPIC_API_KEY: Used for Claude AI integration
echo "ANTHROPIC_API_KEY=<your api key>" >> .env

# SLACK_BOT_TOKEN & SLACK_TEAM_ID: Required for Slack integration
echo "SLACK_BOT_TOKEN=<your api key>" >> .env
echo "SLACK_TEAM_ID=<your api key>" >> .env

# BRAVE_API_KEY: Used for Brave search capabilities
echo "BRAVE_API_KEY=<your api key>" >> .env
```

3. Create a virtual environment and install the dependencies.

```bash
uv venv
source .venv/bin/activate
uv sync
```

### Usage

Run the client with arguments for the server.

```bash
uv run client.py path/to/dir/you/want/to/use
```

## References

- [About MCP](https://modelcontextprotocol.io/introduction)
- [Open source MCP servers](https://github.com/modelcontextprotocol/servers)
- [Claude API](https://docs.anthropic.com/en/api/getting-started)
