# Minecraft Bedrock MCP Server Setup Guide

This guide will help you set up an MCP server that allows Claude Desktop to interact with your Minecraft Bedrock Edition server.

## Prerequisites

### 1. Minecraft Bedrock Dedicated Server
Download the Bedrock Dedicated Server from:
- [Official Minecraft Website](https://www.minecraft.net/en-us/download/server/bedrock)

### 2. Python Requirements
```bash
# Install required packages
pip install mcp

# Or if using uv:
uv add mcp
```

## Installation

### 1. Create Project Directory
```bash
mkdir minecraft-bedrock-mcp
cd minecraft-bedrock-mcp
```

### 2. Save the Server Code
Save the Python code as `bedrock_mcp_server.py` in your project directory.

### 3. Make it Executable
```bash
chmod +x bedrock_mcp_server.py
```

## Configuration

### 1. Bedrock Server Setup
1. Extract the Bedrock Dedicated Server to a directory (e.g., `/path/to/bedrock-server/`)
2. Configure your `server.properties` file as needed
3. Make sure the server can run independently first

### 2. Claude Desktop Configuration
Add this to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "minecraft-bedrock": {
      "command": "python",
      "args": [
        "/ABSOLUTE/PATH/TO/bedrock_mcp_server.py",
        "--server-path",
        "/ABSOLUTE/PATH/TO/BEDROCK-SERVER-DIRECTORY",
        "--auto-start"
      ]
    }
  }
}
```

**Important**: Replace the paths with your actual absolute paths!

## Usage

### Starting the Server

#### Option 1: Manual Server Start
1. Start your Bedrock server manually first
2. Run the MCP server without `--auto-start`:
```bash
python bedrock_mcp_server.py --server-path /path/to/bedrock-server
```

#### Option 2: Auto-start (Recommended)
Let the MCP server start the Bedrock server automatically:
```bash
python bedrock_mcp_server.py --server-path /path/to/bedrock-server --auto-start
```

### Available Commands in Claude

Once connected, you can ask Claude to:

1. **Server Management**
   - "What's the server status?"
   - "Show me recent server logs"
   - "Who's online right now?"

2. **Player Management**
   - "Teleport Steve to coordinates 100, 70, 200"
   - "Give Alex a diamond sword"
   - "Give all players 64 cooked beef"

3. **World Management**
   - "Set the time to day"
   - "Make it rain for 300 seconds"
   - "Clear the weather"

4. **Custom Commands**
   - "Send the command 'say Hello everyone!'"
   - "Run the list command"

## Troubleshooting

### Common Issues

#### 1. Server Won't Start
- Check that the Bedrock server path is correct
- Ensure the `bedrock_server` executable exists and has execute permissions
- Verify server.properties is properly configured

#### 2. Commands Not Working
- Make sure the Bedrock server is running and accessible
- Check server logs for any error messages
- Verify that operator permissions are set correctly

#### 3. Connection Issues
- Ensure the MCP server is pointing to the correct Bedrock server directory
- Check that no other processes are using the server

#### 4. Player Names Not Recognized
- Make sure players are actually connected to the server
- Player names are case-sensitive

### Log Locations
- MCP Server logs: Console output where you ran the script
- Bedrock Server logs: Usually in the server directory or console output

## Supported Commands

The MCP server supports these Minecraft Bedrock commands:

### Administrative
- `list` - List online players
- `say <message>` - Send message to all players
- `tell <player> <message>` - Send private message

### Player Management
- `tp <player> <x> <y> <z>` - Teleport player
- `give <player> <item> [amount]` - Give items
- `gamemode <mode> [player]` - Change game mode

### World Management
- `time set <time>` - Set time (day, night, noon, midnight, or tick value)
- `weather <type> [duration]` - Set weather (clear, rain, thunder)
- `difficulty <level>` - Set difficulty

### Server Control
- `stop` - Stop the server (use with caution!)
- `save-all` - Force save the world

## Example Interactions

```
User: "What's happening on the server?"
Claude: [Uses get-server-status and get-server-logs tools]

User: "Give everyone 64 bread"
Claude: [Uses list-players, then give-item for each player]

User: "Make it daytime and clear weather"
Claude: [Uses set-time with "day" and set-weather with "clear"]

User: "Teleport all players to spawn"
Claude: [Uses list-players, then teleport-player for each to 0,70,0]
```

## Security Notes

- This MCP server can execute any command on your Minecraft server
- Only use with trusted Claude Desktop installations
- Consider running the Bedrock server in a sandboxed environment
- Be careful with the `stop` command as it will shut down your server

## Advanced Configuration

### Custom Server Commands
You can extend the server by adding more tools in the `handle_list_tools()` function. Common additions might include:

- World backup tools
- Player statistics
- Custom plugin commands
- Automated server maintenance

### Multiple Servers
To manage multiple Bedrock servers, you can run multiple instances of this MCP server with different configurations in your Claude Desktop config.