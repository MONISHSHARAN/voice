#!/usr/bin/env python3
"""
MedAgg Healthcare POC Backend Server
Simple, working version for immediate testing
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime
import uuid

# In-memory storage
patients_db = []
hospitals_db = []
appointments_db = []
call_sessions_db = []

# Initialize dummy data
def initialize_dummy_data():
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

class MedAggHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"message": "MedAgg Healthcare POC API", "status": "running", "version": "1.0.0"}
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/patients':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(patients_db).encode())
            
        elif self.path == '/api/hospitals':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(hospitals_db).encode())
            
        elif self.path == '/api/appointments':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(appointments_db).encode())
            
        elif self.path == '/api/calls':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(call_sessions_db).encode())
            
        elif self.path == '/api/admin/analytics/overview':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "patients": {
                    "total": len(patients_db),
                    "recent": len([p for p in patients_db if p['created_at'] > datetime.now().isoformat()[:10]])
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
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        if self.path == '/api/patients':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            patient_data = json.loads(post_data.decode('utf-8'))
            
            try:
                # Create patient
                patient_id = len(patients_db) + 1
                patient = {
                    "id": patient_id,
                    "name": patient_data['name'],
                    "gender": patient_data['gender'],
                    "phone_number": patient_data['phone_number'],
                    "age": patient_data['age'],
                    "location": patient_data['location'],
                    "language_preference": patient_data.get('language_preference', 'english'),
                    "problem_description": patient_data['problem_description'],
                    "medical_category": patient_data['medical_category'],
                    "sub_category": patient_data['sub_category'],
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
                self.simulate_ai_call(call_session_id, patient)
                
                # Create appointment
                appointment_id = len(appointments_db) + 1
                appointment = {
                    "id": appointment_id,
                    "patient_id": patient['id'],
                    "hospital_id": 1,
                    "appointment_date": datetime.now().replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
                    "status": "scheduled",
                    "notes": f"AI-scheduled appointment for {patient['name']} in {patient['language_preference']}"
                }
                appointments_db.append(appointment)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(patient).encode())
                
                print(f"✅ Patient {patient['name']} registered successfully!")
                print(f"📞 AI call initiated in {patient['language_preference']}")
                print(f"📅 Appointment scheduled for {appointment['appointment_date']}")
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"error": str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def simulate_ai_call(self, call_session_id: str, patient: dict):
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
            
            # Update call status to completed
            for session in call_sessions_db:
                if session['id'] == call_session_id:
                    session['status'] = 'completed'
                    break
            
            print(f"✅ AI call completed for patient {patient['name']} in {language}")
            print(f"📞 Call Session ID: {call_session_id}")
            
        except Exception as e:
            print(f"❌ Error in AI call simulation: {e}")

def run_server():
    initialize_dummy_data()
    server = HTTPServer(('localhost', 8000), MedAggHandler)
    print("🏥 MedAgg Healthcare POC Backend Started!")
    print("📊 Dummy data initialized")
    print("🌍 Multilingual AI ready (English, Tamil, Hindi)")
    print("🔗 API running on http://localhost:8000")
    print("📱 Frontend should be on http://localhost:3000")
    server.serve_forever()

if __name__ == "__main__":
    run_server()


