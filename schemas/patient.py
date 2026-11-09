from datetime import date

from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator


class PatientCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    phone: str = Field(min_length=1, max_length=20)
    email: EmailStr | None = None
    birth_date: date | None = None

    @field_validator("birth_date")
    @classmethod
    def check_birth_date(cls, value):
        if value is not None and value > date.today():
            raise ValueError("birth_date cannot be in the future")
        return value


class PatientReplace(PatientCreate):
    model_config = ConfigDict(extra="forbid")


class PatientUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, min_length=3, max_length=100)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    email: EmailStr | None = None
    birth_date: date | None = None

    @field_validator("birth_date")
    @classmethod
    def check_birth_date(cls, value):
        if value is not None and value > date.today():
            raise ValueError("birth_date cannot be in the future")
        return value


class PatientResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: EmailStr | None = None
    birth_date: date | None = None
