# Simple in-memory storage for cardiology appointments and assessments
APPOINTMENTS_DB = {"appointments": {}, "next_id": 1}
ASSESSMENTS_DB = {"assessments": {}, "next_id": 1}

def assess_chest_pain(location, pain_type, duration, triggers="", radiation=""):
    """Assess chest pain symptoms for cardiology evaluation"""
    assessment_id = ASSESSMENTS_DB["next_id"]
    ASSESSMENTS_DB["next_id"] += 1
    
    # Risk assessment based on symptoms
    risk_factors = 0
    risk_level = "low"
    
    # High-risk indicators
    if "sharp" in pain_type.lower() or "stabbing" in pain_type.lower():
        risk_factors += 2
    if "pressure" in pain_type.lower() or "tightness" in pain_type.lower():
        risk_factors += 1
    if "arm" in radiation.lower() or "neck" in radiation.lower() or "jaw" in radiation.lower():
        risk_factors += 3
    if "activity" in triggers.lower() or "exercise" in triggers.lower():
        risk_factors += 1
    if "constant" in duration.lower() or "hours" in duration.lower():
        risk_factors += 1
    
    if risk_factors >= 4:
        risk_level = "high"
    elif risk_factors >= 2:
        risk_level = "medium"
    
    assessment = {
        "id": assessment_id,
        "type": "chest_pain",
        "location": location,
        "pain_type": pain_type,
        "duration": duration,
        "triggers": triggers,
        "radiation": radiation,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "created_at": "2024-01-01T00:00:00Z"  # Will be updated with actual timestamp
    }
    
    ASSESSMENTS_DB["assessments"][assessment_id] = assessment
    
    # Generate recommendation based on risk level
    if risk_level == "high":
        recommendation = f"URGENT: Based on your chest pain symptoms ({pain_type} pain in {location} with {radiation}), this requires immediate medical attention. Please call 108 or go to the nearest emergency room immediately."
        priority = "emergency"
    elif risk_level == "medium":
        recommendation = f"Based on your chest pain symptoms ({pain_type} pain in {location} lasting {duration}), I recommend scheduling an urgent cardiology consultation within 24-48 hours."
        priority = "urgent"
    else:
        recommendation = f"Based on your chest pain symptoms ({pain_type} pain in {location} lasting {duration}), I recommend scheduling a routine cardiology consultation for further evaluation."
        priority = "routine"
    
    return {
        "assessment_id": assessment_id,
        "assessment": assessment,
        "recommendation": recommendation,
        "priority": priority,
        "next_steps": "Schedule cardiology consultation for comprehensive evaluation"
    }

