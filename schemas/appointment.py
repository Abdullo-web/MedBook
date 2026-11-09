from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict, field_validator


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    start_at: datetime
    duration_minutes: Literal[15, 30, 45, 60]
    reason: str | None = Field(default=None, max_length=300)

    @field_validator("start_at")
    @classmethod
    def check_start_at(cls, value):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        value = value.astimezone(timezone.utc)
        if value <= datetime.now(timezone.utc):
            raise ValueError("start_at must be in the future")
        return value


class AppointmentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doctor_id: int | None = None
    start_at: datetime | None = None
    duration_minutes: Literal[15, 30, 45, 60] | None = None
    reason: str | None = Field(default=None, max_length=300)

    @field_validator("start_at")
    @classmethod
    def check_start_at(cls, value):
        if value is None:
            return value
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        value = value.astimezone(timezone.utc)
        if value <= datetime.now(timezone.utc):
            raise ValueError("start_at must be in the future")
        return value


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_at: datetime
    duration_minutes: int
    status: Literal["scheduled", "completed", "cancelled"]
    reason: str | None = None
