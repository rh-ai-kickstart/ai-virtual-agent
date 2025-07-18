"""
User service for agent management operations.

This service handles user-specific agent operations including:
- Agent assignment management
- Duplicate detection and prevention
"""

import logging
from typing import List

from fastapi import HTTPException

from ..api.llamastack import client

log = logging.getLogger(__name__)


class UserService:
    """Service for user-related agent operations"""

    @staticmethod
    async def get_unique_agents_ids(
        user_agent_ids: List[str], new_agent_ids: List[str]
    ) -> List[str]:
        """
        Check for duplicate agent IDs and return only new unique ones.

        Args:
            user_agent_ids: List of agent IDs currently assigned to the user
            new_agent_ids: List of new agent IDs to check for duplicates

        Returns:
            List of agent IDs that are not already assigned to the user
        """
        unique_agent_ids = []
        for agent_id in new_agent_ids:
            if agent_id not in user_agent_ids:
                unique_agent_ids.append(agent_id)
            else:
                log.info(f"Agent {agent_id} already assigned to user, skipping")

        return unique_agent_ids

    @staticmethod
    async def assign_agents_to_user(
        user_agent_ids: List[str], requested_agent_ids: List[str]
    ) -> List[str]:
        """
        Add requested agents to user's agent list, preventing duplicates.

        Args:
            user_agent_ids: List of agent IDs currently assigned to the user
            requested_agent_ids: List of agent IDs to assign to the user

        Returns:
            List of all agent IDs assigned to the user (existing + new unique ones)

        Raises:
            HTTPException: If any agent doesn't exist in LlamaStack
        """
        # Verify all requested agents exist in LlamaStack
        for agent_id in requested_agent_ids:
            try:
                client.agents.retrieve(agent_id=agent_id)  # type: ignore
                log.info(f"Verified agent exists: {agent_id}")
            except Exception as e:
                log.error(f"Agent {agent_id} not found in LlamaStack: {str(e)}")
                raise HTTPException(
                    status_code=404, detail=f"Agent {agent_id} not found"
                )

        # Check for duplicates and get only new unique agent IDs
        new_agent_ids = await UserService.get_unique_agents_ids(
            user_agent_ids, requested_agent_ids
        )

        # Combine existing and new agent IDs
        all_agent_ids = user_agent_ids + new_agent_ids

        log.info(f"Added {len(new_agent_ids)} new agents to user")
        return all_agent_ids

    @staticmethod
    async def remove_agents_from_user(
        current_agent_ids: List[str], agents_to_remove: List[str]
    ) -> List[str]:
        """
        Remove specified agents from user's agent list.

        Args:
            current_agent_ids: List of agent IDs currently assigned to user
            agents_to_remove: List of agent IDs to remove from user

        Returns:
            List of remaining agent IDs after removal
        """
        # Calculate remaining agents
        remaining_agent_ids = [
            agent_id
            for agent_id in current_agent_ids
            if agent_id not in agents_to_remove
        ]

        log.info(f"Removed {len(agents_to_remove)} agents from user")
        return remaining_agent_ids
