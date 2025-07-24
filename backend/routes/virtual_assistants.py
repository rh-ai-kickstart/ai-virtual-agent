"""
Virtual Assistants API endpoints for managing AI agents through LlamaStack.

This module provides CRUD operations for virtual assistants (AI agents) that are
managed through the LlamaStack platform. Virtual assistants can be configured with
different models, tools, knowledge bases, and safety shields.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Request, status, Depends
from llama_stack_client.lib.agents.agent import AgentUtils
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas, models
from ..api.llamastack import get_client_from_request
from ..database import get_db
from ..utils.logging_config import get_logger
from ..virtual_agents.agent_model import VirtualAgent

logger = get_logger(__name__)

router = APIRouter(prefix="/virtual_assistants", tags=["virtual_assistants"])


def get_strategy(sampling_strategy, temperature, top_p, top_k):
    """
    Determines the sampling strategy for the LLM based on user selection.
    Args:
        sampling_strategy: 'greedy', 'top-p', or 'top-k'
        temperature: Temperature parameter for sampling
        top_p: Top-p parameter for nucleus sampling
        top_k: Top-k parameter for k sampling
    Returns:
        Dict containing the sampling strategy configuration
    """
    if sampling_strategy == "top-p":
        temp = max(temperature, 0.1)  # Ensure temp doesn't become 0
        return {"type": "top_p", "temperature": temperature, "top_p": top_p}
    elif sampling_strategy == "top-k":
        temp = max(temperature, 0.1)  # Ensure temp doesn't become 0
        return {"type": "top_k", "temperature": temp, "top_k": top_k}
    # Default and 'greedy' case
    return {"type": "greedy"}


def get_standardized_instructions(user_prompt: str, agent_type: str) -> str:
    """
    Creates standardized instructions with consistent response format based on agent type.

    Args:
        user_prompt: The user's custom prompt/instructions
        agent_type: The type of agent ("ReAct" or "Regular")

    Returns:
        Standardized instructions with appropriate response format requirements
    """
    if agent_type == "ReAct":
        # ReAct agents: Always respond with structured JSON containing thought process and answer
        format_instruction = """

Always respond with complete JSON only:
{"thought": "your thinking", "answer": "your answer"}"""
    else:
        # Regular agents: Respond naturally but consistently
        format_instruction = """

