from fastapi import FastAPI

from routers.specializations import router as specializations_router
from routers.doctors import router as doctors_router
from routers.patients import router as patients_router
from routers.appointments import router as appointments_router

app = FastAPI(title="MedBook API")

app.include_router(specializations_router, prefix="/api/v1")
app.include_router(doctors_router, prefix="/api/v1")
app.include_router(patients_router, prefix="/api/v1")
app.include_router(appointments_router, prefix="/api/v1")
