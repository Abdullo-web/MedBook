from fastapi import APIRouter, HTTPException

from data.storage import doctors, specializations, appointments, next_id
from schemas.doctor import DoctorCreate, DoctorReplace, DoctorUpdate, DoctorResponse
from schemas.appointment import AppointmentResponse

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("", response_model=DoctorResponse, status_code=201)
def create_doctor(data: DoctorCreate):
    specialization_found = False
    for specialization in specializations:
        if specialization["id"] == data.specialization_id:
            specialization_found = True

    if not specialization_found:
        raise HTTPException(status_code=404, detail=f"Specialization with id {data.specialization_id} not found")

    new_id = next_id("doctor")
    new_doctor = data.model_dump()
    new_doctor["id"] = new_id
    doctors.append(new_doctor)
    return new_doctor


@router.get("", response_model=list[DoctorResponse])
def get_doctors(
    specialization_id: int | None = None,
    is_active: bool | None = None,
    min_experience: int | None = None,
    max_price: float | None = None,
    search: str | None = None,
):
    result = []
    for doctor in doctors:
        if specialization_id is not None and doctor["specialization_id"] != specialization_id:
            continue
        if is_active is not None and doctor["is_active"] != is_active:
            continue
        if min_experience is not None and doctor["experience_years"] < min_experience:
            continue
        if max_price is not None and doctor["consultation_price"] > max_price:
            continue
        if search is not None and search.lower() not in doctor["full_name"].lower():
            continue
        result.append(doctor)
    return result


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor

    raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")


@router.put("/{doctor_id}", response_model=DoctorResponse)
def put_doctor(doctor_id: int, data: DoctorReplace):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            specialization_found = False
            for specialization in specializations:
                if specialization["id"] == data.specialization_id:
                    specialization_found = True

            if not specialization_found:
                raise HTTPException(status_code=404, detail=f"Specialization with id {data.specialization_id} not found")

            doctor.update(data.model_dump())
            return doctor

    raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")


@router.patch("/{doctor_id}", response_model=DoctorResponse)
def patch_doctor(doctor_id: int, data: DoctorUpdate):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            update_data = data.model_dump(exclude_unset=True)

            if "specialization_id" in update_data:
                specialization_found = False
                for specialization in specializations:
                    if specialization["id"] == update_data["specialization_id"]:
                        specialization_found = True

                if not specialization_found:
                    raise HTTPException(status_code=404, detail=f"Specialization with id {update_data['specialization_id']} not found")

            doctor.update(update_data)
            return doctor

    raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")


@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            for appointment in appointments:
                if appointment["doctor_id"] == doctor_id:
                    raise HTTPException(status_code=409, detail=f"Doctor with id {doctor_id} has appointments and cannot be deleted")
            doctors.remove(doctor)
            return

    raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")


@router.get("/{doctor_id}/appointments", response_model=list[AppointmentResponse])
def get_doctor_appointments(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            result = []
            for appointment in appointments:
                if appointment["doctor_id"] == doctor_id:
                    result.append(appointment)
            return result

    raise HTTPException(status_code=404, detail=f"Doctor with id {doctor_id} not found")
