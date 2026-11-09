from datetime import date, datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException

from data.storage import appointments, doctors, patients, next_id
from schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", response_model=AppointmentResponse, status_code=201)
def create_appointment(data: AppointmentCreate):
    patient_found = False
    for patient in patients:
        if patient["id"] == data.patient_id:
            patient_found = True

    if not patient_found:
        raise HTTPException(status_code=404, detail=f"Patient with id {data.patient_id} not found")

    doctor_found = None
    for doctor in doctors:
        if doctor["id"] == data.doctor_id:
            doctor_found = doctor

    if doctor_found is None:
        raise HTTPException(status_code=404, detail=f"Doctor with id {data.doctor_id} not found")

    if not doctor_found["is_active"]:
        raise HTTPException(status_code=409, detail=f"Doctor with id {data.doctor_id} is not active")

    new_start = data.start_at
    new_end = new_start + timedelta(minutes=data.duration_minutes)

    for appointment in appointments:
        if appointment["doctor_id"] == data.doctor_id and appointment["status"] == "scheduled":
            existing_start = appointment["start_at"]
            existing_end = existing_start + timedelta(minutes=appointment["duration_minutes"])
            if new_start < existing_end and existing_start < new_end:
                raise HTTPException(status_code=409, detail=f"Doctor with id {data.doctor_id} is busy at this time")

    new_id = next_id("appointment")
    new_appointment = data.model_dump()
    new_appointment["id"] = new_id
    new_appointment["status"] = "scheduled"
    appointments.append(new_appointment)
    return new_appointment


@router.get("", response_model=list[AppointmentResponse])
def get_appointments(
    doctor_id: int | None = None,
    patient_id: int | None = None,
    status: Literal["scheduled", "completed", "cancelled"] | None = None,
    date: date | None = None,
):
    result = []
    for appointment in appointments:
        if doctor_id is not None and appointment["doctor_id"] != doctor_id:
            continue
        if patient_id is not None and appointment["patient_id"] != patient_id:
            continue
        if status is not None and appointment["status"] != status:
            continue
        if date is not None and appointment["start_at"].date() != date:
            continue
        result.append(appointment)
    return result


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int):
    for appointment in appointments:
        if appointment["id"] == appointment_id:
            return appointment

    raise HTTPException(status_code=404, detail=f"Appointment with id {appointment_id} not found")


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def patch_appointment(appointment_id: int, data: AppointmentUpdate):
    for appointment in appointments:
        if appointment["id"] == appointment_id:
            if appointment["status"] != "scheduled":
                raise HTTPException(status_code=409, detail=f"Appointment with id {appointment_id} is {appointment['status']} and cannot be changed")

            update_data = data.model_dump(exclude_unset=True)

            doctor_id = update_data.get("doctor_id", appointment["doctor_id"])
            start_at = update_data.get("start_at", appointment["start_at"])
            duration_minutes = update_data.get("duration_minutes", appointment["duration_minutes"])

            if "doctor_id" in update_data:
                doctor_found = None
                for doctor in doctors:
                    if doctor["id"] == doctor_id:
                        doctor_found = doctor

                if doctor_found is None:
                    raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")

                if not doctor_found["is_active"]:
                    raise HTTPException(status_code=409, detail=f"Doctor with id {doctor_id} is not active")

            new_start = start_at
            new_end = new_start + timedelta(minutes=duration_minutes)

            for other in appointments:
                if other["id"] != appointment_id and other["doctor_id"] == doctor_id and other["status"] == "scheduled":
                    existing_start = other["start_at"]
                    existing_end = existing_start + timedelta(minutes=other["duration_minutes"])
                    if new_start < existing_end and existing_start < new_end:
                        raise HTTPException(status_code=409, detail=f"Doctor with id {doctor_id} is busy at this time")

            appointment.update(update_data)
            return appointment

    raise HTTPException(status_code=404, detail=f"Appointment with id {appointment_id} not found")


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(appointment_id: int):
    for appointment in appointments:
        if appointment["id"] == appointment_id:
            if appointment["status"] != "scheduled":
                raise HTTPException(status_code=409, detail=f"Appointment with id {appointment_id} is {appointment['status']} and cannot be cancelled")

            appointment["status"] = "cancelled"
            return appointment

    raise HTTPException(status_code=404, detail=f"Appointment with id {appointment_id} not found")


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(appointment_id: int):
    for appointment in appointments:
        if appointment["id"] == appointment_id:
            if appointment["status"] != "scheduled":
                raise HTTPException(status_code=409, detail=f"Appointment with id {appointment_id} is {appointment['status']} and cannot be completed")

            end_at = appointment["start_at"] + timedelta(minutes=appointment["duration_minutes"])
            if end_at > datetime.now(timezone.utc):
                raise HTTPException(status_code=409, detail=f"Appointment with id {appointment_id} has not ended yet")

            appointment["status"] = "completed"
            return appointment

    raise HTTPException(status_code=404, detail=f"Appointment with id {appointment_id} not found")
