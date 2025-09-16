#!/usr/bin/env python3
"""
Medical Data Collection Script for MedAgg Healthcare
This script collects medical data from various sources including Kaggle, Hugging Face, and other open sources
"""

import asyncio
import json
import logging
import requests
import pandas as pd
from datasets import load_dataset
import os
from typing import List, Dict, Optional
import zipfile
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalDataCollector:
    def __init__(self):
        self.collected_data = {
            'english': [],
            'tamil': [],
            'hindi': []
        }
        self.kaggle_datasets = [
            "medical-questions-pairs",
            "medical-transcription",
            "medical-qa",
            "healthcare-dataset"
        ]
        
    async def collect_all_data(self):
        """Collect medical data from all sources"""
        try:
            logger.info("Starting medical data collection...")
            
            # Collect from Hugging Face
            await self._collect_from_huggingface()
            
            # Collect from Kaggle (simulated for POC)
            await self._collect_from_kaggle()
            
            # Collect synthetic multilingual data
            await self._collect_synthetic_data()
            
            # Save collected data
            await self._save_collected_data()
            
            logger.info("Medical data collection completed successfully!")
            
        except Exception as e:
            logger.error(f"Error collecting medical data: {e}")
            raise e
    
    async def _collect_from_huggingface(self):
        """Collect medical data from Hugging Face datasets"""
        try:
            logger.info("Collecting data from Hugging Face...")
            
            # Medical Q&A dataset
            try:
                medical_qa = load_dataset("medical_questions_pairs", split="train[:1000]")
                for item in medical_qa:
                    self.collected_data['english'].append({
                        "type": "qa",
                        "question": item.get("question", ""),
                        "answer": item.get("answer", ""),
                        "category": item.get("category", "general"),
                        "source": "huggingface_medical_qa"
                    })
                logger.info(f"Collected {len(medical_qa)} Q&A pairs from Hugging Face")
            except Exception as e:
                logger.warning(f"Could not load medical Q&A dataset: {e}")
            
            # Medical conversations dataset
            try:
                medical_conv = load_dataset("medical_conversations", split="train[:500]")
                for item in medical_conv:
                    self.collected_data['english'].append({
                        "type": "conversation",
                        "context": item.get("context", ""),
                        "conversation": item.get("conversation", []),
                        "source": "huggingface_medical_conversations"
                    })
                logger.info(f"Collected {len(medical_conv)} conversations from Hugging Face")
            except Exception as e:
                logger.warning(f"Could not load medical conversations dataset: {e}")
            
        except Exception as e:
            logger.error(f"Error collecting from Hugging Face: {e}")
    
    async def _collect_from_kaggle(self):
        """Collect medical data from Kaggle datasets (simulated for POC)"""
        try:
            logger.info("Collecting data from Kaggle (simulated)...")
            
            # Simulate Kaggle data collection
            kaggle_data = self._create_simulated_kaggle_data()
            
            for item in kaggle_data:
                self.collected_data['english'].append(item)
            
            logger.info(f"Collected {len(kaggle_data)} items from Kaggle (simulated)")
            
        except Exception as e:
            logger.error(f"Error collecting from Kaggle: {e}")
    
    def _create_simulated_kaggle_data(self) -> List[Dict]:
        """Create simulated Kaggle medical data"""
        return [
            {
                "type": "qa",
                "question": "What are the early signs of diabetes?",
                "answer": "Early signs include increased thirst, frequent urination, fatigue, blurred vision, and slow-healing sores.",
                "category": "endocrinology",
                "source": "kaggle_diabetes_dataset"
            },
            {
                "type": "qa",
                "question": "How can I prevent heart disease?",
                "answer": "Prevent heart disease by maintaining a healthy diet, regular exercise, avoiding smoking, managing stress, and regular health checkups.",
                "category": "cardiology",
                "source": "kaggle_heart_disease_dataset"
            },
            {
                "type": "conversation",
                "context": "Patient consultation about blood pressure",
                "conversation": [
                    {"role": "patient", "content": "My blood pressure has been high lately"},
                    {"role": "doctor", "content": "Let's discuss your lifestyle and medication to help manage your blood pressure effectively."}
                ],
                "source": "kaggle_blood_pressure_dataset"
            },
            {
                "type": "symptom",
                "symptom": "chest pain",
                "description": "Sharp pain in the center of the chest that may radiate to the arm or jaw",
                "possible_causes": ["heart attack", "angina", "muscle strain", "acid reflux"],
                "urgency": "high",
                "source": "kaggle_symptoms_dataset"
            }
        ]
    
    async def _collect_synthetic_data(self):
        """Collect synthetic multilingual medical data"""
        try:
            logger.info("Collecting synthetic multilingual data...")
            
            # English data
            english_data = self._create_english_medical_data()
            self.collected_data['english'].extend(english_data)
            
            # Tamil data
            tamil_data = self._create_tamil_medical_data()
            self.collected_data['tamil'].extend(tamil_data)
            
            # Hindi data
            hindi_data = self._create_hindi_medical_data()
            self.collected_data['hindi'].extend(hindi_data)
            
            logger.info("Synthetic multilingual data collected successfully")
            
        except Exception as e:
            logger.error(f"Error collecting synthetic data: {e}")
    
    def _create_english_medical_data(self) -> List[Dict]:
        """Create English medical data"""
        return [
            {
                "type": "qa",
                "question": "What should I do if I experience chest pain?",
                "answer": "If you experience chest pain, especially if it's severe, crushing, or accompanied by shortness of breath, seek immediate medical attention. Call emergency services or go to the nearest hospital.",
                "category": "cardiology",
                "source": "synthetic_english"
            },
            {
                "type": "conversation",
                "context": "Patient calls about medication side effects",
                "conversation": [
                    {"role": "patient", "content": "I'm experiencing side effects from my medication"},
                    {"role": "assistant", "content": "I understand you're having side effects. Can you describe what symptoms you're experiencing? This will help me provide appropriate guidance."}
                ],
                "source": "synthetic_english"
            },
            {
                "type": "symptom_analysis",
                "symptoms": ["chest pain", "shortness of breath", "fatigue"],
                "analysis": "These symptoms may indicate a cardiovascular condition and require immediate medical evaluation.",
                "recommendation": "Schedule an appointment with a cardiologist as soon as possible.",
                "urgency": "high",
                "source": "synthetic_english"
            }
        ]
    
    def _create_tamil_medical_data(self) -> List[Dict]:
        """Create Tamil medical data"""
        return [
            {
                "type": "qa",
                "question": "மார்பு வலி இருந்தால் நான் என்ன செய்ய வேண்டும்?",
                "answer": "மார்பு வலி இருந்தால், குறிப்பாக அது கடுமையானது, நெருக்கமானது அல்லது மூச்சுத் திணறலுடன் இருந்தால், உடனடி மருத்துவ உதவியை நாடுங்கள். அவசர சேவைகளை அழைக்கவும் அல்லது அருகிலுள்ள மருத்துவமனைக்குச் செல்லுங்கள்.",
                "category": "cardiology",
                "source": "synthetic_tamil"
            },
            {
                "type": "conversation",
                "context": "மருந்து பக்க விளைவுகள் பற்றி நோயாளி அழைப்பு",
                "conversation": [
                    {"role": "patient", "content": "என் மருந்தில் பக்க விளைவுகள் ஏற்படுகின்றன"},
                    {"role": "assistant", "content": "நீங்கள் பக்க விளைவுகளை அனுபவிக்கிறீர்கள் என்பதை புரிந்துகொள்கிறேன். நீங்கள் எந்த அறிகுறிகளை அனுபவிக்கிறீர்கள் என்பதை விவரிக்க முடியுமா? இது பொருத்தமான வழிகாட்டுதலை வழங்க உதவும்."}
                ],
                "source": "synthetic_tamil"
            },
            {
                "type": "symptom_analysis",
                "symptoms": ["மார்பு வலி", "மூச்சுத் திணறல்", "சோர்வு"],
                "analysis": "இந்த அறிகுறிகள் இதய நோயைக் குறிக்கலாம் மற்றும் உடனடி மருத்துவ மதிப்பீடு தேவை.",
                "recommendation": "முடிந்தவரை விரைவில் இதயவியல் நிபுணருடன் ஒரு நேரத்தை திட்டமிடுங்கள்.",
                "urgency": "high",
                "source": "synthetic_tamil"
            }
        ]
    
    def _create_hindi_medical_data(self) -> List[Dict]:
        """Create Hindi medical data"""
        return [
            {
                "type": "qa",
                "question": "अगर मुझे छाती में दर्द है तो मुझे क्या करना चाहिए?",
                "answer": "अगर आपको छाती में दर्द है, खासकर अगर यह गंभीर है, दबाने वाला है या सांस की तकलीफ के साथ है, तो तुरंत चिकित्सा सहायता लें। आपातकालीन सेवाओं को कॉल करें या निकटतम अस्पताल जाएं।",
                "category": "cardiology",
                "source": "synthetic_hindi"
            },
            {
                "type": "conversation",
                "context": "दवा के दुष्प्रभावों के बारे में रोगी का कॉल",
                "conversation": [
                    {"role": "patient", "content": "मुझे अपनी दवा से दुष्प्रभाव हो रहे हैं"},
                    {"role": "assistant", "content": "मैं समझता हूं कि आपको दुष्प्रभाव हो रहे हैं। क्या आप बता सकते हैं कि आप कौन से लक्षण अनुभव कर रहे हैं? यह उपयुक्त मार्गदर्शन प्रदान करने में मदद करेगा।"}
                ],
                "source": "synthetic_hindi"
            },
            {
                "type": "symptom_analysis",
                "symptoms": ["छाती में दर्द", "सांस की तकलीफ", "थकान"],
                "analysis": "ये लक्षण हृदय संबंधी स्थिति का संकेत दे सकते हैं और तत्काल चिकित्सा मूल्यांकन की आवश्यकता है।",
                "recommendation": "जितनी जल्दी हो सके हृदय रोग विशेषज्ञ के साथ अपॉइंटमेंट शेड्यूल करें।",
                "urgency": "high",
                "source": "synthetic_hindi"
            }
        ]
    
    async def _save_collected_data(self):
        """Save collected data to files"""
        try:
            logger.info("Saving collected data...")
            
            # Create data directory
            os.makedirs("./data", exist_ok=True)
            
            # Save data for each language
            for language, data in self.collected_data.items():
                filename = f"./data/medical_data_{language}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved {len(data)} items for {language} to {filename}")
            
            # Save combined data
            combined_filename = "./data/medical_data_combined.json"
            with open(combined_filename, 'w', encoding='utf-8') as f:
                json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved combined data to {combined_filename}")
            
            # Create summary
            summary = {
                "total_items": sum(len(data) for data in self.collected_data.values()),
                "items_by_language": {lang: len(data) for lang, data in self.collected_data.items()},
                "data_types": self._get_data_type_summary(),
                "collection_date": str(pd.Timestamp.now()),
                "sources": self._get_source_summary()
            }
            
            with open("./data/collection_summary.json", 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info("Saved collection summary")
            
        except Exception as e:
            logger.error(f"Error saving collected data: {e}")
            raise e
    
    def _get_data_type_summary(self) -> Dict:
        """Get summary of data types collected"""
        data_types = {}
        for language, data in self.collected_data.items():
            data_types[language] = {}
            for item in data:
                item_type = item.get('type', 'unknown')
                data_types[language][item_type] = data_types[language].get(item_type, 0) + 1
        return data_types
    
    def _get_source_summary(self) -> Dict:
        """Get summary of data sources"""
        sources = {}
        for language, data in self.collected_data.items():
            sources[language] = {}
            for item in data:
                source = item.get('source', 'unknown')
                sources[language][source] = sources[language].get(source, 0) + 1
        return sources
    
    async def create_training_dataset(self):
        """Create formatted training dataset from collected data"""
        try:
            logger.info("Creating training dataset...")
            
            training_data = {
                'english': [],
                'tamil': [],
                'hindi': []
            }
            
            for language, data in self.collected_data.items():
                for item in data:
                    if item['type'] == 'qa':
                        training_data[language].append({
                            "prompt": f"Q: {item['question']}",
                            "completion": f"A: {item['answer']}",
                            "category": item.get('category', 'general')
                        })
                    elif item['type'] == 'conversation':
                        conversation_text = ""
                        for turn in item.get('conversation', []):
                            conversation_text += f"{turn['role']}: {turn['content']}\n"
                        training_data[language].append({
                            "prompt": item.get('context', ''),
                            "completion": conversation_text.strip(),
                            "category": "conversation"
                        })
            
            # Save training dataset
            for language, data in training_data.items():
                filename = f"./data/training_data_{language}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved training data for {language}: {len(data)} items")
            
            logger.info("Training dataset created successfully")
            
        except Exception as e:
            logger.error(f"Error creating training dataset: {e}")
            raise e

async def main():
    """Main data collection function"""
    try:
        logger.info("Starting Medical Data Collection for MedAgg Healthcare")
        
        collector = MedicalDataCollector()
        
        # Collect all data
        await collector.collect_all_data()
        
        # Create training dataset
        await collector.create_training_dataset()
        
        logger.info("Medical data collection completed successfully!")
        
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(main())


