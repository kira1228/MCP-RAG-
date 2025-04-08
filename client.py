import asyncio
import os
import json
from typing import Dict, List, Optional, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env


class MCPServer:
    """Class to represent an individual MCP server connection"""
    def __init__(self, name: str, session: ClientSession, tools: List[Dict[str, Any]]):
        self.name = name
        self.session = session
        self.tools = tools
        self.stdio = None
        self.write = None


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        
        # Dictionary to store multiple server connections
        self.servers: Dict[str, MCPServer] = {}
        self.active_server: Optional[str] = None

    async def connect_to_server(self, name: str, command: str, args: list, env: Optional[Dict[str, str]] = None) -> MCPServer:
        """Connect to an MCP server and add it to the servers dictionary

        Args:
            name: Identifier for this server connection
            command: Command to run (e.g., "npx")
            args: Arguments for the command
            env: Optional environment variables dictionary
            
        Returns:
            The created MCPServer object
        """
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))

        await session.initialize()

        # List available tools
        response = await session.list_tools()
        tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } 
            for tool in response.tools
        ]
        
        print(f"\nConnected to {name} server with tools:", [tool["name"] for tool in tools])
        
        # Create and store the server object
        server = MCPServer(name, session, tools)
        server.stdio = stdio
        server.write = write
        self.servers[name] = server
        
        return server

    async def connect_to_slack(self) -> MCPServer:
        """
        Helper method to connect to Slack MCP server
        """
        # Get slack tokens
        slack_token = os.getenv('SLACK_BOT_TOKEN')
        slack_team_id = os.getenv('SLACK_TEAM_ID')
        
        if not slack_token or not slack_team_id:
            raise EnvironmentError("Missing required environment variables for Slack connection")
        
        env = {
            'SLACK_BOT_TOKEN': slack_token,
            'SLACK_TEAM_ID': slack_team_id
        }

        command = "npx"
        args = ["-y", "@modelcontextprotocol/server-slack"]

        server = await self.connect_to_server("slack", command, args, env)
        print("Connected to Slack MCP server")
        return server

    async def connect_to_brave_search(self) -> MCPServer:
        """
        Helper method to connect to Brave-search MCP server        
        """ 
        # Get brave-search API Key
        brave_search_api = os.getenv('BRAVE_API_KEY')

        env = {
            "BRAVE_API_KEY": brave_search_api
        }

        if not brave_search_api:
            raise EnvironmentError("Brave-search API Key is missing, please check the .env file.")
        
        command = "npx"
        args = ["-y", "@modelcontextprotocol/server-brave-search"]

        server = await self.connect_to_server("brave-search", command, args, env)
        print("Connected Brave-search MCP server")

        return server
     
    async def connect_to_filesystem(self, directory_path) -> MCPServer:
        """
        Helper method to connect to Filesystem MCP server with the specified directory
        
        Args:
            directory_path: Path to the directory to expose via MCP
        """
        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory does not exist: {directory_path}")
            
        command = "npx"
        args = ["-y", "@modelcontextprotocol/server-filesystem", directory_path]
        
        server = await self.connect_to_server("filesystem", command, args)
        print(f"Connected to Filesystem MCP server with directory: {directory_path}")
        return server        

    async def select_server_with_llm(self, query: str) -> Optional[str]:
        """
        Use Claude to determine which server should handle the query
        
        Args:
            query: The user's query string
            
        Returns:
            Server name or None if no specific server is needed
        """
        # Create a description of available servers and their capabilities
        server_descriptions = {
            "filesystem": "Access and manipulate files and directories. Useful for reading files, listing directories, searching for files, and file operations.",
            "brave-search": "Perform web searches using Brave Search. Useful for retrieving up-to-date search results, verifying information, and exploring web content in a privacy-focused manner.",
            "slack": "Interact with Slack. Useful for listing channels, posting messages, replying to threads, adding reactions, and getting channel history or user information."
        }
        
        # Build a prompt for Claude to determine the appropriate server
        available_servers = []
        for name in self.servers.keys():
            if name in server_descriptions:
                available_servers.append(f"- {name}: {server_descriptions[name]}")
        
        # Only ask Claude if we have more than one server
        if len(self.servers) <= 1:
            return next(iter(self.servers.keys())) if self.servers else None
            
        prompt = f"""
                  Based on the following user query, determine which tool server would be most appropriate to use, or if no specific tools are needed.

                  User query: "{query}"

                  Available tool servers:
                  {chr(15).join(available_servers)}

                  You must respond with a JSON object containing a single field "server" with one of these values:

                  - The name of a server if the query clearly needs that server's tools
                  - "none" if the query is general and doesn't need specialized tools

                  Analyze the query's intent and requirements carefully. Only select a server if its tools would be genuinely helpful for addressing the query.

                  Respond only with the JSON object and nothing else.
                  """

        # Get Claude's decision
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse the response to extract the decision
        try:
            decision_text = response.content[0].text.strip()
            # Extract JSON object if it's wrapped in code blocks or has extra text
            if "```" in decision_text:
                json_text = decision_text.split("```")[1].strip()
                if json_text.startswith("json"):
                    json_text = json_text[4:].strip()
            else:
                json_text = decision_text
                
            decision = json.loads(json_text)
            selected_server = decision.get("server")
            
            if selected_server == "none":
                return None
            elif selected_server in self.servers:
                return selected_server
            else:
                print(f"Warning: LLM selected unknown server '{selected_server}'. Using no server.")
                return None
                
        except Exception as e:
            print(f"Error parsing LLM server selection: {e}")
            print(f"Raw response: {response.content[0].text}")
            return None

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        # Use LLM to determine which server to use
        server_name = await self.select_server_with_llm(query)
        
        if server_name:
            print(f"Claude determined that '{server_name}' tools would be most appropriate for this query.")
            server = self.servers[server_name]
            self.active_server = server_name
        else:
            print("Claude determined that no specific tools are needed. Using Claude without tools.")
            self.active_server = None
            
            # Process with Claude only, no tools
            messages = [{"role": "user", "content": query}]
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=messages
            )
            return response.content[0].text
        
        # Process with the selected server
        messages = [{"role": "user", "content": query}]
        
        # Initial Claude API call with the selected server's tools
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=server.tools
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

                # Execute tool call on the selected server
                result = await server.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling {server_name} tool {tool_name} with args {tool_args}]")

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
        
        # Print information about available servers
        if self.servers:
            print("\nConnected servers:")
            for name, server in self.servers.items():
                print(f"- {name}: {len(server.tools)} tools available")
            print("\nThe system will use Claude to determine which tools (if any) are needed for your query.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")
                import traceback
                traceback.print_exc()

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        # Check for directory path argument for filesystem access
        filesystem_path = None
        if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
            filesystem_path = sys.argv[1]
        
        # Connect to both servers if possible
        servers_connected = 0
        
        # Try to connect to filesystem if path provided
        if filesystem_path:
            try:
                await client.connect_to_filesystem(filesystem_path)
                servers_connected += 1
            except Exception as e:
                print(f"Failed to connect to filesystem server: {e}")
        
        # Try to connect to Slack 
        try:
            await client.connect_to_slack()
            servers_connected += 1
        except Exception as e:
            print(f"Failed to connect to Slack server: {e}")

        # Try to connect to Brave-search
        try:
            await client.connect_to_brave_search()
            servers_connected += 1
        except Exception as e:
            print(f"Failed to connect to Brave-search server: {e}")
            
        if servers_connected == 0:
            print("Warning: Failed to connect to any MCP servers. Running with Claude API only.")
            
        await client.chat_loop()
    finally:
        await client.cleanup()
        
if __name__ == "__main__":
    import sys
    asyncio.run(main())