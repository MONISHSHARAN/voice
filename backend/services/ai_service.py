import torch
import whisper
import json
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import logging
from .multilingual_ai_service import MultilingualAIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.multilingual_ai = MultilingualAIService()
        self.conversation_contexts = {}
        
    async def initialize_models(self):
        """Initialize AI models"""
        try:
            # Initialize multilingual AI service
            await self.multilingual_ai.initialize_models()
            logger.info("All AI models loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")
            raise e
    
    async def transcribe_audio(self, audio_file_path: str, language: str = "english") -> str:
        """Convert speech to text using Whisper"""
        try:
            return await self.multilingual_ai.transcribe_audio(audio_file_path, language)
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return "I'm sorry, I couldn't understand what you said. Could you please repeat?"
    
    async def generate_speech(self, text: str, language: str = "english") -> str:
        """Convert text to speech"""
        try:
            return await self.multilingual_ai.generate_speech(text, language)
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return "I'm sorry, there was an error with the voice system."
    
    async def process_conversation(self, call_session_id: str, user_input: str, patient_data: dict) -> str:
        """Process conversation with the AI bot"""
        try:
            return await self.multilingual_ai.process_conversation(call_session_id, user_input, patient_data)
            
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            return "I'm sorry, I'm having trouble processing your request. Let me connect you to a human agent."
    
    async def _generate_response(self, context: dict, user_input: str) -> str:
        """Generate AI response based on conversation context"""
        stage = context["stage"]
        patient_data = context["patient_data"]
        user_input_lower = user_input.lower()
        
        if stage == "greeting":
            context["stage"] = "identity_verification"
            return f"Hello {patient_data['name']}, this is MedAgg calling. I'm your AI healthcare assistant. I received your request for {patient_data['medical_category'].replace('_', ' ')} consultation. Can you please confirm your phone number ending in {patient_data['phone_number'][-4:]}?"
        
        elif stage == "identity_verification":
            if any(word in user_input_lower for word in ["yes", "correct", "right", "confirm"]):
                context["stage"] = "symptom_inquiry"
                return "Thank you for confirming. Now, I'd like to ask you some questions about your symptoms to better understand your condition. Can you tell me more about the problem you described: '{patient_data['problem_description']}'? What specific symptoms are you experiencing?"
            else:
                return "I need to verify your identity for security purposes. Can you please confirm your phone number ending in {patient_data['phone_number'][-4:]}?"
        
        elif stage == "symptom_inquiry":
            context["diagnosis_info"]["symptoms"] = user_input
            context["questions_asked"] += 1
            
            if context["questions_asked"] < 3:
                questions = [
                    "How long have you been experiencing these symptoms?",
                    "On a scale of 1-10, how would you rate the severity of your pain or discomfort?",
                    "Are you currently taking any medications?",
                    "Do you have any allergies to medications?",
                    "Have you had any similar issues in the past?"
                ]
                next_question = questions[context["questions_asked"] - 1]
                return f"I understand. {next_question}"
            else:
                context["stage"] = "diagnosis_summary"
                return await self._generate_diagnosis_summary(context)
        
        elif stage == "diagnosis_summary":
            context["stage"] = "questions_and_answers"
            return "Based on your symptoms, I recommend scheduling an appointment with a specialist. Do you have any questions about your condition or the recommended treatment?"
        
        elif stage == "questions_and_answers":
            if any(word in user_input_lower for word in ["question", "ask", "wondering", "curious"]):
                return await self._answer_medical_question(user_input, context)
            elif any(word in user_input_lower for word in ["no", "none", "nothing", "ready"]):
                context["stage"] = "appointment_scheduling"
                return "Great! Let me help you schedule an appointment. I'll find the best available specialist in your area and book a convenient time for you."
            else:
                return "I'm here to help with any questions you might have. What would you like to know about your condition or treatment options?"
        
        elif stage == "appointment_scheduling":
            context["stage"] = "appointment_confirmed"
            return "Perfect! I've found a suitable appointment for you. Let me confirm the details and send you an email with all the information."
        
        else:
            return "I'm here to help. How can I assist you further?"
    
    async def _generate_diagnosis_summary(self, context: dict) -> str:
        """Generate a diagnosis summary based on symptoms"""
        symptoms = context["diagnosis_info"].get("symptoms", "")
        patient_data = context["patient_data"]
        
        # Simple rule-based diagnosis (in production, use a proper medical AI)
        if "chest pain" in symptoms.lower() or "chest discomfort" in symptoms.lower():
            urgency = "high"
            recommendation = "immediate consultation with a cardiologist"
        elif "shortness of breath" in symptoms.lower() or "breathing" in symptoms.lower():
            urgency = "medium"
            recommendation = "consultation with a cardiologist within a week"
        else:
            urgency = "low"
            recommendation = "routine consultation with a specialist"
        
        context["diagnosis_info"]["urgency"] = urgency
        context["diagnosis_info"]["recommendation"] = recommendation
        
        return f"Based on your symptoms, I recommend {recommendation}. The urgency level is {urgency}. This will help ensure you get the appropriate care for your condition."
    
    async def _answer_medical_question(self, question: str, context: dict) -> str:
        """Answer medical questions (simplified for POC)"""
        question_lower = question.lower()
        
        # Simple Q&A responses (in production, use a medical knowledge base)
        if "what" in question_lower and "expect" in question_lower:
            return "During your consultation, the specialist will review your symptoms, perform a physical examination, and may recommend additional tests like an ECG or echocardiogram to determine the best treatment plan for you."
        
        elif "how long" in question_lower:
            return "The consultation typically takes 30-45 minutes. The specialist will thoroughly evaluate your condition and discuss treatment options with you."
        
        elif "cost" in question_lower or "price" in question_lower:
            return "The cost will depend on your insurance coverage and the specific tests required. Our staff will help you understand the costs before your appointment."
        
        elif "preparation" in question_lower:
            return "Please bring a list of your current medications, any previous test results, and arrive 15 minutes early to complete any necessary paperwork."
        
        else:
            return "That's a great question. I recommend discussing this with your specialist during the appointment, as they can provide personalized advice based on your specific condition."
    
    async def get_conversation_summary(self, call_session_id: str) -> dict:
        """Get conversation summary for appointment booking"""
        if call_session_id not in self.conversation_contexts:
            return {}
        
        context = self.conversation_contexts[call_session_id]
        return {
            "conversation_log": context["conversation_log"],
            "diagnosis_info": context["diagnosis_info"],
            "patient_data": context["patient_data"]
        }
    
    async def clear_conversation_context(self, call_session_id: str):
        """Clear conversation context after call completion"""
        if call_session_id in self.conversation_contexts:
            del self.conversation_contexts[call_session_id]
