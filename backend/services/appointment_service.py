from sqlalchemy.orm import Session
from database import get_db, Appointment, AppointmentStatusEnum
from schemas import AppointmentCreate, AppointmentResponse
from typing import Optional, List
from datetime import datetime, timedelta
import json

class AppointmentService:
    def __init__(self):
        self.db = next(get_db())
    
    async def create_appointment(self, appointment_data: AppointmentCreate) -> Appointment:
        """Create a new appointment"""
        try:
            appointment = Appointment(
                patient_id=appointment_data.patient_id,
                hospital_id=appointment_data.hospital_id,
                appointment_date=appointment_data.appointment_date,
                notes=appointment_data.notes,
                status=AppointmentStatusEnum.SCHEDULED
            )
            
            self.db.add(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            
            return appointment
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_appointment(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID"""
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    def get_appointments_by_patient(self, patient_id: int) -> List[Appointment]:
        """Get all appointments for a patient"""
        return self.db.query(Appointment).filter(Appointment.patient_id == patient_id).all()
    
    def get_appointments_by_hospital(self, hospital_id: int) -> List[Appointment]:
        """Get all appointments for a hospital"""
        return self.db.query(Appointment).filter(Appointment.hospital_id == hospital_id).all()
    
    def get_appointments_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Appointment]:
        """Get appointments within a date range"""
        return self.db.query(Appointment).filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).all()
    
    def update_appointment_status(self, appointment_id: int, status: AppointmentStatusEnum, notes: str = None) -> Optional[Appointment]:
        """Update appointment status (Admin function)"""
        try:
            appointment = self.get_appointment(appointment_id)
            if not appointment:
                return None
            
            appointment.status = status
            if notes:
                appointment.notes = notes
            appointment.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(appointment)
            return appointment
        except Exception as e:
            self.db.rollback()
            raise e
    
    def reschedule_appointment(self, appointment_id: int, new_date: datetime) -> Optional[Appointment]:
        """Reschedule an appointment"""
        try:
            appointment = self.get_appointment(appointment_id)
            if not appointment:
                return None
            
            appointment.appointment_date = new_date
            appointment.status = AppointmentStatusEnum.RESCHEDULED
            appointment.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(appointment)
            return appointment
        except Exception as e:
            self.db.rollback()
            raise e
    
    def cancel_appointment(self, appointment_id: int, reason: str = None) -> Optional[Appointment]:
        """Cancel an appointment"""
        try:
            appointment = self.get_appointment(appointment_id)
            if not appointment:
                return None
            
            appointment.status = AppointmentStatusEnum.CANCELLED
            if reason:
                appointment.notes = f"Cancelled: {reason}"
            appointment.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(appointment)
            return appointment
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_available_slots(self, hospital_id: int, date: datetime) -> List[str]:
        """Get available appointment slots for a hospital on a specific date"""
        try:
            # Get hospital
            from services.hospital_service import HospitalService
            hospital_service = HospitalService()
            hospital = hospital_service.get_hospital(hospital_id)
            
            if not hospital:
                return []
            
            # Parse available slots from hospital
            available_slots = json.loads(hospital.available_slots)
            
            # Get existing appointments for the date
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            existing_appointments = self.db.query(Appointment).filter(
                Appointment.hospital_id == hospital_id,
                Appointment.appointment_date >= start_of_day,
                Appointment.appointment_date <= end_of_day,
                Appointment.status.in_([AppointmentStatusEnum.SCHEDULED, AppointmentStatusEnum.CONFIRMED])
            ).all()
            
            # Extract booked times
            booked_times = []
            for apt in existing_appointments:
                time_str = apt.appointment_date.strftime("%H:%M")
                booked_times.append(time_str)
            
            # Return available slots
            return [slot for slot in available_slots if slot not in booked_times]
            
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return []
    
    def get_appointment_statistics(self) -> dict:
        """Get appointment statistics (Admin function)"""
        try:
            total_appointments = self.db.query(Appointment).count()
            
            status_counts = {}
            for status in AppointmentStatusEnum:
                count = self.db.query(Appointment).filter(Appointment.status == status).count()
                status_counts[status.value] = count
            
            # Get appointments by month (last 12 months)
            from datetime import datetime, timedelta
            twelve_months_ago = datetime.utcnow() - timedelta(days=365)
            
            monthly_appointments = self.db.query(Appointment).filter(
                Appointment.created_at >= twelve_months_ago
            ).all()
            
            monthly_stats = {}
            for apt in monthly_appointments:
                month_key = apt.created_at.strftime("%Y-%m")
                monthly_stats[month_key] = monthly_stats.get(month_key, 0) + 1
            
            return {
                "total_appointments": total_appointments,
                "status_breakdown": status_counts,
                "monthly_trends": monthly_stats
            }
            
        except Exception as e:
            print(f"Error getting appointment statistics: {e}")
            return {}


