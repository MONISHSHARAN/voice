from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

# Database URL for local PostgreSQL
DATABASE_URL = "postgresql://medagg_user:medagg_password@localhost:5432/medagg"

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Enums
class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class LanguageEnum(str, enum.Enum):
    ENGLISH = "english"
    TAMIL = "tamil"
    HINDI = "hindi"

class MedicalCategoryEnum(str, enum.Enum):
    INTERVENTIONAL_CARDIOLOGY = "interventional_cardiology"

class SubCategoryEnum(str, enum.Enum):
    CHRONIC_TOTAL_OCCLUSION = "chronic_total_occlusion"
    RADIOFREQUENCY_ABLATION = "radiofrequency_ablation"

class CallStatusEnum(str, enum.Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"

class AppointmentStatusEnum(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

# Database Models
class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True)
    age = Column(Integer, nullable=False)
    location = Column(String(100), nullable=False)
    language_preference = Column(Enum(LanguageEnum), nullable=False, default=LanguageEnum.ENGLISH)
    problem_description = Column(Text, nullable=False)
    medical_category = Column(Enum(MedicalCategoryEnum), nullable=False)
    sub_category = Column(Enum(SubCategoryEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    call_sessions = relationship("CallSession", back_populates="patient")

class Hospital(Base):
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    location = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    specializations = Column(Text, nullable=False)  # JSON string of specializations
    available_slots = Column(Text, nullable=False)  # JSON string of available time slots
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="hospital")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.SCHEDULED)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    hospital = relationship("Hospital", back_populates="appointments")

class CallSession(Base):
    __tablename__ = "call_sessions"
    
    id = Column(String(50), primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    twilio_call_sid = Column(String(100))
    status = Column(Enum(CallStatusEnum), default=CallStatusEnum.INITIATED)
    conversation_log = Column(Text)  # JSON string of conversation
    diagnosis_notes = Column(Text)
    scheduled_appointment_id = Column(Integer, ForeignKey("appointments.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    patient = relationship("Patient", back_populates="call_sessions")
    scheduled_appointment = relationship("Appointment")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
