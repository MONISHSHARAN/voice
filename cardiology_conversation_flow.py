#!/usr/bin/env python3
"""
Cardiology UFE Questionnaire Conversation Flow
Structured conversation for MedAgg Healthcare Voice Agent
"""

# Conversation Flow Configuration
CARDIO_CONVERSATION_FLOW = {
    "welcome": {
        "message": "Hello! Welcome to MedAgg Healthcare. I'm Dr. MedAgg, your AI cardiology specialist. I'm here to help you with your heart health concerns today. How are you feeling?",
        "next_step": "initial_assessment"
    },
    
    "initial_assessment": {
        "questions": [
            {
                "id": "q1_chest_pain",
                "question": "Do you experience any chest pain or discomfort? Please describe it if yes.",
                "follow_up": "chest_pain_details"
            },
            {
                "id": "q2_shortness_breath", 
                "question": "Do you have shortness of breath, especially during physical activity or when lying down?",
                "follow_up": "breathing_assessment"
            }
        ],
        "next_step": "detailed_assessment"
    },
    
    "chest_pain_details": {
        "questions": [
            {
                "id": "q3_pain_location",
                "question": "Where exactly do you feel the chest pain? Is it in the center, left side, or right side of your chest?",
                "follow_up": "pain_characteristics"
            },
            {
                "id": "q4_pain_duration",
                "question": "How long does the chest pain typically last? Is it constant or does it come and go?",
                "follow_up": "pain_triggers"
            }
        ],
        "next_step": "breathing_assessment"
    },
    
    "breathing_assessment": {
        "questions": [
            {
                "id": "q5_breathing_activity",
                "question": "Does the shortness of breath occur during rest, mild activity like walking, or only during strenuous exercise?",
                "follow_up": "breathing_timing"
            },
            {
                "id": "q6_breathing_position",
                "question": "Do you need to sleep with extra pillows or sit up to breathe comfortably?",
                "follow_up": "appointment_consideration"
            }
        ],
        "next_step": "appointment_consideration"
    },
    
    "appointment_consideration": {
        "message": "Based on your responses, I'd like to schedule a cardiology consultation for you. This will help us better assess your heart health.",
        "questions": [
            {
                "id": "q7_appointment_preference",
                "question": "Would you like to schedule an appointment? I can book you for a cardiology consultation.",
                "follow_up": "appointment_booking"
            }
        ],
        "next_step": "appointment_booking"
    },
    
    "appointment_booking": {
        "questions": [
            {
                "id": "q8_urgency_level",
                "question": "How urgent do you feel this is? Would you say it's low priority, medium priority, or high priority?",
                "follow_up": "appointment_confirmation"
            },
            {
                "id": "q9_preferred_time",
                "question": "Do you have any preferred time for the appointment - morning, afternoon, or evening?",
                "follow_up": "appointment_confirmation"
            }
        ],
        "next_step": "appointment_confirmation"
    },
    
    "appointment_confirmation": {
        "message": "Perfect! I've noted your preferences. Let me book your cardiology appointment now.",
        "next_step": "live_agent_offer"
    },
    
    "live_agent_offer": {
        "message": "Your appointment has been scheduled. Would you like to speak with a live cardiology specialist right now for immediate consultation, or are you satisfied with the appointment booking?",
        "questions": [
            {
                "id": "q10_live_agent",
                "question": "Should I connect you with a live cardiology specialist now?",
                "follow_up": "conversation_end"
            }
        ],
        "next_step": "conversation_end"
    },
    
    "conversation_end": {
        "message": "Thank you for using MedAgg Healthcare. Your cardiology consultation has been scheduled, and we'll contact you with the details. Take care of your heart health!",
        "next_step": "end"
    }
}

# Response patterns for different answers
RESPONSE_PATTERNS = {
    "chest_pain_yes": [
        "I understand you're experiencing chest pain. This is important to address.",
        "Chest pain can be a significant symptom. Let me ask you some specific questions.",
        "Thank you for sharing that. Chest pain requires careful evaluation."
    ],
    "chest_pain_no": [
        "That's good to hear you're not experiencing chest pain.",
        "I'm glad you're not having chest pain issues.",
        "Good, no chest pain is a positive sign."
    ],
    "shortness_breath_yes": [
        "Shortness of breath is another important symptom to evaluate.",
        "I need to understand more about your breathing difficulties.",
        "Breathing issues can be related to heart health. Let me ask some questions."
    ],
    "shortness_breath_no": [
        "That's reassuring that you're not having breathing difficulties.",
        "Good, no breathing problems is positive.",
        "I'm glad your breathing is normal."
    ],
    "appointment_yes": [
        "Excellent! I'll help you schedule a cardiology consultation.",
        "Great! Let me book your appointment right away.",
        "Perfect! I'll arrange your cardiology appointment."
    ],
    "appointment_no": [
        "I understand. You can always call back to schedule when you're ready.",
        "No problem. Feel free to contact us anytime for scheduling.",
        "That's fine. We're here whenever you need us."
    ],
    "live_agent_yes": [
        "I'll connect you with a live cardiology specialist right now.",
        "Perfect! Let me transfer you to our cardiology team.",
        "Great! I'm connecting you with a live specialist now."
    ],
    "live_agent_no": [
        "Understood. Your appointment is confirmed and we'll be in touch.",
        "No problem. Your appointment details will be sent to you.",
        "Perfect. We'll contact you with your appointment information."
    ]
}

# Emergency keywords that should trigger immediate action
EMERGENCY_KEYWORDS = [
    "severe chest pain", "crushing pain", "heart attack", "can't breathe",
    "emergency", "urgent", "immediate", "severe", "intense pain"
]

def get_conversation_flow():
    """Return the conversation flow configuration"""
    return CARDIO_CONVERSATION_FLOW

def get_response_patterns():
    """Return response patterns for different answers"""
    return RESPONSE_PATTERNS

def get_emergency_keywords():
    """Return emergency keywords that need immediate attention"""
    return EMERGENCY_KEYWORDS

def is_emergency_response(text):
    """Check if the response contains emergency keywords"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in EMERGENCY_KEYWORDS)

def get_appropriate_response(response_type, user_answer=""):
    """Get appropriate response based on user answer"""
    patterns = RESPONSE_PATTERNS.get(response_type, [])
    if patterns:
        import random
        return random.choice(patterns)
    return "Thank you for that information. Let me continue with the next question."
