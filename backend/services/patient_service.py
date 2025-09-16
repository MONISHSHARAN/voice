from sqlalchemy.orm import Session
from database import get_db, Patient
from schemas import PatientCreate, PatientResponse
from typing import Optional
import uuid

class PatientService:
    def __init__(self):
        self.db = next(get_db())
    
    async def create_patient(self, patient_data: PatientCreate) -> Patient:
        """Create a new patient"""
        try:
            # Check if patient already exists with same phone number
            existing_patient = self.db.query(Patient).filter(
                Patient.phone_number == patient_data.phone_number
            ).first()
            
            if existing_patient:
                return existing_patient
            
            # Create new patient
            patient = Patient(
                name=patient_data.name,
                gender=patient_data.gender,
                phone_number=patient_data.phone_number,
                age=patient_data.age,
                location=patient_data.location,
                language_preference=patient_data.language_preference,
                problem_description=patient_data.problem_description,
                medical_category=patient_data.medical_category,
                sub_category=patient_data.sub_category
            )
            
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
            
            return patient
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_patient(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID"""
        return self.db.query(Patient).filter(Patient.id == patient_id).first()
    
    def get_patient_by_phone(self, phone_number: str) -> Optional[Patient]:
        """Get patient by phone number"""
        return self.db.query(Patient).filter(Patient.phone_number == phone_number).first()
    
    def update_patient(self, patient_id: int, update_data: dict) -> Optional[Patient]:
        """Update patient information"""
        try:
            patient = self.get_patient(patient_id)
            if not patient:
                return None
            
            for key, value in update_data.items():
                if hasattr(patient, key):
                    setattr(patient, key, value)
            
            self.db.commit()
            self.db.refresh(patient)
            return patient
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_patient(self, patient_id: int) -> bool:
        """Delete patient"""
        try:
            patient = self.get_patient(patient_id)
            if not patient:
                return False
            
            self.db.delete(patient)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
