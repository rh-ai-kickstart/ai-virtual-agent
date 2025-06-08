from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any

from .. import models
from ..database import get_db
from ..api.llamastack import client

router = APIRouter(prefix="/tools", tags=["tools"])

@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_tool_groups(db: AsyncSession = Depends(get_db)):
    """Get all tool groups from both MCP servers and builtin tools from LlamaStack"""
    tool_groups = {}
    
    # Get builtin tools from LlamaStack
    try:
        response = client.tools.list()
        if isinstance(response, list):
            llamastack_tools = [item.__dict__ for item in response]
        elif isinstance(response, dict):
            llamastack_tools = response.get("data", [])
        elif hasattr(response, "data"):
            llamastack_tools = response.data
        else:
            llamastack_tools = []
        
        # Filter for builtin tools (not MCP)
        # builtin_tools = [tool for tool in llamastack_tools if tool.get("provider_id") != "model-context-protocol"]
        
        # Group builtin tools by toolgroup_id
        for tool in llamastack_tools:
            toolgroup_id = tool.get("toolgroup_id", tool.get("identifier"))
            if toolgroup_id and toolgroup_id not in tool_groups:
                tool_groups[toolgroup_id] = {
                    "toolgroup_id": toolgroup_id,
                    "name": toolgroup_id,  # Use toolgroup_id as the display name for simplicity
                    "description": tool.get("description", f"Tools for {toolgroup_id}"),
                    "endpoint_url": None,
                    "configuration": tool.get("metadata", {}),
                    "created_at": None,
                    "updated_at": None
                }
    except Exception as e:
        print(f"Warning: Failed to fetch builtin tools from LlamaStack: {str(e)}")
    
    return list(tool_groups.values())
