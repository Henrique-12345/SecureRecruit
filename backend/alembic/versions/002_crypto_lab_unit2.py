"""crypto lab unit 2 schema

Revision ID: 002_crypto_lab
Revises: 001_initial
Create Date: 2026-11-14 18:20:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_crypto_lab"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "crypto_key_materials",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("derivation_info", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("algorithm", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crypto_key_materials_owner_id", "crypto_key_materials", ["owner_id"])
    op.create_index(
        "ix_crypto_key_materials_key_fingerprint", "crypto_key_materials", ["key_fingerprint"]
    )

    op.create_table(
        "crypto_operations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("key_material_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("operation_type", sa.String(length=40), nullable=False),
        sa.Column("algorithm", sa.String(length=32), nullable=False),
        sa.Column("input_kind", sa.String(length=20), nullable=False),
        sa.Column("input_size", sa.Integer(), nullable=False),
        sa.Column("output_size", sa.Integer(), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("avalanche_score", sa.Float(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["key_material_id"], ["crypto_key_materials.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crypto_operations_user_id", "crypto_operations", ["user_id"])
    op.create_index(
        "ix_crypto_operations_key_material_id", "crypto_operations", ["key_material_id"]
    )
    op.create_index(
        "ix_crypto_operations_operation_type", "crypto_operations", ["operation_type"]
    )
    op.create_index("ix_crypto_operations_algorithm", "crypto_operations", ["algorithm"])
    op.create_index("ix_crypto_operations_created_at", "crypto_operations", ["created_at"])

    op.create_table(
        "stego_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload_operation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cover_original_filename", sa.String(length=255), nullable=False),
        sa.Column("cover_stored_filename", sa.String(length=255), nullable=False),
        sa.Column("cover_file_path", sa.Text(), nullable=False),
        sa.Column("stego_stored_filename", sa.String(length=255), nullable=False),
        sa.Column("stego_file_path", sa.Text(), nullable=False),
        sa.Column("capacity_bits", sa.Integer(), nullable=False),
        sa.Column("payload_bits", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["payload_operation_id"], ["crypto_operations.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stego_stored_filename"),
    )
    op.create_index("ix_stego_artifacts_user_id", "stego_artifacts", ["user_id"])
    op.create_index(
        "ix_stego_artifacts_payload_operation_id", "stego_artifacts", ["payload_operation_id"]
    )

    op.create_table(
        "attack_experiments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("attack_type", sa.String(length=32), nullable=False),
        sa.Column("algorithm", sa.String(length=32), nullable=False),
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("effectiveness_score", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attack_experiments_user_id", "attack_experiments", ["user_id"])
    op.create_index("ix_attack_experiments_attack_type", "attack_experiments", ["attack_type"])
    op.create_index("ix_attack_experiments_created_at", "attack_experiments", ["created_at"])

    op.create_table(
        "anomaly_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("anomaly_type", sa.String(length=40), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("source_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["source_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_anomaly_events_anomaly_type", "anomaly_events", ["anomaly_type"])
    op.create_index("ix_anomaly_events_severity", "anomaly_events", ["severity"])
    op.create_index("ix_anomaly_events_source_user_id", "anomaly_events", ["source_user_id"])
    op.create_index("ix_anomaly_events_detected_at", "anomaly_events", ["detected_at"])


def downgrade() -> None:
    op.drop_table("anomaly_events")
    op.drop_table("attack_experiments")
    op.drop_table("stego_artifacts")
    op.drop_table("crypto_operations")
    op.drop_table("crypto_key_materials")
