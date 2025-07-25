"""init

Revision ID: 8d733567d021
Revises:
Create Date: 2025-05-27 17:59:03.018913

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8d733567d021"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "model_servers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("provider_name", sa.String(length=255), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("endpoint_url", sa.String(length=255), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role", sa.Enum("admin", "devops", "user", name="role"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "guardrails",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("rules", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "knowledge_bases",
        sa.Column("vector_db_name", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("embedding_model", sa.String(length=255), nullable=False),
        sa.Column("provider_id", sa.String(length=255), nullable=True),
        sa.Column("is_external", sa.Boolean(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("source_configuration", sa.JSON(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("vector_db_name"),
    )
    op.create_table(
        "mcp_servers",
        sa.Column("toolgroup_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("endpoint_url", sa.String(length=255), nullable=False),
        sa.Column("configuration", sa.JSON(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("toolgroup_id"),
    )
    op.create_table(
        "virtual_assistants",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chat_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("virtual_assistant_id", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["virtual_assistant_id"],
            ["virtual_assistants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "virtual_assistant_knowledge_bases",
        sa.Column("virtual_assistant_id", sa.UUID(), nullable=False),
        sa.Column("vector_db_name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["vector_db_name"],
            ["knowledge_bases.vector_db_name"],
        ),
        sa.ForeignKeyConstraint(
            ["virtual_assistant_id"], ["virtual_assistants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("virtual_assistant_id", "vector_db_name"),
    )
    op.create_table(
        "virtual_assistant_tools",
        sa.Column("virtual_assistant_id", sa.UUID(), nullable=False),
        sa.Column(
            "tool_type",
            sa.Enum(
                "BUILTIN", "MCP_SERVER", name="tool_type_enum", create_constraint=True
            ),
            nullable=False,
        ),
        sa.Column("toolgroup_id", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["virtual_assistant_id"], ["virtual_assistants.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("virtual_assistant_id", "tool_type", "toolgroup_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("virtual_assistant_tools")
    op.drop_table("virtual_assistant_knowledge_bases")
    op.drop_table("chat_history")
    op.drop_table("virtual_assistants")
    op.drop_table("mcp_servers")
    op.drop_table("knowledge_bases")
    op.drop_table("guardrails")
    op.drop_table("users")
    op.drop_table("model_servers")
    # ### end Alembic commands ###
