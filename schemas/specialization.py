from pydantic import BaseModel, Field, ConfigDict


class SpecializationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=300)


class SpecializationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=300)


class SpecializationResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
