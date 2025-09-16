from sqlalchemy.orm import Session
from database import get_db, CallSession, CallStatusEnum
from schemas import CallSessionResponse
from typing import Optional, Dict
from datetime import datetime
import uuid
import json
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallService:
    def __init__(self):
        self.db = next(get_db())
        self.ai_service = None  # Will be initialized when needed
    
    async def create_call_session(self, patient_id: int) -> CallSession:
        """Create a new call session"""
        try:
            call_session_id = str(uuid.uuid4())
            
            call_session = CallSession(
                id=call_session_id,
                patient_id=patient_id,
                status=CallStatusEnum.INITIATED,
                conversation_log=[]
            )
            
            self.db.add(call_session)
            self.db.commit()
            self.db.refresh(call_session)
            
            logger.info(f"Created call session {call_session_id} for patient {patient_id}")
            return call_session
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating call session: {e}")
            raise e
    
    async def initiate_call(self, phone_number: str, call_session_id: str):
        """Initiate call via Twilio (simulated for POC)"""
        try:
            # For POC, we'll simulate the call initiation
            # In production, this would use Twilio API
            logger.info(f"Initiating call to {phone_number} for session {call_session_id}")
            
            # Update call status
            await self.update_call_status(call_session_id, CallStatusEnum.RINGING)
            
            # Simulate call delay
            await asyncio.sleep(2)
            
            # Update to in progress
            await self.update_call_status(call_session_id, CallStatusEnum.IN_PROGRESS)
            
            # Start the conversation
            await self._start_conversation(call_session_id)
            
        except Exception as e:
            logger.error(f"Error initiating call: {e}")
            await self.update_call_status(call_session_id, CallStatusEnum.FAILED)
    
    async def _start_conversation(self, call_session_id: str):
        """Start the AI conversation"""
        try:
            # Get call session
            call_session = self.get_call_session(call_session_id)
            if not call_session:
                return
            
            # Initialize AI service
            if not self.ai_service:
                from services.ai_service import AIService
                self.ai_service = AIService()
                await self.ai_service.initialize_models()
            
            # Get patient data
            from services.patient_service import PatientService
            patient_service = PatientService()
            patient = patient_service.get_patient(call_session.patient_id)
            
            if not patient:
                logger.error(f"Patient not found for call session {call_session_id}")
                return
            
            # Convert patient to dict
            patient_data = {
                "name": patient.name,
                "phone_number": patient.phone_number,
                "medical_category": patient.medical_category.value,
                "problem_description": patient.problem_description,
                "age": patient.age,
                "gender": patient.gender.value,
                "language_preference": patient.language_preference.value
            }
            
            # Start conversation
            initial_message = await self.ai_service.process_conversation(
                call_session_id, 
                "start_conversation", 
                patient_data
            )
            
            logger.info(f"Conversation started for session {call_session_id}")
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            await self.update_call_status(call_session_id, CallStatusEnum.FAILED)
    
    async def process_voice_input(self, call_session_id: str, audio_text: str) -> str:
        """Process voice input from patient"""
        try:
            # Get call session
            call_session = self.get_call_session(call_session_id)
            if not call_session:
                return "I'm sorry, I couldn't find your call session."
            
            # Get patient data
            from services.patient_service import PatientService
            patient_service = PatientService()
            patient = patient_service.get_patient(call_session.patient_id)
            
            if not patient:
                return "I'm sorry, I couldn't find your patient information."
            
            patient_data = {
                "name": patient.name,
                "phone_number": patient.phone_number,
                "medical_category": patient.medical_category.value,
                "problem_description": patient.problem_description,
                "age": patient.age,
                "gender": patient.gender.value
            }
            
            # Process with AI
            response = await self.ai_service.process_conversation(
                call_session_id, 
                audio_text, 
                patient_data
            )
            
            # Update conversation log
            await self._update_conversation_log(call_session_id, audio_text, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return "I'm sorry, I'm having trouble processing your request. Let me connect you to a human agent."
    
    async def _update_conversation_log(self, call_session_id: str, user_input: str, ai_response: str):
        """Update conversation log in database"""
        try:
            call_session = self.get_call_session(call_session_id)
            if not call_session:
                return
            
            # Get current conversation log
            conversation_log = call_session.conversation_log or []
            
            # Add new entries
            conversation_log.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            conversation_log.append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Update database
            call_session.conversation_log = conversation_log
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating conversation log: {e}")
    
    async def schedule_appointment_from_call(self, call_session_id: str) -> Optional[int]:
        """Schedule appointment based on call conversation"""
        try:
            # Get conversation summary
            if not self.ai_service:
                from services.ai_service import AIService
                self.ai_service = AIService()
            
            conversation_summary = await self.ai_service.get_conversation_summary(call_session_id)
            
            if not conversation_summary:
                return None
            
            # Get patient data
            call_session = self.get_call_session(call_session_id)
            if not call_session:
                return None
            
            from services.patient_service import PatientService
            patient_service = PatientService()
            patient = patient_service.get_patient(call_session.patient_id)
            
            if not patient:
                return None
            
            # Find suitable hospital
            from services.hospital_service import HospitalService
            hospital_service = HospitalService()
            
            # Get hospitals matching patient's medical category and location
            hospitals = await hospital_service.get_hospitals(
                specialization=patient.medical_category.value,
                location=patient.location
            )
            
            if not hospitals:
                # Fallback to any hospital with the specialization
                hospitals = await hospital_service.get_hospitals(
                    specialization=patient.medical_category.value
                )
            
            if not hospitals:
                logger.error("No suitable hospitals found")
                return None
            
            # Select first available hospital
            selected_hospital = hospitals[0]
            
            # Create appointment
            from services.appointment_service import AppointmentService
            appointment_service = AppointmentService()
            
            # Schedule for next available slot (simplified for POC)
            from datetime import datetime, timedelta
            appointment_date = datetime.utcnow() + timedelta(days=1)
            appointment_date = appointment_date.replace(hour=10, minute=0, second=0, microsecond=0)
            
            appointment_data = {
                "patient_id": patient.id,
                "hospital_id": selected_hospital.id,
                "appointment_date": appointment_date,
                "notes": f"AI-scheduled appointment based on call session {call_session_id}"
            }
            
            appointment = await appointment_service.create_appointment(appointment_data)
            
            # Update call session with appointment ID
            call_session.scheduled_appointment_id = appointment.id
            call_session.diagnosis_notes = conversation_summary.get("diagnosis_info", {}).get("recommendation", "")
            self.db.commit()
            
            logger.info(f"Appointment {appointment.id} scheduled for patient {patient.id}")
            return appointment.id
            
        except Exception as e:
            logger.error(f"Error scheduling appointment: {e}")
            return None
    
    async def complete_call(self, call_session_id: str):
        """Complete the call and schedule appointment"""
        try:
            # Schedule appointment
            appointment_id = await self.schedule_appointment_from_call(call_session_id)
            
            # Update call status
            await self.update_call_status(call_session_id, CallStatusEnum.COMPLETED)
            
            # Clear AI conversation context
            if self.ai_service:
                await self.ai_service.clear_conversation_context(call_session_id)
            
            logger.info(f"Call session {call_session_id} completed with appointment {appointment_id}")
            
        except Exception as e:
            logger.error(f"Error completing call: {e}")
            await self.update_call_status(call_session_id, CallStatusEnum.FAILED)
    
    async def update_call_status(self, call_session_id: str, status: CallStatusEnum):
        """Update call status"""
        try:
            call_session = self.get_call_session(call_session_id)
            if not call_session:
                return
            
            call_session.status = status
            if status == CallStatusEnum.COMPLETED:
                call_session.completed_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Call session {call_session_id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Error updating call status: {e}")
    
    def get_call_session(self, call_session_id: str) -> Optional[CallSession]:
        """Get call session by ID"""
        return self.db.query(CallSession).filter(CallSession.id == call_session_id).first()
    
    async def handle_twilio_webhook(self, request: dict):
        """Handle Twilio webhook (for production)"""
        # This would handle actual Twilio webhooks
        # For POC, we'll simulate this
        logger.info(f"Twilio webhook received: {request}")
        return {"status": "ok"}
    
    async def handle_status_webhook(self, request: dict):
        """Handle Twilio status webhook (for production)"""
        # This would handle actual Twilio status updates
        # For POC, we'll simulate this
        logger.info(f"Twilio status webhook received: {request}")
        return {"status": "ok"}
