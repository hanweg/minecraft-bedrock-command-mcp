### Server Commands
- `list` - List online players
- `say <message>` - Broadcast message to all players
- `save-all` - Force save the world
- `stop` - Stop the server

## 🎨 Building Examples

### Quick Structures
```bash
# Build a simple house
# Ask Claude: "Build a stone house, size 5, at coordinates 0, 70, 0"

# Create a pyramid  
# Ask Claude: "Make a diamond pyramid, size 10, at 100, 60, 100"

# Build a tower
# Ask Claude: "Create a cobblestone tower, size 3, height 20, at 50, 60, 50"
```

### Advanced Building
```bash
# Fill large areas
# "Fill the area from -50,60,-50 to 50,80,50 with grass blocks"

# Create hollow structures  
# "Fill from 0,60,0 to 20,80,20 with stone bricks, but make it hollow"

# Replace specific blocks
# "Fill from 10,60,10 to 30,70,30 with oak planks, but only replace dirt blocks"
```

### Structure Templates
```bash
# Save your builds
# "Save the structure from 0,60,0 to 50,100,50 as 'my_mansion'"

# Load saved structures
# "Load the 'my_mansion' template at coordinates 200, 60, 200"

# Clone existing builds
# "Copy the building from 100,60,100 to 150,90,150 and paste it at 300,60,300"
```

### Creative Projects
```bash
# Spawn decorative entities
# "Summon 5 armor stands in a circle around coordinates 0, 70, 0"

# Create particle effects
# "Create flame particles at coordinates 25, 75, 25"

# Build complex structures
# "Create a 50x50 glass dome at coordinates 0, 60, 0"
```

## 🏗️ Common Building Materials

Bedrock Edition supports these common block types:
- **Stone types**: `stone`, `cobblestone`, `stone_bricks`, `smooth_stone`
- **Wood types**: `oak_planks`, `birch_planks`, `spruce_planks`, `jungle_planks`
- **Decorative**: `glass`, `stained_glass`, `wool`, `concrete`
- **Precious**: `diamond_block`, `gold_block`, `iron_block`, `emerald_block`
- **Natural**: `dirt`, `grass`, `sand`, `gravel`, `water`, `lava`
- **Special**: `air` (removes blocks), `barrier` (invisible blocks)# Minecraft Bedrock MCP Server

A Model Context Protocol (MCP) server that enables AI assistants like Claude to interact with Minecraft Bedrock Edition servers through natural language commands.

