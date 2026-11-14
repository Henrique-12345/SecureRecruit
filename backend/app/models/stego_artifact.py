import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StegoArtifact(Base):
    __tablename__ = "stego_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    payload_operation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crypto_operations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    cover_original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    cover_stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    cover_file_path: Mapped[str] = mapped_column(Text, nullable=False)
    stego_stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    stego_file_path: Mapped[str] = mapped_column(Text, nullable=False)
    capacity_bits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payload_bits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User")
    payload_operation = relationship("CryptoOperation", back_populates="stego_artifacts")