Respond naturally and conversationally. Provide clear, helpful answers."""
    
    return user_prompt + format_instruction


@router.post(
    "/",
    response_model=schemas.VirtualAssistantRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_virtual_assistant(
    va: schemas.VirtualAssistantCreate, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Create a new virtual assistant agent in LlamaStack.

    Args:
        va: Virtual assistant configuration including model, tools, and settings

    Returns:
        The created virtual assistant with generated ID

    Raises:
        HTTPException: If creation fails
    """
    client = get_client_from_request(request)
    try:
        sampling_params = {
            "strategy": get_strategy(
                va.sampling_strategy,
                va.temperature,
                va.top_p,
                va.top_k,
            ),
            "max_tokens": va.max_tokens,
            "repetition_penalty": va.repetition_penalty,
        }

        tools = []
        for i, tool_info in enumerate(va.tools or []):
            if tool_info.toolgroup_id == "builtin::rag":
                if len(va.knowledge_base_ids or []) > 0:
                    tool_dict = dict(
                        name="builtin::rag",
                        args={
                            "vector_db_ids": list(va.knowledge_base_ids or []),
                        },
                    )
                    tools.append(tool_dict)
            else:
                tools.append(tool_info.toolgroup_id)

        # Create standardized instructions based on agent type
        standardized_instructions = get_standardized_instructions(va.prompt or "", va.agent_type or "ReAct")
        
        agent_config = AgentUtils.get_agent_config(
            model=va.model_name,
            instructions=standardized_instructions,
            tools=tools,
            sampling_params=sampling_params,
            max_infer_iters=va.max_infer_iters,
            input_shields=va.input_shields,
            output_shields=va.output_shields,
        )
        agent_config["name"] = va.name

        agentic_system_create_response = await client.agents.create(
            agent_config=agent_config,
        )

        # Store agent type in database
        try:
            converted_agent_type = models.AgentTypeEnum(va.agent_type or "ReAct")
            db_agent_type = models.AgentType(
                agent_id=agentic_system_create_response.agent_id,
                agent_type=converted_agent_type
            )
            db.add(db_agent_type)
            await db.commit()
        except Exception as db_error:
            logger.error(f"Error storing agent_type: {str(db_error)}")
            await db.rollback()
            # Continue anyway, don't fail agent creation

        return schemas.VirtualAssistantRead(
            id=agentic_system_create_response.agent_id,
            name=va.name,
            agent_type=va.agent_type,
            input_shields=va.input_shields,
            output_shields=va.output_shields,
            prompt=va.prompt,
            model_name=va.model_name,
            knowledge_base_ids=va.knowledge_base_ids,
            tools=va.tools,
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"ERROR: create_virtual_assistant: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


def to_va_response(agent: VirtualAgent, agent_type: str = "ReAct"):
    """
    Convert a LlamaStack VirtualAgent to API response format.

    Args:
        agent: VirtualAgent object from LlamaStack
        agent_type: Agent type from database lookup

    Returns:
        VirtualAssistantRead schema with formatted data
    """
    tools = []
    kb_ids = []

    for toolgroup in agent.agent_config.get("toolgroups", []):
        if isinstance(toolgroup, dict):
            tool_name = toolgroup.get("name")
            tools.append(schemas.ToolAssociationInfo(toolgroup_id=tool_name))
            if tool_name == "builtin::rag":
                kb_ids = toolgroup.get("args", {}).get("vector_db_ids", [])
                logger.debug("Assigned vector_db_ids:", kb_ids)
        elif isinstance(toolgroup, str):
            tools.append(schemas.ToolAssociationInfo(toolgroup_id=toolgroup))

    id = agent.agent_id
    name = agent.agent_config.get("name", "")
    name = name if name is not None else "Missing Name"
    input_shields = agent.agent_config.get("input_shields", [])
    output_shields = agent.agent_config.get("output_shields", [])
    prompt = agent.agent_config.get("instructions", "")
    model_name = agent.agent_config.get("model", "")
    return schemas.VirtualAssistantRead(
        id=id,
        name=name,
        agent_type=agent_type,
        input_shields=input_shields,
        output_shields=output_shields,
        prompt=prompt,
        model_name=model_name,
        knowledge_base_ids=kb_ids,
        tools=tools,  # Use the 'tools' field with the correct structure
    )


@router.get("/", response_model=List[schemas.VirtualAssistantRead])
async def get_virtual_assistants(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Retrieve all virtual assistants from LlamaStack.

    Returns:
        List of all virtual assistants configured in the system
    """
    # get all virtual assitants or agents from llama stack
    client = get_client_from_request(request)
    agents = await client.agents.list()
    response_list = []
    for agent in agents:
        # Get agent type from database
        agent_type = "ReAct"  # Default
        try:
            from sqlalchemy.future import select
            result = await db.execute(select(models.AgentType).where(models.AgentType.agent_id == agent.agent_id))
            agent_type_record = result.scalar_one_or_none()
            if agent_type_record:
                agent_type = agent_type_record.agent_type.value
        except Exception:
            pass  # Use default
        response_list.append(to_va_response(agent, agent_type))
    return response_list


@router.get("/{va_id}", response_model=schemas.VirtualAssistantRead)
async def read_virtual_assistant(va_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a specific virtual assistant by ID.

    Args:
        va_id: The unique identifier of the virtual assistant

    Returns:
        The virtual assistant configuration and metadata

    Raises:
        HTTPException: If virtual assistant not found
    """
    client = get_client_from_request(request)
    agent = await client.agents.retrieve(agent_id=va_id)
    
    # Get agent type from database
    agent_type = "ReAct"  # Default
    try:
        from sqlalchemy.future import select
        result = await db.execute(select(models.AgentType).where(models.AgentType.agent_id == va_id))
        agent_type_record = result.scalar_one_or_none()
        if agent_type_record:
            agent_type = agent_type_record.agent_type.value
    except Exception:
        pass  # Use default
    
    return to_va_response(agent, agent_type)


# @router.put("/{va_id}", response_model=schemas.VirtualAssistantRead)
# async def update_virtual_assistant(va_id: str):
#     pass


@router.delete("/{va_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_virtual_assistant(va_id: str, request: Request):
    """
    Delete a virtual assistant from LlamaStack.

    Args:
        va_id: The unique identifier of the virtual assistant to delete

    Returns:
        None (204 No Content status)
    """
    client = get_client_from_request(request)
    await client.agents.delete(agent_id=va_id)
    return None
