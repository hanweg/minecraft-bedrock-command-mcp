#!/usr/bin/env python3
"""
Minecraft Bedrock Edition MCP Server

This server provides tools to interact with a Minecraft Bedrock Dedicated Server
through stdin commands and log parsing.

Usage:
    python bedrock_mcp_server.py --server-path /path/to/bedrock_server

Requirements:
    - Minecraft Bedrock Dedicated Server installed and configured
    - Server must be running or this script can start it
"""

import asyncio
import json
import logging
import re
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bedrock-mcp")

class BedrockServerManager:
    """Manages communication with Minecraft Bedrock Dedicated Server"""
    
    def __init__(self, server_path: str):
        self.server_path = Path(server_path)
        self.server_executable = self.server_path / "bedrock_server.exe" if self.server_path.suffix == ".exe" else self.server_path / "bedrock_server"
        self.process: Optional[subprocess.Popen] = None
        self.log_buffer: List[str] = []
        self.players_online: List[str] = []
        self.server_running = False
        
    async def start_server(self) -> bool:
        """Start the Bedrock server if not already running"""
        if self.server_running:
            return True
            
        try:
            # Change to server directory
            cwd = self.server_path if self.server_path.is_dir() else self.server_path.parent
            
            executable = self.server_executable
            if not executable.exists():
                # Try different common names
                for name in ["bedrock_server", "bedrock_server.exe", "BedrockServer.exe"]:
                    test_path = cwd / name
                    if test_path.exists():
                        executable = test_path
                        break
                        
            if not executable.exists():
                logger.error(f"Bedrock server executable not found in {cwd}")
                return False
                
            # Start the server process
            self.process = subprocess.Popen(
                [str(executable)],
                cwd=str(cwd),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Start log monitoring thread
            threading.Thread(target=self._monitor_logs, daemon=True).start()
            
            self.server_running = True
            logger.info("Bedrock server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def _monitor_logs(self):
        """Monitor server logs in a separate thread"""
        if not self.process:
            return
            
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    line = line.strip()
                    self.log_buffer.append(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")
                    
                    # Keep only last 100 log lines
                    if len(self.log_buffer) > 100:
                        self.log_buffer.pop(0)
                    
                    # Parse for player events
                    self._parse_log_line(line)
                    
        except Exception as e:
            logger.error(f"Error monitoring logs: {e}")
    
    def _parse_log_line(self, line: str):
        """Parse log lines for useful information"""
        # Player join pattern
        join_pattern = r"Player connected: (.+?),"
        join_match = re.search(join_pattern, line)
        if join_match:
            player = join_match.group(1)
            if player not in self.players_online:
                self.players_online.append(player)
                
        # Player leave pattern  
        leave_pattern = r"Player disconnected: (.+?),"
        leave_match = re.search(leave_pattern, line)
        if leave_match:
            player = leave_match.group(1)
            if player in self.players_online:
                self.players_online.remove(player)
    
    async def send_command(self, command: str) -> str:
        """Send a command to the server"""
        if not self.process or not self.server_running:
            return "Error: Server is not running"
            
        try:
            # Send command to server stdin
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()
            
            # Wait a bit for the command to process
            await asyncio.sleep(0.5)
            
            # Return recent logs that might contain the response
            recent_logs = self.log_buffer[-10:] if self.log_buffer else ["No recent activity"]
            return "\n".join(recent_logs)
            
        except Exception as e:
            return f"Error sending command: {e}"
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get current server status"""
        return {
            "running": self.server_running,
            "players_online": len(self.players_online),
            "player_list": self.players_online,
            "process_id": self.process.pid if self.process else None
        }
    
    def get_recent_logs(self, lines: int = 20) -> List[str]:
        """Get recent server logs"""
        return self.log_buffer[-lines:] if self.log_buffer else ["No logs available"]
    
    async def stop_server(self):
        """Stop the server gracefully"""
        if self.process:
            await self.send_command("stop")
            await asyncio.sleep(2)
            
            if self.process.poll() is None:
                self.process.terminate()
                
            self.server_running = False

# Initialize the MCP server
server = Server("minecraft-bedrock")
bedrock_manager: Optional[BedrockServerManager] = None

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available Minecraft Bedrock tools"""
    logger.info("LIST_TOOLS called - returning Minecraft tools")
    
    tools = [
        types.Tool(
            name="send-command",
            description="Send a command to the Minecraft Bedrock server",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The Minecraft command to send (without leading slash)"
                    }
                },
                "required": ["command"]
            }
        ),
        types.Tool(
            name="get-server-status",
            description="Get the current status of the Minecraft server",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="list-players",
            description="List players currently online",
            inputSchema={
                "type": "object", 
                "properties": {}
            }
        ),
        types.Tool(
            name="get-server-logs",
            description="Get recent server logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "lines": {
                        "type": "number",
                        "description": "Number of recent log lines to retrieve"
                    }
                }
            }
        ),
        types.Tool(
            name="teleport-player",
            description="Teleport a player to specific coordinates",
            inputSchema={
                "type": "object",
                "properties": {
                    "player": {
                        "type": "string",
                        "description": "Player name to teleport"
                    },
                    "x": {"type": "number", "description": "X coordinate"},
                    "y": {"type": "number", "description": "Y coordinate"}, 
                    "z": {"type": "number", "description": "Z coordinate"}
                },
                "required": ["player", "x", "y", "z"]
            }
        ),
        types.Tool(
            name="give-item",
            description="Give an item to a player",
            inputSchema={
                "type": "object",
                "properties": {
                    "player": {
                        "type": "string",
                        "description": "Player name to give item to"
                    },
                    "item": {
                        "type": "string", 
                        "description": "Item ID (e.g., 'diamond_sword', 'stone', 'apple')"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount of items to give"
                    }
                },
                "required": ["player", "item"]
            }
        ),
        types.Tool(
            name="set-time",
            description="Set the time of day in the world",
            inputSchema={
                "type": "object",
                "properties": {
                    "time": {
                        "type": "string",
                        "description": "Time to set ('day', 'night', 'noon', 'midnight', or tick value)"
                    }
                },
                "required": ["time"]
            }
        ),
        types.Tool(
            name="set-weather",
            description="Change the weather in the world",
            inputSchema={
                "type": "object",
                "properties": {
                    "weather": {
                        "type": "string",
                        "description": "Weather type ('clear', 'rain', 'thunder')"
                    },
                    "duration": {
                        "type": "number",
                        "description": "Duration in seconds (optional)"
                    }
                },
                "required": ["weather"]
            }
        ),
        types.Tool(
            name="setblock",
            description="Place a single block at specific coordinates",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {"type": "number", "description": "X coordinate"},
                    "y": {"type": "number", "description": "Y coordinate"},
                    "z": {"type": "number", "description": "Z coordinate"},
                    "block": {
                        "type": "string",
                        "description": "Block type (e.g., 'stone', 'oak_planks', 'glass', 'dirt')"
                    }
                },
                "required": ["x", "y", "z", "block"]
            }
        ),
        types.Tool(
            name="fill",
            description="Fill a rectangular area with blocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "x1": {"type": "number", "description": "First corner X coordinate"},
                    "y1": {"type": "number", "description": "First corner Y coordinate"},
                    "z1": {"type": "number", "description": "First corner Z coordinate"},
                    "x2": {"type": "number", "description": "Second corner X coordinate"},
                    "y2": {"type": "number", "description": "Second corner Y coordinate"},
                    "z2": {"type": "number", "description": "Second corner Z coordinate"},
                    "block": {
                        "type": "string",
                        "description": "Block type to fill with (e.g., 'stone', 'air', 'water')"
                    },
                    "fill_mode": {
                        "type": "string",
                        "description": "Fill mode ('replace', 'destroy', 'keep', 'outline', 'hollow')"
                    }
                },
                "required": ["x1", "y1", "z1", "x2", "y2", "z2", "block"]
            }
        ),
        types.Tool(
            name="clone",
            description="Copy blocks from one area to another",
            inputSchema={
                "type": "object",
                "properties": {
                    "x1": {"type": "number", "description": "Source area first corner X"},
                    "y1": {"type": "number", "description": "Source area first corner Y"},
                    "z1": {"type": "number", "description": "Source area first corner Z"},
                    "x2": {"type": "number", "description": "Source area second corner X"},
                    "y2": {"type": "number", "description": "Source area second corner Y"},
                    "z2": {"type": "number", "description": "Source area second corner Z"},
                    "dest_x": {"type": "number", "description": "Destination X coordinate"},
                    "dest_y": {"type": "number", "description": "Destination Y coordinate"},
                    "dest_z": {"type": "number", "description": "Destination Z coordinate"}
                },
                "required": ["x1", "y1", "z1", "x2", "y2", "z2", "dest_x", "dest_y", "dest_z"]
            }
        ),
        types.Tool(
            name="structure-save",
            description="Save a structure template from the world",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the structure template"
                    },
                    "x1": {"type": "number", "description": "First corner X coordinate"},
                    "y1": {"type": "number", "description": "First corner Y coordinate"},
                    "z1": {"type": "number", "description": "First corner Z coordinate"},
                    "x2": {"type": "number", "description": "Second corner X coordinate"},
                    "y2": {"type": "number", "description": "Second corner Y coordinate"},
                    "z2": {"type": "number", "description": "Second corner Z coordinate"}
                },
                "required": ["name", "x1", "y1", "z1", "x2", "y2", "z2"]
            }
        ),
        types.Tool(
            name="structure-load",
            description="Load and place a saved structure template",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the structure template to load"
                    },
                    "x": {"type": "number", "description": "X coordinate to place structure"},
                    "y": {"type": "number", "description": "Y coordinate to place structure"},
                    "z": {"type": "number", "description": "Z coordinate to place structure"}
                },
                "required": ["name", "x", "y", "z"]
            }
        ),
        types.Tool(
            name="summon",
            description="Spawn entities (mobs, items, etc.) at specific coordinates",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity": {
                        "type": "string",
                        "description": "Entity type (e.g., 'cow', 'zombie', 'armor_stand', 'item')"
                    },
                    "x": {"type": "number", "description": "X coordinate"},
                    "y": {"type": "number", "description": "Y coordinate"},
                    "z": {"type": "number", "description": "Z coordinate"}
                },
                "required": ["entity", "x", "y", "z"]
            }
        ),
        types.Tool(
            name="particle",
            description="Create particle effects at specific locations",
            inputSchema={
                "type": "object",
                "properties": {
                    "particle_type": {
                        "type": "string",
                        "description": "Particle type (e.g., 'flame', 'smoke', 'heart', 'explosion')"
                    },
                    "x": {"type": "number", "description": "X coordinate"},
                    "y": {"type": "number", "description": "Y coordinate"},
                    "z": {"type": "number", "description": "Z coordinate"}
                },
                "required": ["particle_type", "x", "y", "z"]
            }
        ),
        types.Tool(
            name="create-simple-building",
            description="Create common building structures like houses, towers, or walls",
            inputSchema={
                "type": "object",
                "properties": {
                    "structure_type": {
                        "type": "string",
                        "description": "Type of structure ('house', 'tower', 'wall', 'platform', 'pyramid')"
                    },
                    "x": {"type": "number", "description": "Center/start X coordinate"},
                    "y": {"type": "number", "description": "Base Y coordinate"},
                    "z": {"type": "number", "description": "Center/start Z coordinate"},
                    "size": {
                        "type": "number",
                        "description": "Size parameter (width/height depending on structure)"
                    },
                    "material": {
                        "type": "string",
                        "description": "Primary building material (e.g., 'stone', 'oak_planks', 'cobblestone')"
                    }
                },
                "required": ["structure_type", "x", "y", "z", "size"]
            }
        )
    ]
    
    logger.info(f"Returning {len(tools)} tools to client")
    for tool in tools:
        logger.info(f"Tool: {tool.name}")
    
    return tools

