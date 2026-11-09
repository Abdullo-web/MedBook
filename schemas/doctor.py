from pydantic import BaseModel, Field, ConfigDict


class DoctorCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    specialization_id: int
    experience_years: int = Field(ge=0)
    consultation_price: float = Field(gt=0)
    is_active: bool = True


class DoctorReplace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=3, max_length=100)
    specialization_id: int
    experience_years: int = Field(ge=0)
    consultation_price: float = Field(gt=0)
    is_active: bool = True


class DoctorUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, min_length=3, max_length=100)
    specialization_id: int | None = None
    experience_years: int | None = Field(default=None, ge=0)
    consultation_price: float | None = Field(default=None, gt=0)
    is_active: bool | None = None


class DoctorResponse(BaseModel):
    id: int
    full_name: str
    specialization_id: int
    experience_years: int
    consultation_price: float
    is_active: bool