def assess_breathing(severity, timing, duration="", associated_symptoms=""):
    """Assess breathing difficulties and shortness of breath"""
    assessment_id = ASSESSMENTS_DB["next_id"]
    ASSESSMENTS_DB["next_id"] += 1
    
    # Risk assessment for breathing issues
    risk_factors = 0
    risk_level = "low"
    
    if severity.lower() == "severe":
        risk_factors += 3
    elif severity.lower() == "moderate":
        risk_factors += 1
    
    if "rest" in timing.lower() or "lying" in timing.lower():
        risk_factors += 2
    if "swelling" in associated_symptoms.lower() or "edema" in associated_symptoms.lower():
        risk_factors += 2
    if "dizziness" in associated_symptoms.lower() or "fainting" in associated_symptoms.lower():
        risk_factors += 1
    
    if risk_factors >= 4:
        risk_level = "high"
    elif risk_factors >= 2:
        risk_level = "medium"
    
    assessment = {
        "id": assessment_id,
        "type": "breathing",
        "severity": severity,
        "timing": timing,
        "duration": duration,
        "associated_symptoms": associated_symptoms,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    ASSESSMENTS_DB["assessments"][assessment_id] = assessment
    
    # Generate recommendation
    if risk_level == "high":
        recommendation = f"URGENT: Severe breathing difficulty {timing} requires immediate medical attention. Please call 108 or go to the nearest emergency room immediately."
        priority = "emergency"
    elif risk_level == "medium":
        recommendation = f"Based on your breathing assessment ({severity} difficulty {timing}), I recommend scheduling an urgent pulmonary/cardiology consultation within 24-48 hours."
        priority = "urgent"
    else:
        recommendation = f"Based on your breathing assessment ({severity} difficulty {timing}), I recommend scheduling a routine consultation for pulmonary evaluation."
        priority = "routine"
    
    return {
        "assessment_id": assessment_id,
        "assessment": assessment,
        "recommendation": recommendation,
        "priority": priority,
        "next_steps": "Schedule pulmonary/cardiology consultation for breathing evaluation"
    }

def schedule_appointment(patient_name, phone_number, appointment_type, urgency, preferred_time=""):
    """Schedule a cardiology appointment"""
    appointment_id = APPOINTMENTS_DB["next_id"]
    APPOINTMENTS_DB["next_id"] += 1
    
    # Determine appointment details based on urgency
    if urgency.lower() == "emergency":
        appointment_time = "Immediate - Emergency Department"
        duration = "Emergency consultation"
    elif urgency.lower() == "high":
        appointment_time = "Within 24-48 hours"
        duration = "Urgent consultation (30-45 minutes)"
    elif urgency.lower() == "medium":
        appointment_time = "Within 1 week"
        duration = "Standard consultation (30 minutes)"
    else:
        appointment_time = "Within 2-4 weeks"
        duration = "Routine consultation (20-30 minutes)"
    
    if preferred_time and urgency.lower() != "emergency":
        appointment_time = f"{preferred_time} - {appointment_time}"
    
    appointment = {
        "id": appointment_id,
        "patient_name": patient_name,
        "phone_number": phone_number,
        "appointment_type": appointment_type,
        "urgency": urgency,
        "preferred_time": preferred_time,
        "scheduled_time": appointment_time,
        "duration": duration,
        "status": "scheduled",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    APPOINTMENTS_DB["appointments"][appointment_id] = appointment
    
    return {
        "appointment_id": appointment_id,
        "message": f"Appointment {appointment_id} scheduled successfully for {patient_name}",
        "appointment_details": appointment,
        "confirmation": f"Your {appointment_type} appointment is scheduled for {appointment_time}. Duration: {duration}. You will receive a confirmation call shortly."
    }

def check_appointment(appointment_id):
    """Check existing appointment status"""
    appointment = APPOINTMENTS_DB["appointments"].get(int(appointment_id))
    if appointment:
        return {
            "found": True,
            "appointment": appointment,
            "status": appointment["status"],
            "message": f"Appointment {appointment_id} found for {appointment['patient_name']}"
        }
    return {
        "found": False,
        "error": f"Appointment {appointment_id} not found",
        "message": "Please check your appointment ID and try again"
    }

def handle_emergency(symptoms, severity, patient_location=""):
    """Handle emergency situations with immediate response"""
    emergency_id = ASSESSMENTS_DB["next_id"]
    ASSESSMENTS_DB["next_id"] += 1
    
    emergency = {
        "id": emergency_id,
        "type": "emergency",
        "symptoms": symptoms,
        "severity": severity,
        "location": patient_location,
        "action_required": "immediate_medical_attention",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    ASSESSMENTS_DB["assessments"][emergency_id] = emergency
    
    # Generate emergency response
    if severity.lower() == "critical" or "heart attack" in symptoms.lower():
        emergency_message = f"🚨 CRITICAL EMERGENCY ALERT 🚨\n\nPatient: {patient_location or 'Location not provided'}\nSymptoms: {symptoms}\nSeverity: {severity}\n\nIMMEDIATE ACTION REQUIRED:\n1. Call 108 (Emergency Services) immediately\n2. If patient is conscious, have them sit down and rest\n3. Do NOT give any medication unless prescribed\n4. Stay with the patient until emergency services arrive\n\nThis is a medical emergency requiring immediate professional intervention."
        priority = "critical"
    else:
        emergency_message = f"🚨 EMERGENCY ALERT 🚨\n\nPatient: {patient_location or 'Location not provided'}\nSymptoms: {symptoms}\nSeverity: {severity}\n\nIMMEDIATE ACTION REQUIRED:\n1. Call 108 (Emergency Services) immediately\n2. Go to the nearest hospital emergency room\n3. Do not delay seeking medical attention\n\nPlease seek immediate medical care for these symptoms."
        priority = "urgent"
    
    return {
        "emergency_id": emergency_id,
        "emergency": emergency,
        "message": emergency_message,
        "priority": priority,
        "immediate_actions": [
            "Call 108 (Emergency Services)",
            "Go to nearest hospital emergency room",
            "Do not delay seeking medical attention"
        ],
        "follow_up": "Emergency team has been alerted. Please seek immediate medical care."
    }

def get_patient_history(patient_name, phone_number):
    """Get patient's medical history and previous assessments"""
    # Find all assessments for this patient
    patient_assessments = []
    for assessment in ASSESSMENTS_DB["assessments"].values():
        # In a real system, you'd match by patient ID or phone number
        patient_assessments.append(assessment)
    
    # Find all appointments for this patient
    patient_appointments = []
    for appointment in APPOINTMENTS_DB["appointments"].values():
        if appointment["patient_name"].lower() == patient_name.lower():
            patient_appointments.append(appointment)
    
    return {
        "patient_name": patient_name,
        "phone_number": phone_number,
        "assessments": patient_assessments,
        "appointments": patient_appointments,
        "total_assessments": len(patient_assessments),
        "total_appointments": len(patient_appointments),
        "message": f"Retrieved medical history for {patient_name}"
    }

# Function mapping dictionary for Deepgram Agent API
FUNCTION_MAP = {
    'assess_chest_pain': assess_chest_pain,
    'assess_breathing': assess_breathing,
    'schedule_appointment': schedule_appointment,
    'check_appointment': check_appointment,
    'handle_emergency': handle_emergency,
    'get_patient_history': get_patient_history
}