![Minecraft Bedrock MCP](https://img.shields.io/badge/Minecraft-Bedrock%20Edition-green)
![MCP](https://img.shields.io/badge/MCP-Compatible-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow)

## 🎯 Overview

This MCP server bridges the gap between AI assistants and Minecraft Bedrock Edition servers, allowing you to:

- **Manage your server** through natural language commands
- **Control player actions** (teleportation, item giving, etc.)
- **Monitor server status** and player activity in real-time
- **Automate world management** (time, weather, etc.)

Unlike Minecraft Java Edition which uses RCON, Bedrock Edition requires direct process communication, which this server handles seamlessly.

## ✨ Features

### 🎮 Server Management
- Start and monitor Bedrock Dedicated Server processes
- Real-time log parsing and monitoring
- Server status reporting
- Graceful server shutdown

### 👥 Player Management  
- List online players
- Teleport players to specific coordinates
- Give items to players
- Send messages to players

### 🌍 World Control
- Set time of day (day, night, noon, midnight, or specific ticks)
- Control weather (clear, rain, thunder)
- Execute any Bedrock server command

### 🏗️ Building & Construction
- **Block Placement**: Place individual blocks with `setblock`
- **Area Filling**: Fill large areas with blocks using `fill` command
- **Structure Cloning**: Copy and paste structures with `clone`
- **Structure Templates**: Save and load reusable structure templates
- **Quick Buildings**: Create common structures (houses, towers, walls, pyramids)
- **Entity Spawning**: Summon mobs, items, and other entities
- **Particle Effects**: Create visual effects and particles

### 📊 Monitoring
- Real-time server logs
- Player join/leave tracking
- Command execution feedback
- Error handling and reporting

## 🚀 Quick Start

### Prerequisites

1. **Minecraft Bedrock Dedicated Server**
   - Download from [minecraft.net/download/server/bedrock](https://www.minecraft.net/en-us/download/server/bedrock)
   - Extract and configure your server

2. **Python 3.10+**
   ```bash
   python --version  # Should be 3.10 or higher
   ```

3. **MCP Python SDK**
   ```bash
   pip install mcp
   # or
   uv add mcp
   ```

### Installation

1. **Clone or download** this repository
2. **Save** `bedrock_mcp_server.py` to your desired location
3. **Make it executable** (Linux/macOS):
   ```bash
   chmod +x bedrock_mcp_server.py
   ```

### Configuration

#### 1. Test Your Bedrock Server
First, ensure your Bedrock server runs independently:
```bash
cd /path/to/your/bedrock-server
./bedrock_server  # or bedrock_server.exe on Windows
```

#### 2. Configure Claude Desktop
Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

**⚠️ Important**: Use absolute paths, not relative ones!

#### Example Paths:
- **macOS/Linux**: `/Users/username/minecraft/bedrock-server`
- **Windows**: `C:\\Users\\username\\minecraft\\bedrock-server`

#### Example Claude Desktop Config:
```json
{
  "mcpServers": {
    "minecraft-bedrock": {
      "command": "/ABSOLUTE/PATH/TO/PROJECT/.venv/bin/python",
      "args": [
        "/ABSOLUTE/PATH/TO/PROJECT/bedrock_mcp_server.py",
        "--server-path",
        "/ABSOLUTE/PATH/TO/BEDROCK-SERVER-DIRECTORY",
        "--auto-start"
      ]
    }
  }
}
```

**Windows example:**
```json
{
  "mcpServers": {
    "minecraft-bedrock": {
      "command": "C:\\Users\\YourName\\minecraft-bedrock-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\YourName\\minecraft-bedrock-mcp\\bedrock_mcp_server.py",
        "--server-path",
        "C:\\MinecraftServer",
        "--auto-start"
      ]
    }
  }
}
```

### Usage

#### Starting the MCP Server

**Option 1: Auto-start Bedrock Server (Recommended)**
```powershell
# Windows
python bedrock_mcp_server.py --server-path C:\MinecraftServer --auto-start
```

```bash
# Linux/macOS
python bedrock_mcp_server.py --server-path /path/to/bedrock-server --auto-start
```

**Option 2: Connect to Running Server**
```powershell
# Start your Bedrock server first, then:
# Windows
python bedrock_mcp_server.py --server-path C:\MinecraftServer
```

```bash
# Linux/macOS
python bedrock_mcp_server.py --server-path /path/to/bedrock-server
```

#### Restart Claude Desktop
After configuring, restart Claude Desktop to load the MCP server.

## 💬 Example Conversations

Once connected, you can interact with your Minecraft server through Claude:

### Server Status
```
You: "What's the status of my Minecraft server?"
Claude: [Checks server status, shows online players and recent activity]
```

### Player Management
```
You: "Teleport Steve to coordinates 100, 70, 200"
Claude: [Executes teleport command and confirms success]

You: "Give everyone 64 cooked beef"
Claude: [Lists players and gives items to each one]
```

### Building & Construction
```
You: "Build a 10x10 stone house at coordinates 100, 70, 200"
Claude: [Uses create-simple-building to construct a house]

You: "Fill the area from 0,60,0 to 50,80,50 with glass to make a giant cube"
Claude: [Uses fill command to create a massive glass structure]

You: "Place a diamond block at 10, 65, 10"
Claude: [Uses setblock to place the specific block]

You: "Copy the building from 100,70,100 to 120,80,120 and paste it at 200,70,200"
Claude: [Uses clone command to duplicate the structure]
```

### World Control
```
You: "Make it daytime and clear the weather"
Claude: [Sets time to day and weather to clear]

You: "Start a thunderstorm for 5 minutes"
Claude: [Sets weather to thunder for 300 seconds]
```

### Building & Construction
```
You: "Build a 10x10 stone house at coordinates 100, 70, 200"
Claude: [Uses create-simple-building to construct a house]

You: "Fill the area from 0,60,0 to 50,80,50 with glass to make a giant cube"
Claude: [Uses fill command to create a massive glass structure]

You: "Place a diamond block at 10, 65, 10"
Claude: [Uses setblock to place the specific block]

You: "Copy the building from 100,70,100 to 120,80,120 and paste it at 200,70,200"
Claude: [Uses clone command to duplicate the structure]
```

### Creative Projects
```
You: "Create a pyramid made of gold blocks, size 20, at spawn"
Claude: [Uses create-simple-building with pyramid type]

You: "Summon 10 cows around coordinates 150, 70, 150"
Claude: [Uses summon command multiple times with slight coordinate variations]

You: "Save the castle I built from 50,60,50 to 100,90,100 as 'my_castle'"
Claude: [Uses structure-save to preserve the build as a template]

You: "Load my_castle template at coordinates 300, 70, 300"
Claude: [Uses structure-load to place the saved structure]
```

### Advanced Commands
```
You: "Show me the last 15 lines of server logs"
Claude: [Retrieves and displays recent server logs]

You: "Send a message saying 'Server restart in 5 minutes' to all players"
Claude: [Uses the say command to broadcast the message]
```

## 🛠️ Available Tools

The MCP server provides these tools to Claude:

| Tool | Description | Example |
|------|-------------|---------|
| `send-command` | Execute any Bedrock server command | `say Hello everyone!` |
| `get-server-status` | Get server status and player count | - |
| `list-players` | List all online players | - |
| `get-server-logs` | Retrieve recent server logs | Last 20 lines |
| `teleport-player` | Teleport a player to coordinates | Steve to (100, 70, 200) |
| `give-item` | Give items to a player | 64 diamond to Alex |
| `set-time` | Set the world time | day, night, noon, midnight |
| `set-weather` | Change weather conditions | clear, rain, thunder |
| **Building Tools** | | |
| `setblock` | Place a single block | Stone at (10, 65, 10) |
| `fill` | Fill rectangular areas with blocks | Glass cube 20x20x20 |
| `clone` | Copy and paste structures | Duplicate building |
| `structure-save` | Save structures as templates | Save castle as 'my_castle' |
| `structure-load` | Load saved structure templates | Place 'my_castle' at coords |
| `summon` | Spawn entities (mobs, items) | Spawn cow at (100, 70, 100) |
| `particle` | Create particle effects | Flame particles at location |
| `create-simple-building` | Build common structures | House, tower, pyramid, wall |

## 🔧 Command Line Options

```bash
python bedrock_mcp_server.py [OPTIONS]

Options:
  --server-path PATH     Path to Bedrock server directory or executable (required)
  --auto-start          Automatically start the Bedrock server if not running
  --help               Show help message
```

## 📋 Supported Minecraft Commands

The server supports all standard Bedrock Edition commands:

### Player Commands
- `tp <player> <x> <y> <z>` - Teleport player
- `give <player> <item> [amount]` - Give items to player
- `gamemode <mode> [player]` - Change player's game mode
- `tell <player> <message>` - Send private message to player

### World Commands  
- `time set <value>` - Set world time
- `weather <type> [duration]` - Control weather
- `difficulty <level>` - Set difficulty level
- `gamerule <rule> <value>` - Modify game rules

### Building Commands
- `setblock <x> <y> <z> <block> [mode]` - Place single block
- `fill <x1> <y1> <z1> <x2> <y2> <z2> <block> [mode]` - Fill area with blocks
- `clone <x1> <y1> <z1> <x2> <y2> <z2> <destX> <destY> <destZ> [mode]` - Copy structures
- `structure save <name> <x1> <y1> <z1> <x2> <y2> <z2>` - Save structure template
- `structure load <name> <x> <y> <z>` - Load structure template

### Entity Commands
- `summon <entity> <x> <y> <z> [nbt]` - Spawn entities
- `particle <type> <x> <y> <z>` - Create particle effects
- `kill @e[type=<entity>]` - Remove specific entity types

## 🐛 Troubleshooting

### Common Issues

#### Server Won't Connect
```
Error: Bedrock server executable not found
```
**Solution**: Check that your `--server-path` points to the directory containing `bedrock_server` or `bedrock_server.exe`

#### Commands Not Working
```
Error: Server is not running
```
**Solution**: 
- Use `--auto-start` flag, or
- Start your Bedrock server manually first

#### Claude Can't See the Tools
**Check**:
1. Claude Desktop config file syntax is valid JSON
2. Paths are absolute, not relative
3. You've restarted Claude Desktop after configuration changes

#### Permission Errors
```
Error: Permission denied
```
**Solution**:
- Make sure the script is executable: `chmod +x bedrock_mcp_server.py`
- Run with appropriate permissions for the Bedrock server directory

### Debug Mode

Add logging to see what's happening:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Locations
- **MCP Server logs**: Console output where you ran the script
- **Bedrock Server logs**: Server console or log files in server directory

## 🔒 Security Considerations

⚠️ **Important Security Notes**:

- This MCP server can execute **any** command on your Minecraft server
- Only use with **trusted AI assistants** and secure environments
- The `stop` command will **shut down your server** - use carefully
- Consider running the Bedrock server in a **containerized environment**
- Monitor server logs for **unexpected commands**

### Recommendations:
1. **Backup your world** before first use
2. **Test in a development environment** first  
3. **Use server permissions** to limit potential damage
4. **Monitor command execution** through logs

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- **WebSocket support** for more advanced Bedrock server communication
- **Plugin integration** for enhanced functionality  
- **Multi-server management** capabilities
- **Advanced player statistics** and monitoring
- **Automated backup systems**

### Development Setup
```bash
git clone <repository>
cd minecraft-bedrock-mcp
pip install -e .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Model Context Protocol** team for the excellent MCP framework
- **Minecraft Bedrock Edition** community for server documentation
- Inspired by Java Edition MCP servers like [rcon-mcp](https://github.com/rgbkrk/rcon-mcp)

## 📞 Support

Having issues? Check these resources:

1. **[Troubleshooting Section](#-troubleshooting)** above
2. **[MCP Documentation](https://modelcontextprotocol.io/)**
3. **[Minecraft Bedrock Server Documentation](https://minecraft.wiki/w/Bedrock_Dedicated_Server)**
4. **GitHub Issues** (if this were a real repository)

---

**Happy Mining with AI! ⛏️🤖**