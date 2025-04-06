import asyncio
import os
from typing import Optional, Dict
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self, command: str, args: list, env:Optional[Dict[str, str]] = None):
        """Connect to an MCP server

        Args:
            command:
                "npx"
            args: 
                ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
                ["-y", "@modelcontextprotocol/server-slack"]  
            env:
                Optional environment variables dictionary
        """
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def connect_to_slack(self):
      """
      Helper method to connect to Slack MCP server
      """
      # Get slack tokens
      slack_token = os.getenv('SLACK_BOT_TOKEN')
      slack_team_id = os.getenv('SLACK_TEAM_ID')
      
      if not slack_token or not slack_team_id:
          raise EnvironmentError("Missing required environment variables")
      
      env = {
          'SLACK_BOT_TOKEN': slack_token,
          'SLACK_TEAM_ID': slack_team_id
      }

      command = "npx"
      args = ["-y", "@modelcontextprotocol/server-slack"]

      await self.connect_to_server(command, args, env)
      print("Connected to Slack MCP server")

    async def connect_to_filesystem(self, directory_path):
        """
        Helper method to connect to Filesystem MCP server with the specified directory
        
        Args:
            directory_path: Path to the directory to expose via MCP
        """
        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory does not exist: {directory_path}")
            
        command = "npx"
        args = ["-y", "@modelcontextprotocol/server-filesystem", directory_path]
        
        await self.connect_to_server(command, args)
        print(f"Connected to Filesystem MCP server with directory: {directory_path}")      

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        tool_results = []
        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Continue conversation with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                        "role": "assistant",
                        "content": content.text
                    })
                messages.append({
                    "role": "user",
                    "content": result.content
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        # Handle command line arguments
        if len(sys.argv) > 1:
            # Check if only a directory path is provided
            if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
                directory_path = sys.argv[1]
                print(f"Connecting to Filesystem MCP server with directory: {directory_path}")
                await client.connect_to_filesystem(directory_path)

            elif len(sys.argv) >= 3:
                command = sys.argv[1]
                args = sys.argv[2:]
                await client.connect_to_server(command, args)
                
            else:
                print("Usage:")
                print("  python client.py <directory_path>")
                print("  python client.py <command> <args>")
                print("  python client.py (no args to use Slack MCP server)")
                sys.exit(1)
        else:
            # Default to Slack MCP server if no arguments provided
            print("No arguments provided, connecting to Slack MCP server...")
            await client.connect_to_slack()
            
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())