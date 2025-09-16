#!/usr/bin/env python3
"""
Simplified MedAgg Healthcare POC Backend
This version works without complex dependencies for testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import uuid

# Create FastAPI app
app = FastAPI(
    title="MedAgg Healthcare POC",
    description="AI-powered healthcare appointment booking system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
patients_db = []
hospitals_db = []
appointments_db = []
call_sessions_db = []

# Pydantic models
class PatientCreate(BaseModel):
    name: str
    gender: str
    phone_number: str
    age: int
    location: str
    language_preference: str = "english"
    problem_description: str
    medical_category: str
    sub_category: str

class PatientResponse(BaseModel):
    id: int
    name: str
    gender: str
    phone_number: str
    age: int
    location: str
    language_preference: str
    problem_description: str
    medical_category: str
    sub_category: str
    created_at: str

class HospitalResponse(BaseModel):
    id: int
    name: str
    location: str
    address: str
    phone_number: str
    email: str
    specializations: List[str]

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    hospital_id: int
    appointment_date: str
    status: str
    notes: Optional[str] = None

class CallSessionResponse(BaseModel):
    id: str
    patient_id: int
    status: str
    conversation_log: List[dict]
    created_at: str

# Initialize dummy data
def initialize_dummy_data():
    """Initialize dummy hospitals and data"""
    global hospitals_db
    
    hospitals_db = [
        {
            "id": 1,
            "name": "MedCity General Hospital",
            "location": "New York",
            "address": "123 Medical Plaza, New York, NY 10001",
            "phone_number": "+1-555-0101",
            "email": "info@medcityny.com",
            "specializations": ["interventional_cardiology", "chronic_total_occlusion", "radiofrequency_ablation"]
        },
        {
            "id": 2,
            "name": "CardioCare Center",
            "location": "Los Angeles",
            "address": "456 Heart Street, Los Angeles, CA 90210",
            "phone_number": "+1-555-0102",
            "email": "contact@cardiocare.com",
            "specializations": ["interventional_cardiology", "chronic_total_occlusion"]
        },
        {
            "id": 3,
            "name": "Advanced Heart Institute",
            "location": "Chicago",
            "address": "789 Cardiac Ave, Chicago, IL 60601",
            "phone_number": "+1-555-0103",
            "email": "info@advancedheart.com",
            "specializations": ["interventional_cardiology", "radiofrequency_ablation"]
        }
    ]

# Multilingual AI responses
def get_ai_response(language: str, stage: str, patient_data: dict) -> str:
    """Get AI response based on language and conversation stage"""
    
    responses = {
        "english": {
            "greeting": f"Hello {patient_data['name']}, this is MedAgg calling. I'm your AI healthcare assistant. I received your request for {patient_data['medical_category'].replace('_', ' ')} consultation. Can you please confirm your phone number ending in {patient_data['phone_number'][-4:]}?",
            "symptom_inquiry": f"Thank you for confirming. Now, I'd like to ask you some questions about your symptoms to better understand your condition. Can you tell me more about the problem you described: '{patient_data['problem_description']}'? What specific symptoms are you experiencing?",
            "diagnosis": "Based on your symptoms, I recommend immediate consultation with a cardiologist. The urgency level is high. This will help ensure you get the appropriate care for your condition.",
            "appointment": "Great! Let me help you schedule an appointment. I'll find the best available specialist in your area and book a convenient time for you.",
            "confirmation": "Perfect! I've found a suitable appointment for you. Let me confirm the details and send you an email with all the information."
        },
        "tamil": {
            "greeting": f"வணக்கம் {patient_data['name']}, இது MedAgg அழைப்பு. நான் உங்கள் AI சுகாதார உதவியாளர். நான் உங்கள் {patient_data['medical_category'].replace('_', ' ')} ஆலோசனை கோரிக்கையைப் பெற்றேன். உங்கள் தொலைபேசி எண்ணின் கடைசி 4 இலக்கங்களை {patient_data['phone_number'][-4:]} என்பதை உறுதிப்படுத்த முடியுமா?",
            "symptom_inquiry": f"உறுதிப்படுத்தியதற்கு நன்றி. இப்போது, உங்கள் நிலையை நன்றாக புரிந்துகொள்ள உங்கள் அறிகுறிகள் பற்றி சில கேள்விகளைக் கேட்க விரும்புகிறேன். நீங்கள் விவரித்த பிரச்சினையைப் பற்றி மேலும் சொல்ல முடியுமா: '{patient_data['problem_description']}'? நீங்கள் எந்த குறிப்பிட்ட அறிகுறிகளை அனுபவிக்கிறீர்கள்?",
            "diagnosis": "உங்கள் அறிகுறிகளின் அடிப்படையில், நான் இதயவியல் நிபுணருடன் உடனடி ஆலோசனையை பரிந்துரைக்கிறேன். அவசரநிலை நிலை உயர். இது உங்கள் நிலைக்கு பொருத்தமான பராமரிப்பைப் பெற உதவும்.",
            "appointment": "சிறப்பு! நான் உங்களுக்கு ஒரு நேரத்தை திட்டமிட உதவுகிறேன். நான் உங்கள் பகுதியில் சிறந்த கிடைக்கும் நிபுணரைக் கண்டுபிடித்து வசதியான நேரத்தில் பதிவு செய்கிறேன்.",
            "confirmation": "சரியானது! நான் உங்களுக்கு பொருத்தமான நேரத்தைக் கண்டுபிடித்தேன். விவரங்களை உறுதிப்படுத்தி அனைத்து தகவல்களுடன் உங்களுக்கு மின்னஞ்சல் அனுப்புகிறேன்."
        },
        "hindi": {
            "greeting": f"नमस्ते {patient_data['name']}, यह MedAgg का कॉल है। मैं आपका AI स्वास्थ्य सहायक हूं। मुझे आपके {patient_data['medical_category'].replace('_', ' ')} परामर्श के लिए अनुरोध प्राप्त हुआ है। क्या आप अपना फोन नंबर जो {patient_data['phone_number'][-4:]} पर समाप्त होता है, उसे पुष्टि कर सकते हैं?",
            "symptom_inquiry": f"पुष्टि करने के लिए धन्यवाद। अब, मैं आपकी स्थिति को बेहतर समझने के लिए आपके लक्षणों के बारे में कुछ प्रश्न पूछना चाहूंगा। क्या आप उस समस्या के बारे में और बता सकते हैं जिसका आपने वर्णन किया: '{patient_data['problem_description']}'? आप कौन से विशिष्ट लक्षणों का अनुभव कर रहे हैं?",
            "diagnosis": "आपके लक्षणों के आधार पर, मैं हृदय रोग विशेषज्ञ के साथ तत्काल परामर्श की सिफारिश करता हूं। तात्कालिकता स्तर उच्च है। यह सुनिश्चित करेगा कि आपको अपनी स्थिति के लिए उपयुक्त देखभाल मिले।",
            "appointment": "बहुत बढ़िया! मैं आपके लिए अपॉइंटमेंट शेड्यूल करने में मदद करूंगा। मैं आपके क्षेत्र में सबसे अच्छे उपलब्ध विशेषज्ञ को खोजूंगा और आपके लिए सुविधाजनक समय बुक करूंगा।",
            "confirmation": "बहुत बढ़िया! मैंने आपके लिए एक उपयुक्त अपॉइंटमेंट खोजा है। मुझे विवरणों की पुष्टि करने दें और सभी जानकारी के साथ आपको ईमेल भेजने दें।"
        }
    }
    
    return responses.get(language, responses["english"]).get(stage, "I'm here to help. How can I assist you further?")

# API Endpoints
@app.get("/")
async def root():
    return {"message": "MedAgg Healthcare POC API", "status": "running", "version": "1.0.0"}

@app.post("/api/patients", response_model=PatientResponse)
async def create_patient(patient_data: PatientCreate):
    """Create a new patient and trigger AI call simulation"""
    try:
        # Create patient
        patient_id = len(patients_db) + 1
        patient = {
            "id": patient_id,
            "name": patient_data.name,
            "gender": patient_data.gender,
            "phone_number": patient_data.phone_number,
            "age": patient_data.age,
            "location": patient_data.location,
            "language_preference": patient_data.language_preference,
            "problem_description": patient_data.problem_description,
            "medical_category": patient_data.medical_category,
            "sub_category": patient_data.sub_category,
            "created_at": datetime.now().isoformat()
        }
        patients_db.append(patient)
        
        # Create call session
        call_session_id = str(uuid.uuid4())
        call_session = {
            "id": call_session_id,
            "patient_id": patient_id,
            "status": "initiated",
            "conversation_log": [],
            "created_at": datetime.now().isoformat()
        }
        call_sessions_db.append(call_session)
        
        # Simulate AI call process
        await simulate_ai_call(call_session_id, patient)
        
        return PatientResponse(**patient)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def simulate_ai_call(call_session_id: str, patient: dict):
    """Simulate AI call process"""
    try:
        language = patient.get('language_preference', 'english')
        
        # Update call status
        for session in call_sessions_db:
            if session['id'] == call_session_id:
                session['status'] = 'in_progress'
                break
        
        # Simulate conversation
        conversation_stages = ['greeting', 'symptom_inquiry', 'diagnosis', 'appointment', 'confirmation']
        
        for stage in conversation_stages:
            # Get AI response
            ai_response = get_ai_response(language, stage, patient)
            
            # Log conversation
            for session in call_sessions_db:
                if session['id'] == call_session_id:
                    session['conversation_log'].append({
                        "role": "assistant",
                        "content": ai_response,
                        "timestamp": datetime.now().isoformat(),
                        "stage": stage
                    })
                    break
            
            # Simulate delay between responses
            import asyncio
            await asyncio.sleep(1)
        
        # Create appointment
        appointment_id = len(appointments_db) + 1
        appointment = {
            "id": appointment_id,
            "patient_id": patient['id'],
            "hospital_id": 1,  # Default to first hospital
            "appointment_date": (datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)).isoformat(),
            "status": "scheduled",
            "notes": f"AI-scheduled appointment for {patient['name']} in {language}"
        }
        appointments_db.append(appointment)
        
        # Update call status to completed
        for session in call_sessions_db:
            if session['id'] == call_session_id:
                session['status'] = 'completed'
                break
        
        print(f"✅ AI call completed for patient {patient['name']} in {language}")
        print(f"📞 Call Session ID: {call_session_id}")
        print(f"📅 Appointment ID: {appointment_id}")
        
    except Exception as e:
        print(f"❌ Error in AI call simulation: {e}")

@app.get("/api/patients", response_model=List[PatientResponse])
async def get_patients():
    """Get all patients"""
    return [PatientResponse(**patient) for patient in patients_db]

@app.get("/api/hospitals", response_model=List[HospitalResponse])
async def get_hospitals():
    """Get all hospitals"""
    return [HospitalResponse(**hospital) for hospital in hospitals_db]

@app.get("/api/appointments", response_model=List[AppointmentResponse])
async def get_appointments():
    """Get all appointments"""
    return [AppointmentResponse(**appointment) for appointment in appointments_db]

@app.get("/api/calls", response_model=List[CallSessionResponse])
async def get_call_sessions():
    """Get all call sessions"""
    return [CallSessionResponse(**session) for session in call_sessions_db]

@app.get("/api/calls/{call_id}", response_model=CallSessionResponse)
async def get_call_session(call_id: str):
    """Get specific call session"""
    for session in call_sessions_db:
        if session['id'] == call_id:
            return CallSessionResponse(**session)
    raise HTTPException(status_code=404, detail="Call session not found")

# Admin endpoints
@app.get("/api/admin/analytics/overview")
async def get_system_overview():
    """Get system overview for admin dashboard"""
    return {
        "patients": {
            "total": len(patients_db),
            "recent": len([p for p in patients_db if p['created_at'] > (datetime.now().isoformat()[:10])])
        },
        "hospitals": {
            "total": len(hospitals_db)
        },
        "appointments": {
            "total_appointments": len(appointments_db),
            "status_breakdown": {
                "scheduled": len([a for a in appointments_db if a['status'] == 'scheduled']),
                "completed": len([a for a in appointments_db if a['status'] == 'completed']),
                "cancelled": len([a for a in appointments_db if a['status'] == 'cancelled'])
            }
        },
        "calls": {
            "total": len(call_sessions_db),
            "completed": len([c for c in call_sessions_db if c['status'] == 'completed']),
            "failed": len([c for c in call_sessions_db if c['status'] == 'failed']),
            "success_rate": (len([c for c in call_sessions_db if c['status'] == 'completed']) / len(call_sessions_db) * 100) if call_sessions_db else 0
        }
    }

@app.get("/api/admin/patients", response_model=List[PatientResponse])
async def get_all_patients():
    """Get all patients for admin"""
    return [PatientResponse(**patient) for patient in patients_db]

@app.get("/api/admin/hospitals", response_model=List[HospitalResponse])
async def get_all_hospitals():
    """Get all hospitals for admin"""
    return [HospitalResponse(**hospital) for hospital in hospitals_db]

@app.get("/api/admin/appointments", response_model=List[AppointmentResponse])
async def get_all_appointments():
    """Get all appointments for admin"""
    return [AppointmentResponse(**appointment) for appointment in appointments_db]

@app.get("/api/admin/calls", response_model=List[CallSessionResponse])
async def get_all_call_sessions():
    """Get all call sessions for admin"""
    return [CallSessionResponse(**session) for session in call_sessions_db]

# Initialize dummy data on startup
@app.on_event("startup")
async def startup_event():
    initialize_dummy_data()
    print("🏥 MedAgg Healthcare POC Backend Started!")
    print("📊 Dummy data initialized")
    print("🌍 Multilingual AI ready (English, Tamil, Hindi)")
    print("🔗 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