@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List available resources (empty for this server)"""
    logger.info("LIST_RESOURCES called")
    return []

@server.list_prompts()
async def handle_list_prompts() -> List[types.Prompt]:
    """List available prompts (empty for this server)"""
    logger.info("LIST_PROMPTS called")
    return []

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any] | None
) -> List[types.TextContent]:
    """Handle tool calls for Minecraft Bedrock server"""
    
    logger.info(f"CALL_TOOL called: {name} with {arguments}")
    
    if not bedrock_manager:
        return [types.TextContent(
            type="text",
            text="Error: Bedrock server manager not initialized"
        )]
    
    if not arguments:
        arguments = {}
    
    try:
        if name == "send-command":
            command = arguments.get("command", "")
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Command sent: {command}\n\nServer response:\n{result}"
            )]
        
        elif name == "get-server-status":
            status = bedrock_manager.get_server_status()
            status_text = f"""Server Status:
- Running: {status['running']}
- Players Online: {status['players_online']}
- Process ID: {status['process_id']}

Players: {', '.join(status['player_list']) if status['player_list'] else 'None'}"""
            
            return [types.TextContent(type="text", text=status_text)]
        
        elif name == "list-players":
            status = bedrock_manager.get_server_status()
            players = status['player_list']
            if players:
                player_text = f"Players online ({len(players)}):\n" + "\n".join(f"- {player}" for player in players)
            else:
                player_text = "No players currently online"
                
            return [types.TextContent(type="text", text=player_text)]
        
        elif name == "get-server-logs":
            lines = arguments.get("lines", 20)
            logs = bedrock_manager.get_recent_logs(lines)
            log_text = f"Recent server logs ({len(logs)} lines):\n\n" + "\n".join(logs)
            return [types.TextContent(type="text", text=log_text)]
        
        elif name == "teleport-player":
            player = arguments["player"]
            x, y, z = arguments["x"], arguments["y"], arguments["z"]
            command = f"tp {player} {x} {y} {z}"
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Teleported {player} to ({x}, {y}, {z})\n\nServer response:\n{result}"
            )]
        
        elif name == "give-item":
            player = arguments["player"]
            item = arguments["item"] 
            amount = arguments.get("amount", 1)
            command = f"give {player} {item} {amount}"
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Gave {amount} {item} to {player}\n\nServer response:\n{result}"
            )]
        
        elif name == "set-time":
            time_value = arguments["time"]
            command = f"time set {time_value}"
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text", 
                text=f"Set time to {time_value}\n\nServer response:\n{result}"
            )]
        
        elif name == "set-weather":
            weather = arguments["weather"]
            duration = arguments.get("duration")
            
            if duration:
                command = f"weather {weather} {duration}"
            else:
                command = f"weather {weather}"
                
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Set weather to {weather}\n\nServer response:\n{result}"
            )]
        
        elif name == "setblock":
            x, y, z = arguments["x"], arguments["y"], arguments["z"]
            block = arguments["block"]
            
            command = f"setblock {x} {y} {z} {block}"
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Placed {block} at ({x}, {y}, {z})\n\nServer response:\n{result}"
            )]
        
        elif name == "fill":
            x1, y1, z1 = arguments["x1"], arguments["y1"], arguments["z1"]
            x2, y2, z2 = arguments["x2"], arguments["y2"], arguments["z2"]
            block = arguments["block"]
            fill_mode = arguments.get("fill_mode", "replace")
            
            command = f"fill {x1} {y1} {z1} {x2} {y2} {z2} {block} {fill_mode}"
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Filled area from ({x1},{y1},{z1}) to ({x2},{y2},{z2}) with {block}\n\nServer response:\n{result}"
            )]
        
        elif name == "clone":
            x1, y1, z1 = arguments["x1"], arguments["y1"], arguments["z1"]
            x2, y2, z2 = arguments["x2"], arguments["y2"], arguments["z2"]
            dest_x, dest_y, dest_z = arguments["dest_x"], arguments["dest_y"], arguments["dest_z"]
            
            command = f"clone {x1} {y1} {z1} {x2} {y2} {z2} {dest_x} {dest_y} {dest_z}"
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Cloned area from ({x1},{y1},{z1})-({x2},{y2},{z2}) to ({dest_x},{dest_y},{dest_z})\n\nServer response:\n{result}"
            )]
        
        elif name == "structure-save":
            name_arg = arguments["name"]
            x1, y1, z1 = arguments["x1"], arguments["y1"], arguments["z1"]
            x2, y2, z2 = arguments["x2"], arguments["y2"], arguments["z2"]
            
            command = f"structure save {name_arg} {x1} {y1} {z1} {x2} {y2} {z2}"
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Saved structure '{name_arg}' from ({x1},{y1},{z1}) to ({x2},{y2},{z2})\n\nServer response:\n{result}"
            )]
        
        elif name == "structure-load":
            name_arg = arguments["name"]
            x, y, z = arguments["x"], arguments["y"], arguments["z"]
            
            command = f"structure load {name_arg} {x} {y} {z}"
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Loaded structure '{name_arg}' at ({x}, {y}, {z})\n\nServer response:\n{result}"
            )]
        
        elif name == "summon":
            entity = arguments["entity"]
            x, y, z = arguments["x"], arguments["y"], arguments["z"]
            
            command = f"summon {entity} {x} {y} {z}"
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Summoned {entity} at ({x}, {y}, {z})\n\nServer response:\n{result}"
            )]
        
        elif name == "particle":
            particle_type = arguments["particle_type"]
            x, y, z = arguments["x"], arguments["y"], arguments["z"]
            
            command = f"particle {particle_type} {x} {y} {z}"
            result = await bedrock_manager.send_command(command)
            return [types.TextContent(
                type="text",
                text=f"Created {particle_type} particles at ({x}, {y}, {z})\n\nServer response:\n{result}"
            )]
        
        elif name == "create-simple-building":
            structure_type = arguments["structure_type"]
            x, y, z = arguments["x"], arguments["y"], arguments["z"]
            size = arguments["size"]
            material = arguments.get("material", "stone")
            
            # Build different structures using multiple fill commands
            commands = []
            
            if structure_type == "house":
                # Simple house: floor, walls, roof
                commands = [
                    f"fill {x-size} {y} {z-size} {x+size} {y} {z+size} {material}",  # Floor
                    f"fill {x-size} {y+1} {z-size} {x+size} {y+5} {z+size} {material} hollow",  # Walls
                    f"setblock {x} {y+1} {z-size} air",  # Door
                    f"fill {x-size} {y+6} {z-size} {x+size} {y+6} {z+size} {material}"  # Roof
                ]
            elif structure_type == "tower":
                # Tower
                commands = [
                    f"fill {x-size} {y} {z-size} {x+size} {y+20} {z+size} {material} hollow"
                ]
            elif structure_type == "wall":
                # Simple wall
                commands = [
                    f"fill {x} {y} {z-size} {x} {y+5} {z+size} {material}"
                ]
            elif structure_type == "platform":
                # Flat platform
                commands = [
                    f"fill {x-size} {y} {z-size} {x+size} {y} {z+size} {material}"
                ]
            elif structure_type == "pyramid":
                # Step pyramid
                for i in range(size):
                    current_size = size - i
                    if current_size > 0:
                        commands.append(
                            f"fill {x-current_size} {y+i} {z-current_size} {x+current_size} {y+i} {z+current_size} {material}"
                        )
            
            # Execute all commands
            results = []
            for cmd in commands:
                result = await bedrock_manager.send_command(cmd)
                results.append(result)
                await asyncio.sleep(0.1)  # Small delay between commands
            
            return [types.TextContent(
                type="text",
                text=f"Built {structure_type} at ({x}, {y}, {z}) with size {size} using {material}\n\nExecuted {len(commands)} commands\n\nFinal result:\n{results[-1] if results else 'No commands executed'}"
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Error executing {name}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

async def main():
    """Main function to run the MCP server"""
    global bedrock_manager
    
    parser = argparse.ArgumentParser(description="Minecraft Bedrock MCP Server")
    parser.add_argument(
        "--server-path",
        required=True,
        help="Path to Bedrock server directory or executable"
    )
    parser.add_argument(
        "--auto-start",
        action="store_true",
        help="Automatically start the Bedrock server if not running"
    )
    
    args = parser.parse_args()
    
    # Initialize Bedrock server manager
    bedrock_manager = BedrockServerManager(args.server_path)
    
    if args.auto_start:
        logger.info("Starting Bedrock server...")
        if not await bedrock_manager.start_server():
            logger.error("Failed to start Bedrock server")
            return
    
    # Run the MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="minecraft-bedrock",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())

def cli_main():
    """Entry point for console script"""
    asyncio.run(main())