import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import CryptoAlgorithm


class CryptoKeyMaterial(Base):
    __tablename__ = "crypto_key_materials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    derivation_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    algorithm: Mapped[str] = mapped_column(
        String(32), nullable=False, default=CryptoAlgorithm.CUSTOM_SPN.value
    )
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    owner = relationship("User")
    operations = relationship("CryptoOperation", back_populates="key_material")
