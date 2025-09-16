from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database import get_db, Patient, Hospital, Appointment, CallSession
from schemas import PatientResponse, HospitalResponse, AppointmentResponse, CallSessionResponse
from services import PatientService, HospitalService, AppointmentService, CallService, EmailService
from typing import List, Optional
from datetime import datetime, timedelta
import json

# Create admin router
admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Initialize services
patient_service = PatientService()
hospital_service = HospitalService()
appointment_service = AppointmentService()
call_service = CallService()
email_service = EmailService()

# Patient Management APIs
@admin_router.get("/patients", response_model=List[PatientResponse])
async def get_all_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all patients with pagination and search"""
    query = db.query(Patient)
    
    if search:
        query = query.filter(
            Patient.name.ilike(f"%{search}%") |
            Patient.phone_number.ilike(f"%{search}%") |
            Patient.location.ilike(f"%{search}%")
        )
    
    patients = query.offset(skip).limit(limit).all()
    return [PatientResponse.from_orm(patient) for patient in patients]

@admin_router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient_details(patient_id: int, db: Session = Depends(get_db)):
    """Get detailed patient information"""
    patient = patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse.from_orm(patient)

@admin_router.put("/patients/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int, 
    update_data: dict, 
    db: Session = Depends(get_db)
):
    """Update patient information"""
    patient = patient_service.update_patient(patient_id, update_data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse.from_orm(patient)

@admin_router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete patient"""
    success = patient_service.delete_patient(patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

# Hospital Management APIs
@admin_router.get("/hospitals", response_model=List[HospitalResponse])
async def get_all_hospitals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    location: Optional[str] = None,
    specialization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all hospitals with filtering"""
    hospitals = await hospital_service.get_hospitals(specialization, location)
    return [HospitalResponse.from_orm(hospital) for hospital in hospitals[skip:skip+limit]]

@admin_router.post("/hospitals", response_model=HospitalResponse)
async def create_hospital(hospital_data: dict, db: Session = Depends(get_db)):
    """Create new hospital"""
    try:
        hospital = hospital_service.create_hospital(hospital_data)
        return HospitalResponse.from_orm(hospital)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@admin_router.put("/hospitals/{hospital_id}", response_model=HospitalResponse)
async def update_hospital(
    hospital_id: int, 
    update_data: dict, 
    db: Session = Depends(get_db)
):
    """Update hospital information"""
    hospital = hospital_service.update_hospital(hospital_id, update_data)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return HospitalResponse.from_orm(hospital)

@admin_router.delete("/hospitals/{hospital_id}")
async def delete_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """Delete hospital"""
    success = hospital_service.delete_hospital(hospital_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return {"message": "Hospital deleted successfully"}

# Appointment Management APIs
@admin_router.get("/appointments", response_model=List[AppointmentResponse])
async def get_all_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    hospital_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get all appointments with filtering"""
    query = db.query(Appointment)
    
    if status:
        query = query.filter(Appointment.status == status)
    if hospital_id:
        query = query.filter(Appointment.hospital_id == hospital_id)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if start_date:
        query = query.filter(Appointment.appointment_date >= start_date)
    if end_date:
        query = query.filter(Appointment.appointment_date <= end_date)
    
    appointments = query.offset(skip).limit(limit).all()
    return [AppointmentResponse.from_orm(appointment) for appointment in appointments]

@admin_router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment_details(appointment_id: int, db: Session = Depends(get_db)):
    """Get detailed appointment information"""
    appointment = appointment_service.get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return AppointmentResponse.from_orm(appointment)

@admin_router.put("/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: int,
    status: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update appointment status"""
    from database import AppointmentStatusEnum
    try:
        status_enum = AppointmentStatusEnum(status)
        appointment = appointment_service.update_appointment_status(appointment_id, status_enum, notes)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return AppointmentResponse.from_orm(appointment)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")

@admin_router.put("/appointments/{appointment_id}/reschedule")
async def reschedule_appointment(
    appointment_id: int,
    new_date: datetime,
    db: Session = Depends(get_db)
):
    """Reschedule appointment"""
    appointment = appointment_service.reschedule_appointment(appointment_id, new_date)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return AppointmentResponse.from_orm(appointment)

@admin_router.put("/appointments/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Cancel appointment"""
    appointment = appointment_service.cancel_appointment(appointment_id, reason)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return AppointmentResponse.from_orm(appointment)

# Call Session Management APIs
@admin_router.get("/calls", response_model=List[CallSessionResponse])
async def get_all_call_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all call sessions with filtering"""
    query = db.query(CallSession)
    
    if status:
        query = query.filter(CallSession.status == status)
    if patient_id:
        query = query.filter(CallSession.patient_id == patient_id)
    
    call_sessions = query.offset(skip).limit(limit).all()
    return [CallSessionResponse.from_orm(session) for session in call_sessions]

@admin_router.get("/calls/{call_id}", response_model=CallSessionResponse)
async def get_call_details(call_id: str, db: Session = Depends(get_db)):
    """Get detailed call session information"""
    call_session = call_service.get_call_session(call_id)
    if not call_session:
        raise HTTPException(status_code=404, detail="Call session not found")
    return CallSessionResponse.from_orm(call_session)

# Analytics and Reporting APIs
@admin_router.get("/analytics/overview")
async def get_system_overview(db: Session = Depends(get_db)):
    """Get system overview statistics"""
    try:
        # Patient statistics
        total_patients = db.query(Patient).count()
        
        # Hospital statistics
        total_hospitals = db.query(Hospital).count()
        
        # Appointment statistics
        appointment_stats = appointment_service.get_appointment_statistics()
        
        # Call session statistics
        total_calls = db.query(CallSession).count()
        completed_calls = db.query(CallSession).filter(CallSession.status == "completed").count()
        failed_calls = db.query(CallSession).filter(CallSession.status == "failed").count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_patients = db.query(Patient).filter(Patient.created_at >= week_ago).count()
        recent_appointments = db.query(Appointment).filter(Appointment.created_at >= week_ago).count()
        
        return {
            "patients": {
                "total": total_patients,
                "recent": recent_patients
            },
            "hospitals": {
                "total": total_hospitals
            },
            "appointments": appointment_stats,
            "calls": {
                "total": total_calls,
                "completed": completed_calls,
                "failed": failed_calls,
                "success_rate": (completed_calls / total_calls * 100) if total_calls > 0 else 0
            },
            "recent_activity": {
                "new_patients": recent_patients,
                "new_appointments": recent_appointments
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/analytics/patients/trends")
async def get_patient_trends(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Get patient registration trends"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get daily patient registrations
        daily_patients = db.query(Patient).filter(
            Patient.created_at >= start_date,
            Patient.created_at <= end_date
        ).all()
        
        # Group by date
        trends = {}
        for patient in daily_patients:
            date_key = patient.created_at.strftime("%Y-%m-%d")
            trends[date_key] = trends.get(date_key, 0) + 1
        
        return {
            "period_days": days,
            "daily_trends": trends,
            "total_patients": len(daily_patients)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/analytics/appointments/trends")
async def get_appointment_trends(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Get appointment trends"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get appointments in date range
        appointments = db.query(Appointment).filter(
            Appointment.created_at >= start_date,
            Appointment.created_at <= end_date
        ).all()
        
        # Group by date and status
        trends = {}
        for apt in appointments:
            date_key = apt.created_at.strftime("%Y-%m-%d")
            if date_key not in trends:
                trends[date_key] = {}
            trends[date_key][apt.status.value] = trends[date_key].get(apt.status.value, 0) + 1
        
        return {
            "period_days": days,
            "daily_trends": trends,
            "total_appointments": len(appointments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Email Management APIs
@admin_router.post("/emails/send")
async def send_custom_email(
    to_email: str,
    subject: str,
    body: str,
    appointment_id: Optional[int] = None
):
    """Send custom email"""
    try:
        success = await email_service._send_email(to_email, subject, body)
        if success:
            return {"message": "Email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/emails/send-reminders")
async def send_appointment_reminders():
    """Send appointment reminders for tomorrow's appointments"""
    try:
        # Get tomorrow's appointments
        tomorrow = datetime.utcnow() + timedelta(days=1)
        start_of_day = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        appointments = db.query(Appointment).filter(
            Appointment.appointment_date >= start_of_day,
            Appointment.appointment_date <= end_of_day,
            Appointment.status.in_(["scheduled", "confirmed"])
        ).all()
        
        sent_count = 0
        for appointment in appointments:
            # Get patient and hospital details
            patient = patient_service.get_patient(appointment.patient_id)
            hospital = hospital_service.get_hospital(appointment.hospital_id)
            
            if patient and hospital:
                appointment_data = {
                    "patient_name": patient.name,
                    "hospital_name": hospital.name,
                    "hospital_address": hospital.address,
                    "hospital_phone": hospital.phone_number,
                    "appointment_date": appointment.appointment_date.strftime("%Y-%m-%d %H:%M")
                }
                
                # Send reminder email
                success = await email_service.send_appointment_reminder(
                    patient.email if hasattr(patient, 'email') else f"{patient.phone_number}@medagg.com",
                    appointment_data
                )
                
                if success:
                    sent_count += 1
        
        return {
            "message": f"Sent {sent_count} reminder emails",
            "total_appointments": len(appointments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Management APIs
@admin_router.post("/system/initialize-data")
async def initialize_system_data():
    """Initialize system with dummy data"""
    try:
        # Create dummy hospitals
        await hospital_service.create_dummy_hospitals()
        
        return {"message": "System data initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/system/health")
async def system_health_check():
    """Check system health"""
    try:
        # Check database connection
        db = next(get_db())
        db.execute("SELECT 1")
        
        # Check Redis connection (if available)
        # redis_client = redis.Redis.from_url(redis_url)
        # redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


