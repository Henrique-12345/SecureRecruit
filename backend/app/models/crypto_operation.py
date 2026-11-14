import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CryptoOperation(Base):
    __tablename__ = "crypto_operations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    key_material_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crypto_key_materials.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    operation_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    algorithm: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    input_kind: Mapped[str] = mapped_column(String(20), nullable=False, default="text")
    input_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    avalanche_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    user = relationship("User")
    key_material = relationship("CryptoKeyMaterial", back_populates="operations")
    stego_artifacts = relationship("StegoArtifact", back_populates="payload_operation")
