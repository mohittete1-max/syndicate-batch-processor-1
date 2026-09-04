import sys
import os

# Patch standard streams if they lack valid file descriptors (common in IDE runners)
try:
    sys.stderr.fileno()
except Exception:
    sys.stderr = open(os.devnull, 'w')

try:
    sys.stdout.fileno()
except Exception:
    sys.stdout = open(os.devnull, 'w')

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    server_params = StdioServerParameters(
        command=r"C:\Users\User\AppData\Local\Python\pythoncore-3.14-64\python.exe",
        args=[r"C:\Users\User\OneDrive\Desktop\Cricket\syndicate_mcp_server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools = await session.list_tools()
            print("Registered Tools:", [t.name for t in tools.tools])
            
            weather_res = await session.call_tool("fetch_venue_weather", {"city_name": "Dubai"})
            print("\n[Weather Tool Output]:")
            print(weather_res.content[0].text)
            
            opt_res = await session.call_tool("run_syndicate_optimization", {"match_name": "IND-W vs HK-W"})
            print("\n[Optimization Tool Output]:")
            print(opt_res.content[0].text)

if __name__ == "__main__":
    asyncio.run(run_client())
