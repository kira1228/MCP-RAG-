# AI-powered Chat System with multiple MCP servers.

## Overview 🌟

[MCP](https://modelcontextprotocol.io/introduction) is a powerful client-server architecture that enables host applications to connect with multiple AI servers seamlessly. This system offers enhanced capabilities through specialized MCP servers:

- **[MCP Filesystem](https://github.com/modelcontextprotocol/servers/blob/main/src/filesystem/README.md)**:
  Allows Claude to search and retrieve information from your specified local folders, making your documents and files accessible to the AI.

- **[MCP Slack Server](https://github.com/modelcontextprotocol/servers/blob/main/src/slack/README.md)**:
  Connects to your Slack workspace, enabling Claude to access and reference your conversations,
  channels, and shared resources.

- **[MCP Brave-Search](https://github.com/modelcontextprotocol/servers/blob/main/src/brave-search/README.md)**:
  Provides real-time web search capabilities, allowing Claude to find and incorporate the latest information from the internet.

The system intelligently determines which server to utilize based on your queries. Claude automatically analyzes your questions and decides whether to search your local files, check Slack history, or perform a web search - all without requiring explicit instructions from you.

## General Architecture 🛠️

At its core, MCP follows a client-server architecture where a host application can connect to multiple servers:

<img width="737" alt="MCP Architecture Diagram" src="https://github.com/user-attachments/assets/6800d38e-3e46-42a8-bd22-479a0b6accca" />

## Getting Started! 🚀

### Prerequisites 🤝

You need to install `uv` to run this project.

```bash
# MacOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup ⚙️

1. Clone the repository.

```bash
git clone https://github.com/kira1228/mcp-chat-bot.git
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
# MacOS/Linux
uv venv
source .venv/bin/activate
uv sync

# Windows
uv venv
.venv\Scripts\activate
uv sync
```

### Usage 💻

Run the client with arguments for the server.

```bash
uv run client.py path/to/dir/you/want/to/use
```

## References 📚

- [About MCP](https://modelcontextprotocol.io/introduction)
- [Open source MCP servers](https://github.com/modelcontextprotocol/servers)
- [Claude API](https://docs.anthropic.com/en/api/getting-started)
- [Brave search API]

## License 🔑
This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
