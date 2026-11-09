from fastapi import APIRouter, HTTPException

from data.storage import patients, appointments, next_id
from schemas.patient import PatientCreate, PatientReplace, PatientUpdate, PatientResponse
from schemas.appointment import AppointmentResponse

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(data: PatientCreate):
    new_id = next_id("patient")
    new_patient = data.model_dump()
    new_patient["id"] = new_id
    patients.append(new_patient)
    return new_patient


@router.get("", response_model=list[PatientResponse])
def get_patients(search: str | None = None):
    result = []
    for patient in patients:
        if search is not None and search.lower() not in patient["full_name"].lower():
            continue
        result.append(patient)
    return result


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int):
    for patient in patients:
        if patient["id"] == patient_id:
            return patient

    raise HTTPException(status_code=404, detail=f"Patient with id {patient_id} not found")


@router.put("/{patient_id}", response_model=PatientResponse)
def put_patient(patient_id: int, data: PatientReplace):
    for patient in patients:
        if patient["id"] == patient_id:
            patient.update(data.model_dump())
            return patient

    raise HTTPException(status_code=404, detail=f"Patient with id {patient_id} not found")


@router.patch("/{patient_id}", response_model=PatientResponse)
def patch_patient(patient_id: int, data: PatientUpdate):
    for patient in patients:
        if patient["id"] == patient_id:
            update_data = data.model_dump(exclude_unset=True)
            patient.update(update_data)
            return patient

    raise HTTPException(status_code=404, detail=f"Patient with id {patient_id} not found")


@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int):
    for patient in patients:
        if patient["id"] == patient_id:
            for appointment in appointments:
                if appointment["patient_id"] == patient_id:
                    raise HTTPException(status_code=409, detail=f"Patient with id {patient_id} has appointments and cannot be deleted")
            patients.remove(patient)
            return

    raise HTTPException(status_code=404, detail=f"Patient with id {patient_id} not found")


@router.get("/{patient_id}/appointments", response_model=list[AppointmentResponse])
def get_patient_appointments(patient_id: int):
    for patient in patients:
        if patient["id"] == patient_id:
            result = []
            for appointment in appointments:
                if appointment["patient_id"] == patient_id:
                    result.append(appointment)
            return result

    raise HTTPException(status_code=404, detail=f"Patient with id {patient_id} not found")
