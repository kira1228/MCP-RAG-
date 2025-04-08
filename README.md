# AI-powered Chat System with multiple MCP servers,

## Overview 🌟

MCP is a powerful client-server architecture that enables host applications to connect with multiple AI servers seamlessly. This system offers enhanced capabilities through specialized MCP servers:

- **MCP Filesystem**:
  Allows Claude to search and retrieve information from your specified local folders, making your documents and files accessible to the AI.

- **MCP Slack Server**:
  Connects to your Slack workspace, enabling Claude to access and reference your conversations,
  channels, and shared resources.

- **MCP Brave-Search**:
  Provides real-time web search capabilities, allowing Claude to find and incorporate the latest information from the internet.

The system intelligently determines which server to utilize based on your queries. Claude automatically analyzes your questions and decides whether to search your local files, check Slack history, or perform a web search - all without requiring explicit instructions from you.

## General Architecture 🔨

At its core, MCP follows a client-server architecture where a host application can connect to multiple servers:

<img width="737" alt="MCP Architecture Diagram" src="https://github.com/user-attachments/assets/6800d38e-3e46-42a8-bd22-479a0b6accca" />

## Getting Started! 🚀

### Prerequisites 🤝

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

### Usage 💻

Run the client with arguments for the server.

```bash
uv run client.py path/to/dir/you/want/to/use
```

## References 📖

- [About MCP](https://modelcontextprotocol.io/introduction)
- [Open source MCP servers](https://github.com/modelcontextprotocol/servers)
- [Claude API](https://docs.anthropic.com/en/api/getting-started)
