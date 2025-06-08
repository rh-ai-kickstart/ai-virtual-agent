from fastapi import FastAPI
from mcp import MCPServer
from tools.flight_search import FlightSearchTool

app = FastAPI()
server = MCPServer(app)

server.register_tool(FlightSearchTool())