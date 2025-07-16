"""
Agent initialization utility for loading agents from YAML configuration.

This module provides functionality to read agent configurations from YAML files
and initialize them using existing API functions on application startup.
"""

import os
import yaml
from typing import Dict, List, Optional
from pathlib import Path

from ..utils.logging_config import get_logger
from ..routes.knowledge_bases import create_knowledge_base
from ..routes.virtual_assistants import create_virtual_assistant
from .. import schemas

logger = get_logger(__name__)


def load_agent_config(config_path: str = "/etc/agent-config/agent_config.yaml") -> Dict:
    """
    Load agent configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Dictionary containing agent configurations
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"Loaded agent configuration from {config_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Agent config file not found at {config_path}")
        return {"agents": []}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config file {config_path}: {e}")
        raise


def convert_yaml_agent_to_schema(yaml_agent: Dict) -> Dict:
    """
    Convert YAML agent configuration to the format expected by the API schema.
    
    Args:
        yaml_agent: Agent configuration from YAML
        
    Returns:
        Dictionary in the format expected by VirtualAssistantCreate schema
    """
    agent_config = {
        "name": yaml_agent.get("name", "Unnamed Agent"),
        "model_name": yaml_agent.get("model", "llama3.1-8b-instruct"),
        "prompt": yaml_agent.get("description", "You are a helpful assistant."),
        "temperature": 0.1,
        "top_p": 0.95,
        "max_tokens": 4096,
        "repetition_penalty": 1.0,
        "max_infer_iters": 10,
        "input_shields": [],
        "output_shields": [],
        "tools": [],
        "knowledge_base_ids": [],
        "enable_session_persistence": False
    }
    
    # Convert MCP tools to tool format
    mcp_tools = yaml_agent.get("mcp_tools", [])
    logger.debug(f"Processing MCP tools: {mcp_tools}")
    for tool in mcp_tools:
        tool_name = tool.get("name")
        if tool_name:
            if tool_name == "builtin::rag":
                continue
            else:
                agent_config["tools"].append({"toolgroup_id": f"mcp::{tool_name}"})
                logger.debug(f"Added MCP tool: {tool_name}")
    
    # Convert knowledge bases
    knowledge_bases = yaml_agent.get("knowledge_bases", [])
    logger.debug(f"Processing knowledge bases: {knowledge_bases}")
    for kb in knowledge_bases:
        kb_name = kb.get("name")
        if kb_name:
            agent_config["knowledge_base_ids"].append(kb_name)
            logger.debug(f"Added knowledge base ID: {kb_name}")
    
    # Add RAG tool if knowledge bases are specified
    if agent_config["knowledge_base_ids"]:
        agent_config["tools"].append({"toolgroup_id": "builtin::rag"})
        logger.debug(f"Added builtin::rag tool for knowledge bases: {agent_config['knowledge_base_ids']}")
    else:
        logger.debug("No knowledge bases found, not adding builtin::rag tool")
    
    return agent_config


async def create_knowledge_bases_from_config(yaml_agent: Dict, knowledge_base_ids: List[str]) -> None:
    """
    Create knowledge bases from YAML configuration if they don't exist.
    
    Args:
        yaml_agent: The YAML agent configuration
        knowledge_base_ids: List of knowledge base IDs to create
    """
    from ..database import AsyncSessionLocal
    from .. import models
    from sqlalchemy import select
    
    knowledge_bases = yaml_agent.get("knowledge_bases", [])
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.KnowledgeBase))
        existing_kbs = {kb.vector_db_name for kb in result.scalars().all()}
        
        for kb_config in knowledge_bases:
            kb_name = kb_config.get("name")
            if not kb_name or kb_name not in knowledge_base_ids:
                logger.debug(f"Skipping knowledge base config: name='{kb_name}', not in required_ids={knowledge_base_ids}")
                continue
            
            # Validate knowledge base configuration
            files = kb_config.get("files", [])
            if not files:
                logger.warning(f"Knowledge base '{kb_name}' has no files specified, skipping creation")
                continue
            
            if not isinstance(files, list):
                logger.error(f"Knowledge base '{kb_name}' files must be a list, got {type(files)}")
                continue
            
            # Skip if knowledge base already exists
            if kb_name in existing_kbs:
                logger.info(f"Knowledge base '{kb_name}' already exists, skipping creation")
                continue
            
            try:
                # Create knowledge base configuration
                kb_create = schemas.KnowledgeBaseCreate(
                    name=kb_config.get("description", kb_name),
                    version="1.0",
                    embedding_model="all-MiniLM-L6-v2",
                    provider_id="pgvector",
                    vector_db_name=kb_name,
                    is_external=False,
                    source="URL",
                    source_configuration=files
                )
                
                logger.info(f"Creating knowledge base '{kb_name}' with configuration: {kb_create.model_dump()}")
                
                try:
                    await create_knowledge_base(kb_create)
                    logger.info(f"Successfully created knowledge base '{kb_name}' using API function")
                except Exception as api_error:
                    logger.warning(f"Failed to create knowledge base '{kb_name}' via API: {str(api_error)}")
                    logger.info(f"Creating knowledge base '{kb_name}' in database with PENDING status")
                    
                    db_kb = models.KnowledgeBase(**kb_create.model_dump(exclude_unset=True))
                    db_kb.status = "PENDING"
                    db.add(db_kb)
                    await db.commit()
                    await db.refresh(db_kb)
                    
                    logger.info(f"Successfully created knowledge base '{kb_name}' in database with PENDING status")
                
            except Exception as e:
                logger.error(f"Failed to create knowledge base '{kb_name}': {str(e)}")
                continue


async def initialize_agents_from_config(config_path: Optional[str] = None) -> None:
    """
    Initialize agents from YAML configuration file on startup.
    
    Args:
        config_path: Optional path to config file. If None, uses default path.
    """
    if config_path is None:
        config_path = "/etc/agent-config/agent_config.yaml"
    
    try:
        config = load_agent_config(config_path)
        agents = config.get("agents", [])
        
        if not agents:
            logger.info("No agents found in configuration file")
            return
        
        logger.info(f"Found {len(agents)} agents in configuration file")
        
        # Get existing agents to avoid duplicates
        from ..api.llamastack import client
        existing_agents = client.agents.list()
        existing_names = {agent.agent_config.get("name", "") for agent in existing_agents}
        
        for yaml_agent in agents:
            agent_name = yaml_agent.get("name", "Unnamed Agent")
            
            # Skip if agent already exists
            if agent_name in existing_names:
                logger.info(f"Agent '{agent_name}' already exists, skipping initialization")
                continue
            
            try:
                logger.info(f"Processing YAML agent config for '{agent_name}': {yaml_agent}")
                
                agent_config = convert_yaml_agent_to_schema(yaml_agent)
                logger.info(f"Converted agent config for '{agent_name}': {agent_config}")
                
                # Create VirtualAssistantCreate object
                va_create = schemas.VirtualAssistantCreate(**agent_config)
                
                # Check if agent uses RAG tool and has knowledge bases
                has_rag_tool = va_create.tools and any(tool.toolgroup_id == "builtin::rag" for tool in va_create.tools)
                
                logger.info(f"Agent '{agent_name}' - RAG tool: {has_rag_tool}, Knowledge bases: {va_create.knowledge_base_ids}")
                logger.info(f"Agent '{agent_name}' - Tools: {[tool.toolgroup_id for tool in va_create.tools] if va_create.tools else []}")
                
                if has_rag_tool and va_create.knowledge_base_ids:
                    logger.info(f"Creating knowledge bases for agent '{agent_name}': {va_create.knowledge_base_ids}")
                    try:
                        await create_knowledge_bases_from_config(yaml_agent, va_create.knowledge_base_ids)
                        logger.info(f"Successfully created knowledge bases for agent '{agent_name}'")
                    except Exception as kb_error:
                        logger.warning(f"Failed to create knowledge bases for agent '{agent_name}': {str(kb_error)}")
                        logger.warning(f"Agent '{agent_name}' will be created without knowledge bases")
                        
                        va_create.knowledge_base_ids = []
                        if va_create.tools:
                            va_create.tools = [tool for tool in va_create.tools if tool.toolgroup_id != "builtin::rag"]
                elif has_rag_tool and not va_create.knowledge_base_ids:
                    logger.warning(f"Agent '{agent_name}' has RAG tool but no knowledge bases specified")
                elif not has_rag_tool and va_create.knowledge_base_ids:
                    logger.warning(f"Agent '{agent_name}' has knowledge bases but no RAG tool")
                else:
                    logger.info(f"Agent '{agent_name}' - No RAG tool or knowledge bases configured")
                
                response = await create_virtual_assistant(va_create)
                logger.info(f"Successfully initialized agent '{agent_name}' with ID: {response.id}")
                
            except Exception as e:
                logger.error(f"Failed to initialize agent '{agent_name}': {str(e)}")
                continue
        
        logger.info("Agent initialization completed")
        
    except Exception as e:
        logger.error(f"Error during agent initialization: {str(e)}")
        raise 