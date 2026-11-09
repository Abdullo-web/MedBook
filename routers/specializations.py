from fastapi import APIRouter, HTTPException

from data.storage import specializations, doctors, next_id
from schemas.specialization import SpecializationCreate, SpecializationUpdate, SpecializationResponse

router = APIRouter(prefix="/specializations", tags=["Specializations"])


@router.post("", response_model=SpecializationResponse, status_code=201)
def create_specialization(data: SpecializationCreate):
    for specialization in specializations:
        if specialization["name"].lower() == data.name.lower():
            raise HTTPException(status_code=409, detail=f"Specialization with name {data.name} already exists")

    new_id = next_id("specialization")
    new_specialization = data.model_dump()
    new_specialization["id"] = new_id
    specializations.append(new_specialization)
    return new_specialization


@router.get("", response_model=list[SpecializationResponse])
def get_specializations():
    return specializations


@router.get("/{specialization_id}", response_model=SpecializationResponse)
def get_specialization(specialization_id: int):
    for specialization in specializations:
        if specialization["id"] == specialization_id:
            return specialization

    raise HTTPException(status_code=404, detail=f"Specialization with id {specialization_id} not found")


@router.patch("/{specialization_id}", response_model=SpecializationResponse)
def patch_specialization(specialization_id: int, data: SpecializationUpdate):
    for specialization in specializations:
        if specialization["id"] == specialization_id:
            update_data = data.model_dump(exclude_unset=True)

            if "name" in update_data:
                for other in specializations:
                    if other["id"] != specialization_id and other["name"].lower() == update_data["name"].lower():
                        raise HTTPException(status_code=409, detail=f"Specialization with name {update_data['name']} already exists")

            specialization.update(update_data)
            return specialization

    raise HTTPException(status_code=404, detail=f"Specialization with id {specialization_id} not found")


@router.delete("/{specialization_id}", status_code=204)
def delete_specialization(specialization_id: int):
    for specialization in specializations:
        if specialization["id"] == specialization_id:
            for doctor in doctors:
                if doctor["specialization_id"] == specialization_id:
                    raise HTTPException(status_code=409, detail=f"Specialization with id {specialization_id} has doctors and cannot be deleted")
            specializations.remove(specialization)
            return

    raise HTTPException(status_code=404, detail=f"Specialization with id {specialization_id} not found")
