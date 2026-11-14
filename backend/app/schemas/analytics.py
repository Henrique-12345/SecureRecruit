from pydantic import BaseModel, Field


class SeedLoadRequest(BaseModel):
    crypto_events: int = Field(default=1000, ge=0, le=20000)
    auth_failures: int = Field(default=200, ge=0, le=10000)
    attack_events: int = Field(default=50, ge=0, le=2000)
    hours_span: int = Field(default=48, ge=1, le=720)


class SeedLoadResponse(BaseModel):
    crypto_operations: int
    auth_failures: int
    attack_experiments: int
    total: int
