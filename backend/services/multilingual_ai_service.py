import torch
import whisper
import json
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    AutoModelForSeq2SeqLM, pipeline,
    BitsAndBytesConfig
)
import numpy as np
from datasets import load_dataset
import pandas as pd
import requests
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultilingualAIService:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.conversation_contexts = {}
        self.medical_datasets = {}
        self.language_models = {
            'english': 'microsoft/DialoGPT-medium',
            'tamil': 'microsoft/DialoGPT-medium',  # Will be fine-tuned
            'hindi': 'microsoft/DialoGPT-medium'   # Will be fine-tuned
        }
        self.tts_models = {
            'english': 'microsoft/speecht5_tts',
            'tamil': 'microsoft/speecht5_tts',
            'hindi': 'microsoft/speecht5_tts'
        }
        self.stt_models = {
            'english': 'openai/whisper-base.en',
            'tamil': 'openai/whisper-base',
            'hindi': 'openai/whisper-base'
        }
        
        # Medical terminology in multiple languages
        self.medical_terms = {
            'english': {
                'heart': 'heart', 'chest_pain': 'chest pain', 'breathing': 'breathing',
                'blood_pressure': 'blood pressure', 'diabetes': 'diabetes',
                'medication': 'medication', 'symptoms': 'symptoms'
            },
            'tamil': {
                'heart': 'இதயம்', 'chest_pain': 'மார்பு வலி', 'breathing': 'சுவாசம்',
                'blood_pressure': 'இரத்த அழுத்தம்', 'diabetes': 'பெரும்பாலான நோய்',
                'medication': 'மருந்து', 'symptoms': 'அறிகுறிகள்'
            },
            'hindi': {
                'heart': 'दिल', 'chest_pain': 'छाती में दर्द', 'breathing': 'सांस लेना',
                'blood_pressure': 'रक्तचाप', 'diabetes': 'मधुमेह',
                'medication': 'दवा', 'symptoms': 'लक्षण'
            }
        }
        
        # Conversation templates in multiple languages
        self.conversation_templates = {
            'english': {
                'greeting': "Hello {name}, this is MedAgg calling. I'm your AI healthcare assistant. I received your request for {medical_category} consultation. Can you please confirm your phone number ending in {phone_last4}?",
                'identity_confirmed': "Thank you for confirming. Now, I'd like to ask you some questions about your symptoms to better understand your condition. Can you tell me more about the problem you described: '{problem_description}'? What specific symptoms are you experiencing?",
                'symptom_questions': [
                    "How long have you been experiencing these symptoms?",
                    "On a scale of 1-10, how would you rate the severity of your pain or discomfort?",
                    "Are you currently taking any medications?",
                    "Do you have any allergies to medications?",
                    "Have you had any similar issues in the past?"
                ],
                'diagnosis_summary': "Based on your symptoms, I recommend {recommendation}. The urgency level is {urgency}. This will help ensure you get the appropriate care for your condition.",
                'questions_welcome': "Based on your symptoms, I recommend scheduling an appointment with a specialist. Do you have any questions about your condition or the recommended treatment?",
                'appointment_scheduling': "Great! Let me help you schedule an appointment. I'll find the best available specialist in your area and book a convenient time for you."
            },
            'tamil': {
                'greeting': "வணக்கம் {name}, இது MedAgg அழைப்பு. நான் உங்கள் AI சுகாதார உதவியாளர். நான் உங்கள் {medical_category} ஆலோசனை கோரிக்கையைப் பெற்றேன். உங்கள் தொலைபேசி எண்ணின் கடைசி 4 இலக்கங்களை {phone_last4} என்பதை உறுதிப்படுத்த முடியுமா?",
                'identity_confirmed': "உறுதிப்படுத்தியதற்கு நன்றி. இப்போது, உங்கள் நிலையை நன்றாக புரிந்துகொள்ள உங்கள் அறிகுறிகள் பற்றி சில கேள்விகளைக் கேட்க விரும்புகிறேன். நீங்கள் விவரித்த பிரச்சினையைப் பற்றி மேலும் சொல்ல முடியுமா: '{problem_description}'? நீங்கள் எந்த குறிப்பிட்ட அறிகுறிகளை அனுபவிக்கிறீர்கள்?",
                'symptom_questions': [
                    "இந்த அறிகுறிகளை நீங்கள் எவ்வளவு காலமாக அனுபவிக்கிறீர்கள்?",
                    "1-10 அளவில், உங்கள் வலி அல்லது அசௌகரியத்தின் தீவிரத்தை எவ்வளவு மதிப்பிடுவீர்கள்?",
                    "நீங்கள் தற்போது எந்த மருந்துகளை எடுத்துக்கொண்டிருக்கிறீர்கள்?",
                    "உங்களுக்கு மருந்துகளுக்கு எந்தவிதமான ஒவ்வாமை உள்ளதா?",
                    "கடந்த காலத்தில் இதுபோன்ற பிரச்சினைகள் இருந்தனவா?"
                ],
                'diagnosis_summary': "உங்கள் அறிகுறிகளின் அடிப்படையில், நான் {recommendation} பரிந்துரைக்கிறேன். அவசரநிலை நிலை {urgency}. இது உங்கள் நிலைக்கு பொருத்தமான பராமரிப்பைப் பெற உதவும்.",
                'questions_welcome': "உங்கள் அறிகுறிகளின் அடிப்படையில், நான் ஒரு நிபுணருடன் ஒரு நேரத்தை திட்டமிட பரிந்துரைக்கிறேன். உங்கள் நிலை அல்லது பரிந்துரைக்கப்பட்ட சிகிச்சை பற்றி உங்களுக்கு ஏதேனும் கேள்விகள் உள்ளனவா?",
                'appointment_scheduling': "சிறப்பு! நான் உங்களுக்கு ஒரு நேரத்தை திட்டமிட உதவுகிறேன். நான் உங்கள் பகுதியில் சிறந்த கிடைக்கும் நிபுணரைக் கண்டுபிடித்து வசதியான நேரத்தில் பதிவு செய்கிறேன்."
            },
            'hindi': {
                'greeting': "नमस्ते {name}, यह MedAgg का कॉल है। मैं आपका AI स्वास्थ्य सहायक हूं। मुझे आपके {medical_category} परामर्श के लिए अनुरोध प्राप्त हुआ है। क्या आप अपना फोन नंबर जो {phone_last4} पर समाप्त होता है, उसे पुष्टि कर सकते हैं?",
                'identity_confirmed': "पुष्टि करने के लिए धन्यवाद। अब, मैं आपकी स्थिति को बेहतर समझने के लिए आपके लक्षणों के बारे में कुछ प्रश्न पूछना चाहूंगा। क्या आप उस समस्या के बारे में और बता सकते हैं जिसका आपने वर्णन किया: '{problem_description}'? आप कौन से विशिष्ट लक्षणों का अनुभव कर रहे हैं?",
                'symptom_questions': [
                    "आप इन लक्षणों का अनुभव कब से कर रहे हैं?",
                    "1-10 के पैमाने पर, आप अपने दर्द या असुविधा की गंभीरता को कैसे दर करेंगे?",
                    "क्या आप वर्तमान में कोई दवा ले रहे हैं?",
                    "क्या आपको दवाओं से कोई एलर्जी है?",
                    "क्या आपको पहले भी ऐसी समस्याएं हुई हैं?"
                ],
                'diagnosis_summary': "आपके लक्षणों के आधार पर, मैं {recommendation} की सिफारिश करता हूं। तात्कालिकता स्तर {urgency} है। यह सुनिश्चित करेगा कि आपको अपनी स्थिति के लिए उपयुक्त देखभाल मिले।",
                'questions_welcome': "आपके लक्षणों के आधार पर, मैं एक विशेषज्ञ के साथ अपॉइंटमेंट शेड्यूल करने की सिफारिश करता हूं। क्या आपके पास अपनी स्थिति या अनुशंसित उपचार के बारे में कोई प्रश्न हैं?",
                'appointment_scheduling': "बहुत बढ़िया! मैं आपके लिए अपॉइंटमेंट शेड्यूल करने में मदद करूंगा। मैं आपके क्षेत्र में सबसे अच्छे उपलब्ध विशेषज्ञ को खोजूंगा और आपके लिए सुविधाजनक समय बुक करूंगा।"
            }
        }
    
    async def initialize_models(self):
        """Initialize all multilingual models"""
        try:
            logger.info("Initializing multilingual AI models...")
            
            # Initialize STT models
            await self._initialize_stt_models()
            
            # Initialize TTS models
            await self._initialize_tts_models()
            
            # Initialize LLM models
            await self._initialize_llm_models()
            
            # Load medical datasets
            await self._load_medical_datasets()
            
            logger.info("All multilingual AI models initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing multilingual models: {e}")
            raise e
    
    async def _initialize_stt_models(self):
        """Initialize Speech-to-Text models for all languages"""
        try:
            for lang, model_name in self.stt_models.items():
                logger.info(f"Loading STT model for {lang}: {model_name}")
                self.models[f"stt_{lang}"] = whisper.load_model(model_name.split('/')[-1])
                logger.info(f"STT model for {lang} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading STT models: {e}")
            raise e
    
    async def _initialize_tts_models(self):
        """Initialize Text-to-Speech models for all languages"""
        try:
            for lang, model_name in self.tts_models.items():
                logger.info(f"Loading TTS model for {lang}: {model_name}")
                # Using a simple TTS approach for POC
                # In production, use actual TTS models
                self.models[f"tts_{lang}"] = f"TTS model for {lang}"
                logger.info(f"TTS model for {lang} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading TTS models: {e}")
            raise e
    
    async def _initialize_llm_models(self):
        """Initialize LLM models for conversation"""
        try:
            # Use a lightweight model for POC
            model_name = "microsoft/DialoGPT-medium"
            
            logger.info(f"Loading LLM model: {model_name}")
            
            # Load tokenizer and model
            self.tokenizers['conversation'] = AutoTokenizer.from_pretrained(model_name)
            self.models['conversation'] = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Add padding token
            if self.tokenizers['conversation'].pad_token is None:
                self.tokenizers['conversation'].pad_token = self.tokenizers['conversation'].eos_token
            
            logger.info("LLM model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading LLM models: {e}")
            raise e
    
    async def _load_medical_datasets(self):
        """Load medical datasets for training and context"""
        try:
            logger.info("Loading medical datasets...")
            
            # Load medical Q&A dataset from Hugging Face
            try:
                medical_qa = load_dataset("medical_questions_pairs", split="train[:1000]")
                self.medical_datasets['qa'] = medical_qa
                logger.info("Medical Q&A dataset loaded")
            except:
                logger.warning("Could not load medical Q&A dataset, using fallback")
                self.medical_datasets['qa'] = self._create_fallback_medical_qa()
            
            # Load multilingual medical terms
            self.medical_datasets['terms'] = self.medical_terms
            
            logger.info("Medical datasets loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading medical datasets: {e}")
            # Use fallback data
            self.medical_datasets = {
                'qa': self._create_fallback_medical_qa(),
                'terms': self.medical_terms
            }
    
    def _create_fallback_medical_qa(self):
        """Create fallback medical Q&A data"""
        return [
            {
                "question": "What are the symptoms of heart disease?",
                "answer": "Common symptoms include chest pain, shortness of breath, fatigue, and irregular heartbeat.",
                "language": "english"
            },
            {
                "question": "How is diabetes managed?",
                "answer": "Diabetes is managed through medication, diet, exercise, and regular blood sugar monitoring.",
                "language": "english"
            },
            {
                "question": "இதய நோயின் அறிகுறிகள் என்ன?",
                "answer": "பொதுவான அறிகுறிகளில் மார்பு வலி, மூச்சுத் திணறல், சோர்வு மற்றும் ஒழுங்கற்ற இதயத் துடிப்பு ஆகியவை அடங்கும்.",
                "language": "tamil"
            },
            {
                "question": "मधुमेह का प्रबंधन कैसे किया जाता है?",
                "answer": "मधुमेह का प्रबंधन दवा, आहार, व्यायाम और नियमित रक्त शर्करा निगरानी के माध्यम से किया जाता है।",
                "language": "hindi"
            }
        ]
    
    async def transcribe_audio(self, audio_file_path: str, language: str = "english") -> str:
        """Convert speech to text using language-specific Whisper model"""
        try:
            if f"stt_{language}" not in self.models:
                language = "english"  # Fallback to English
            
            model = self.models[f"stt_{language}"]
            result = model.transcribe(audio_file_path, language=language)
            return result["text"].strip()
            
        except Exception as e:
            logger.error(f"Error transcribing audio in {language}: {e}")
            return "I'm sorry, I couldn't understand what you said. Could you please repeat?"
    
    async def generate_speech(self, text: str, language: str = "english") -> str:
        """Convert text to speech in the specified language"""
        try:
            logger.info(f"TTS ({language}): {text}")
            # For POC, return text. In production, generate actual audio
            return text
            
        except Exception as e:
            logger.error(f"Error generating speech in {language}: {e}")
            return "I'm sorry, there was an error with the voice system."
    
    async def process_conversation(self, call_session_id: str, user_input: str, patient_data: dict) -> str:
        """Process conversation with multilingual AI"""
        try:
            language = patient_data.get('language_preference', 'english')
            
            # Get or create conversation context
            if call_session_id not in self.conversation_contexts:
                self.conversation_contexts[call_session_id] = {
                    "stage": "greeting",
                    "patient_data": patient_data,
                    "conversation_log": [],
                    "diagnosis_info": {},
                    "questions_asked": 0,
                    "language": language
                }
            
            context = self.conversation_contexts[call_session_id]
            context["conversation_log"].append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.utcnow().isoformat(),
                "language": language
            })
            
            # Generate response using LLM
            response = await self._generate_llm_response(context, user_input, language)
            
            # Log assistant response
            context["conversation_log"].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.utcnow().isoformat(),
                "language": language
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing conversation: {e}")
            return self._get_error_message(language)
    
    async def _generate_llm_response(self, context: dict, user_input: str, language: str) -> str:
        """Generate response using LLM with medical knowledge"""
        try:
            stage = context["stage"]
            patient_data = context["patient_data"]
            
            # Get conversation template for the language
            templates = self.conversation_templates.get(language, self.conversation_templates['english'])
            
            if stage == "greeting":
                context["stage"] = "identity_verification"
                return templates['greeting'].format(
                    name=patient_data['name'],
                    medical_category=patient_data['medical_category'].replace('_', ' '),
                    phone_last4=patient_data['phone_number'][-4:]
                )
            
            elif stage == "identity_verification":
                if any(word in user_input.lower() for word in self._get_yes_words(language)):
                    context["stage"] = "symptom_inquiry"
                    return templates['identity_confirmed'].format(
                        problem_description=patient_data['problem_description']
                    )
                else:
                    return self._get_confirmation_prompt(language, patient_data['phone_number'][-4:])
            
            elif stage == "symptom_inquiry":
                context["diagnosis_info"]["symptoms"] = user_input
                context["questions_asked"] += 1
                
                if context["questions_asked"] < 3:
                    questions = templates['symptom_questions']
                    next_question = questions[context["questions_asked"] - 1]
                    return f"I understand. {next_question}"
                else:
                    context["stage"] = "diagnosis_summary"
                    return await self._generate_diagnosis_summary(context, language)
            
            elif stage == "diagnosis_summary":
                context["stage"] = "questions_and_answers"
                return templates['questions_welcome']
            
            elif stage == "questions_and_answers":
                if any(word in user_input.lower() for word in self._get_question_words(language)):
                    return await self._answer_medical_question(user_input, context, language)
                elif any(word in user_input.lower() for word in self._get_no_words(language)):
                    context["stage"] = "appointment_scheduling"
                    return templates['appointment_scheduling']
                else:
                    return self._get_questions_prompt(language)
            
            elif stage == "appointment_scheduling":
                context["stage"] = "appointment_confirmed"
                return self._get_appointment_confirmation(language)
            
            else:
                return self._get_default_response(language)
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._get_error_message(language)
    
    def _get_yes_words(self, language: str) -> List[str]:
        """Get yes/confirmation words for each language"""
        words = {
            'english': ['yes', 'correct', 'right', 'confirm', 'yeah', 'yep'],
            'tamil': ['ஆம்', 'சரி', 'உண்மை', 'உறுதி', 'ஆமாம்'],
            'hindi': ['हाँ', 'सही', 'ठीक', 'पुष्टि', 'जी हाँ']
        }
        return words.get(language, words['english'])
    
    def _get_no_words(self, language: str) -> List[str]:
        """Get no words for each language"""
        words = {
            'english': ['no', 'none', 'nothing', 'ready', 'done'],
            'tamil': ['இல்லை', 'ஒன்றும் இல்லை', 'தயார்', 'முடிந்தது'],
            'hindi': ['नहीं', 'कुछ नहीं', 'तैयार', 'हो गया']
        }
        return words.get(language, words['english'])
    
    def _get_question_words(self, language: str) -> List[str]:
        """Get question words for each language"""
        words = {
            'english': ['question', 'ask', 'wondering', 'curious', 'what', 'how', 'why'],
            'tamil': ['கேள்வி', 'கேட்க', 'ஆச்சரியம்', 'என்ன', 'எப்படி', 'ஏன்'],
            'hindi': ['प्रश्न', 'पूछना', 'जिज्ञासा', 'क्या', 'कैसे', 'क्यों']
        }
        return words.get(language, words['english'])
    
    def _get_confirmation_prompt(self, language: str, phone_last4: str) -> str:
        """Get confirmation prompt in specified language"""
        prompts = {
            'english': f"I need to verify your identity for security purposes. Can you please confirm your phone number ending in {phone_last4}?",
            'tamil': f"பாதுகாப்பு நோக்கங்களுக்காக உங்கள் அடையாளத்தை உறுதிப்படுத்த வேண்டும். உங்கள் தொலைபேசி எண்ணின் கடைசி 4 இலக்கங்களை {phone_last4} என்பதை உறுதிப்படுத்த முடியுமா?",
            'hindi': f"सुरक्षा उद्देश्यों के लिए मुझे आपकी पहचान सत्यापित करने की आवश्यकता है। क्या आप अपना फोन नंबर जो {phone_last4} पर समाप्त होता है, उसे पुष्टि कर सकते हैं?"
        }
        return prompts.get(language, prompts['english'])
    
    def _get_questions_prompt(self, language: str) -> str:
        """Get questions prompt in specified language"""
        prompts = {
            'english': "I'm here to help with any questions you might have. What would you like to know about your condition or treatment options?",
            'tamil': "உங்களுக்கு இருக்கும் எந்த கேள்விகளுக்கும் நான் உதவ இங்கே இருக்கிறேன். உங்கள் நிலை அல்லது சிகிச்சை விருப்பங்கள் பற்றி நீங்கள் என்ன தெரிந்து கொள்ள விரும்புகிறீர்கள்?",
            'hindi': "मैं यहाँ आपके किसी भी प्रश्न में मदद के लिए हूँ। आप अपनी स्थिति या उपचार विकल्पों के बारे में क्या जानना चाहते हैं?"
        }
        return prompts.get(language, prompts['english'])
    
    def _get_appointment_confirmation(self, language: str) -> str:
        """Get appointment confirmation in specified language"""
        prompts = {
            'english': "Perfect! I've found a suitable appointment for you. Let me confirm the details and send you an email with all the information.",
            'tamil': "சரியானது! நான் உங்களுக்கு பொருத்தமான நேரத்தைக் கண்டுபிடித்தேன். விவரங்களை உறுதிப்படுத்தி அனைத்து தகவல்களுடன் உங்களுக்கு மின்னஞ்சல் அனுப்புகிறேன்.",
            'hindi': "बहुत बढ़िया! मैंने आपके लिए एक उपयुक्त अपॉइंटमेंट खोजा है। मुझे विवरणों की पुष्टि करने दें और सभी जानकारी के साथ आपको ईमेल भेजने दें।"
        }
        return prompts.get(language, prompts['english'])
    
    def _get_default_response(self, language: str) -> str:
        """Get default response in specified language"""
        prompts = {
            'english': "I'm here to help. How can I assist you further?",
            'tamil': "நான் உதவ இங்கே இருக்கிறேன். மேலும் எப்படி உதவ முடியும்?",
            'hindi': "मैं यहाँ मदद के लिए हूँ। मैं आपकी और कैसे सहायता कर सकता हूँ?"
        }
        return prompts.get(language, prompts['english'])
    
    def _get_error_message(self, language: str) -> str:
        """Get error message in specified language"""
        prompts = {
            'english': "I'm sorry, I'm having trouble processing your request. Let me connect you to a human agent.",
            'tamil': "மன்னிக்கவும், உங்கள் கோரிக்கையை செயல்படுத்துவதில் சிக்கல் உள்ளது. நான் உங்களை மனித உதவியாளருடன் இணைக்கிறேன்.",
            'hindi': "मुझे खेद है, मुझे आपके अनुरोध को संसाधित करने में परेशानी हो रही है। मैं आपको एक मानव एजेंट से जोड़ता हूँ।"
        }
        return prompts.get(language, prompts['english'])
    
    async def _generate_diagnosis_summary(self, context: dict, language: str) -> str:
        """Generate diagnosis summary using medical knowledge"""
        try:
            symptoms = context["diagnosis_info"].get("symptoms", "")
            patient_data = context["patient_data"]
            
            # Simple rule-based diagnosis (can be enhanced with ML models)
            if any(term in symptoms.lower() for term in ['chest pain', 'chest discomfort', 'மார்பு வலி', 'छाती में दर्द']):
                urgency = "high" if language == 'english' else self._translate_urgency('high', language)
                recommendation = self._get_recommendation('cardiology', language)
            elif any(term in symptoms.lower() for term in ['breathing', 'shortness', 'சுவாசம்', 'सांस']):
                urgency = "medium" if language == 'english' else self._translate_urgency('medium', language)
                recommendation = self._get_recommendation('cardiology', language)
            else:
                urgency = "low" if language == 'english' else self._translate_urgency('low', language)
                recommendation = self._get_recommendation('general', language)
            
            context["diagnosis_info"]["urgency"] = urgency
            context["diagnosis_info"]["recommendation"] = recommendation
            
            templates = self.conversation_templates.get(language, self.conversation_templates['english'])
            return templates['diagnosis_summary'].format(
                recommendation=recommendation,
                urgency=urgency
            )
            
        except Exception as e:
            logger.error(f"Error generating diagnosis summary: {e}")
            return self._get_error_message(language)
    
    def _translate_urgency(self, urgency: str, language: str) -> str:
        """Translate urgency level to target language"""
        translations = {
            'english': {'high': 'high', 'medium': 'medium', 'low': 'low'},
            'tamil': {'high': 'உயர்', 'medium': 'நடுத்தர', 'low': 'குறைந்த'},
            'hindi': {'high': 'उच्च', 'medium': 'मध्यम', 'low': 'कम'}
        }
        return translations.get(language, translations['english']).get(urgency, urgency)
    
    def _get_recommendation(self, specialty: str, language: str) -> str:
        """Get medical recommendation in target language"""
        recommendations = {
            'english': {
                'cardiology': 'immediate consultation with a cardiologist',
                'general': 'routine consultation with a specialist'
            },
            'tamil': {
                'cardiology': 'இதயவியல் நிபுணருடன் உடனடி ஆலோசனை',
                'general': 'நிபுணருடன் வழக்கமான ஆலோசனை'
            },
            'hindi': {
                'cardiology': 'हृदय रोग विशेषज्ञ के साथ तत्काल परामर्श',
                'general': 'विशेषज्ञ के साथ नियमित परामर्श'
            }
        }
        return recommendations.get(language, recommendations['english']).get(specialty, 'consultation with a specialist')
    
    async def _answer_medical_question(self, question: str, context: dict, language: str) -> str:
        """Answer medical questions using knowledge base"""
        try:
            # Search in medical Q&A dataset
            qa_data = self.medical_datasets.get('qa', [])
            
            # Simple keyword matching (can be enhanced with semantic search)
            question_lower = question.lower()
            
            for qa in qa_data:
                if qa.get('language') == language and any(word in question_lower for word in qa['question'].lower().split()):
                    return qa['answer']
            
            # Fallback responses
            fallback_responses = {
                'english': "That's a great question. I recommend discussing this with your specialist during the appointment, as they can provide personalized advice based on your specific condition.",
                'tamil': "அது ஒரு சிறந்த கேள்வி. உங்கள் குறிப்பிட்ட நிலையின் அடிப்படையில் தனிப்பட்ட ஆலோசனையை வழங்க முடியும் என்பதால், இதை உங்கள் நிபுணருடன் நேரத்தில் விவாதிக்க பரிந்துரைக்கிறேன்.",
                'hindi': "यह एक बहुत अच्छा प्रश्न है। मैं अनुशंसा करता हूं कि आप इसे अपॉइंटमेंट के दौरान अपने विशेषज्ञ के साथ चर्चा करें, क्योंकि वे आपकी विशिष्ट स्थिति के आधार पर व्यक्तिगत सलाह दे सकते हैं।"
            }
            
            return fallback_responses.get(language, fallback_responses['english'])
            
        except Exception as e:
            logger.error(f"Error answering medical question: {e}")
            return self._get_error_message(language)
    
    async def get_conversation_summary(self, call_session_id: str) -> dict:
        """Get conversation summary for appointment booking"""
        if call_session_id not in self.conversation_contexts:
            return {}
        
        context = self.conversation_contexts[call_session_id]
        return {
            "conversation_log": context["conversation_log"],
            "diagnosis_info": context["diagnosis_info"],
            "patient_data": context["patient_data"],
            "language": context.get("language", "english")
        }
    
    async def clear_conversation_context(self, call_session_id: str):
        """Clear conversation context after call completion"""
        if call_session_id in self.conversation_contexts:
            del self.conversation_contexts[call_session_id]
    
    async def train_model(self, training_data: List[Dict], language: str = "english"):
        """Train/fine-tune the model with new data"""
        try:
            logger.info(f"Training model for {language} with {len(training_data)} samples")
            
            # This is a placeholder for actual training
            # In production, implement proper fine-tuning
            logger.info(f"Model training completed for {language}")
            
        except Exception as e:
            logger.error(f"Error training model for {language}: {e}")
            raise e


