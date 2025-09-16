# This file is for Pydantic models (schemas)
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from database import GenderEnum, MedicalCategoryEnum, SubCategoryEnum, CallStatusEnum, AppointmentStatusEnum

# Patient Schemas
class PatientBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    gender: GenderEnum
    phone_number: str = Field(..., regex=r'^\+?1?\d{9,15}$')
    age: int = Field(..., ge=0, le=120)
    location: str = Field(..., min_length=2, max_length=100)
    problem_description: str = Field(..., min_length=10, max_length=1000)
    medical_category: MedicalCategoryEnum
    sub_category: SubCategoryEnum

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Hospital Schemas
class HospitalBase(BaseModel):
    name: str
    location: str
    address: str
    phone_number: str
    email: str
    specializations: List[str]
    available_slots: List[str]

class HospitalResponse(HospitalBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Appointment Schemas
class AppointmentBase(BaseModel):
    patient_id: int
    hospital_id: int
    appointment_date: datetime
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    id: int
    status: AppointmentStatusEnum
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Call Session Schemas
class CallSessionBase(BaseModel):
    patient_id: int
    twilio_call_sid: Optional[str] = None
    status: CallStatusEnum = CallStatusEnum.INITIATED
    conversation_log: Optional[List[dict]] = None
    diagnosis_notes: Optional[str] = None
    scheduled_appointment_id: Optional[int] = None

class CallSessionCreate(CallSessionBase):
    pass

class CallSessionResponse(CallSessionBase):
    id: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# AI Conversation Schemas
class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class DiagnosisRequest(BaseModel):
    patient_id: int
    symptoms: List[str]
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None

class DiagnosisResponse(BaseModel):
    diagnosis: str
    recommended_specialization: str
    urgency_level: str  # "low", "medium", "high", "urgent"
    recommended_hospitals: List[int]
    next_steps: List[str]

# Email Schemas
class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    appointment_id: Optional[int] = None

class EmailResponse(BaseModel):
    message_id: str
    status: str
    sent_at: datetime

