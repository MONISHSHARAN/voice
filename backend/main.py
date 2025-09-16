from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

from database import get_db, engine, Base
from schemas import (
    PatientCreate, PatientResponse, HospitalResponse, 
    AppointmentCreate, AppointmentResponse, CallSessionResponse
)
from services import (
    PatientService, HospitalService, AppointmentService, 
    AIService, CallService, EmailService
)
from admin_routes import admin_router

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="MedAgg Healthcare POC",
    description="AI-powered healthcare appointment booking system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include admin routes
app.include_router(admin_router)

# Initialize services
patient_service = PatientService()
hospital_service = HospitalService()
appointment_service = AppointmentService()
ai_service = AIService()
call_service = CallService()
email_service = EmailService()

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    # Create dummy hospitals
    await hospital_service.create_dummy_hospitals()
    print("MedAgg Healthcare POC started successfully!")

@app.get("/")
async def root():
    return {"message": "MedAgg Healthcare POC API", "status": "running"}

@app.post("/api/patients", response_model=PatientResponse)
async def create_patient(patient_data: PatientCreate, background_tasks: BackgroundTasks):
    """Create a new patient and trigger AI call"""
    try:
        # Create patient
        patient = await patient_service.create_patient(patient_data)
        
        # Trigger AI call in background
        background_tasks.add_task(initiate_ai_call, patient.id)
        
        return PatientResponse.from_orm(patient)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get patient by ID"""
    patient = patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse.from_orm(patient)

@app.get("/api/hospitals", response_model=list[HospitalResponse])
async def get_hospitals(specialization: str = None, location: str = None):
    """Get hospitals with optional filtering"""
    hospitals = await hospital_service.get_hospitals(specialization, location)
    return [HospitalResponse.from_orm(hospital) for hospital in hospitals]

@app.post("/api/appointments", response_model=AppointmentResponse)
async def create_appointment(appointment_data: AppointmentCreate):
    """Create a new appointment"""
    try:
        appointment = await appointment_service.create_appointment(appointment_data)
        return AppointmentResponse.from_orm(appointment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: int):
    """Get appointment by ID"""
    appointment = appointment_service.get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return AppointmentResponse.from_orm(appointment)

@app.post("/api/calls/{call_id}/status")
async def update_call_status(call_id: str, status: str):
    """Update call status"""
    await call_service.update_call_status(call_id, status)
    return {"message": "Call status updated"}

@app.get("/api/calls/{call_id}", response_model=CallSessionResponse)
async def get_call_session(call_id: str):
    """Get call session details"""
    session = await call_service.get_call_session(call_id)
    if not session:
        raise HTTPException(status_code=404, detail="Call session not found")
    return CallSessionResponse.from_orm(session)

# Webhook endpoints for Twilio
@app.post("/api/webhooks/twilio/voice")
async def twilio_voice_webhook(request: dict):
    """Handle incoming Twilio voice calls"""
    return await call_service.handle_twilio_webhook(request)

@app.post("/api/webhooks/twilio/status")
async def twilio_status_webhook(request: dict):
    """Handle Twilio call status updates"""
    return await call_service.handle_status_webhook(request)

# Background task functions
async def initiate_ai_call(patient_id: int):
    """Initiate AI call to patient"""
    try:
        # Get patient details
        patient = patient_service.get_patient(patient_id)
        if not patient:
            return
        
        # Create call session
        call_session = await call_service.create_call_session(patient_id)
        
        # Initiate call via Twilio
        await call_service.initiate_call(patient.phone_number, call_session.id)
        
        print(f"AI call initiated for patient {patient_id}")
    except Exception as e:
        print(f"Error initiating AI call: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
