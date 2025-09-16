#!/usr/bin/env python3
"""
Multilingual AI Training Script for MedAgg Healthcare
This script trains and fine-tunes the multilingual AI models using medical datasets
"""

import asyncio
import json
import logging
from typing import List, Dict
import pandas as pd
from datasets import load_dataset, Dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
import torch
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultilingualAITrainer:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.training_data = {}
        
    async def load_medical_datasets(self):
        """Load medical datasets from various sources"""
        try:
            logger.info("Loading medical datasets...")
            
            # Load from Hugging Face datasets
            try:
                # Medical Q&A dataset
                medical_qa = load_dataset("medical_questions_pairs", split="train[:5000]")
                self.training_data['medical_qa'] = medical_qa
                logger.info("Loaded medical Q&A dataset from Hugging Face")
            except Exception as e:
                logger.warning(f"Could not load medical Q&A dataset: {e}")
                self.training_data['medical_qa'] = self._create_synthetic_medical_qa()
            
            # Load multilingual medical conversations
            self.training_data['conversations'] = self._create_multilingual_conversations()
            
            # Load medical terminology
            self.training_data['terminology'] = self._create_medical_terminology()
            
            logger.info("All medical datasets loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading medical datasets: {e}")
            raise e
    
    def _create_synthetic_medical_qa(self) -> List[Dict]:
        """Create synthetic medical Q&A data for training"""
        return [
            {
                "question": "What are the symptoms of heart disease?",
                "answer": "Common symptoms include chest pain, shortness of breath, fatigue, and irregular heartbeat.",
                "language": "english",
                "category": "cardiology"
            },
            {
                "question": "How is diabetes managed?",
                "answer": "Diabetes is managed through medication, diet, exercise, and regular blood sugar monitoring.",
                "language": "english",
                "category": "endocrinology"
            },
            {
                "question": "What causes high blood pressure?",
                "answer": "High blood pressure can be caused by genetics, diet, lack of exercise, stress, and certain medical conditions.",
                "language": "english",
                "category": "cardiology"
            },
            {
                "question": "இதய நோயின் அறிகுறிகள் என்ன?",
                "answer": "பொதுவான அறிகுறிகளில் மார்பு வலி, மூச்சுத் திணறல், சோர்வு மற்றும் ஒழுங்கற்ற இதயத் துடிப்பு ஆகியவை அடங்கும்.",
                "language": "tamil",
                "category": "cardiology"
            },
            {
                "question": "மதுநீரிழிவு எவ்வாறு நிர்வகிக்கப்படுகிறது?",
                "answer": "மதுநீரிழிவு மருந்து, உணவு, உடற்பயிற்சி மற்றும் வழக்கமான இரத்த சர்க்கரை கண்காணிப்பு மூலம் நிர்வகிக்கப்படுகிறது.",
                "language": "tamil",
                "category": "endocrinology"
            },
            {
                "question": "मधुमेह का प्रबंधन कैसे किया जाता है?",
                "answer": "मधुमेह का प्रबंधन दवा, आहार, व्यायाम और नियमित रक्त शर्करा निगरानी के माध्यम से किया जाता है।",
                "language": "hindi",
                "category": "endocrinology"
            },
            {
                "question": "उच्च रक्तचाप का कारण क्या है?",
                "answer": "उच्च रक्तचाप आनुवंशिकता, आहार, व्यायाम की कमी, तनाव और कुछ चिकित्सा स्थितियों के कारण हो सकता है।",
                "language": "hindi",
                "category": "cardiology"
            }
        ]
    
    def _create_multilingual_conversations(self) -> List[Dict]:
        """Create multilingual conversation data for training"""
        return [
            {
                "context": "Patient calls about chest pain",
                "conversation": [
                    {"role": "user", "content": "I have chest pain", "language": "english"},
                    {"role": "assistant", "content": "I understand you're experiencing chest pain. Can you describe the pain in more detail? Is it sharp, dull, or burning?", "language": "english"}
                ],
                "language": "english"
            },
            {
                "context": "Patient calls about chest pain in Tamil",
                "conversation": [
                    {"role": "user", "content": "எனக்கு மார்பு வலி இருக்கிறது", "language": "tamil"},
                    {"role": "assistant", "content": "உங்களுக்கு மார்பு வலி இருக்கிறது என்பதை புரிந்துகொள்கிறேன். வலியை மேலும் விரிவாக விவரிக்க முடியுமா? அது கூர்மையானது, மந்தமானது அல்லது எரியும் வகையானதா?", "language": "tamil"}
                ],
                "language": "tamil"
            },
            {
                "context": "Patient calls about chest pain in Hindi",
                "conversation": [
                    {"role": "user", "content": "मुझे छाती में दर्द है", "language": "hindi"},
                    {"role": "assistant", "content": "मैं समझता हूं कि आपको छाती में दर्द हो रहा है। क्या आप दर्द को और विस्तार से बता सकते हैं? क्या यह तेज, सुस्त या जलन वाला है?", "language": "hindi"}
                ],
                "language": "hindi"
            }
        ]
    
    def _create_medical_terminology(self) -> Dict:
        """Create medical terminology in multiple languages"""
        return {
            "english": {
                "heart": "heart", "chest_pain": "chest pain", "breathing": "breathing",
                "blood_pressure": "blood pressure", "diabetes": "diabetes",
                "medication": "medication", "symptoms": "symptoms",
                "appointment": "appointment", "doctor": "doctor", "hospital": "hospital"
            },
            "tamil": {
                "heart": "இதயம்", "chest_pain": "மார்பு வலி", "breathing": "சுவாசம்",
                "blood_pressure": "இரத்த அழுத்தம்", "diabetes": "மதுநீரிழிவு",
                "medication": "மருந்து", "symptoms": "அறிகுறிகள்",
                "appointment": "நேரம்", "doctor": "மருத்துவர்", "hospital": "மருத்துவமனை"
            },
            "hindi": {
                "heart": "दिल", "chest_pain": "छाती में दर्द", "breathing": "सांस लेना",
                "blood_pressure": "रक्तचाप", "diabetes": "मधुमेह",
                "medication": "दवा", "symptoms": "लक्षण",
                "appointment": "अपॉइंटमेंट", "doctor": "डॉक्टर", "hospital": "अस्पताल"
            }
        }
    
    async def prepare_training_data(self):
        """Prepare training data for each language"""
        try:
            logger.info("Preparing training data...")
            
            for language in ['english', 'tamil', 'hindi']:
                self.training_data[f'{language}_formatted'] = self._format_data_for_language(language)
                logger.info(f"Prepared training data for {language}")
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise e
    
    def _format_data_for_language(self, language: str) -> List[str]:
        """Format data for specific language training"""
        formatted_data = []
        
        # Add Q&A data
        for qa in self.training_data['medical_qa']:
            if qa.get('language') == language:
                formatted_data.append(f"Q: {qa['question']}\nA: {qa['answer']}")
        
        # Add conversation data
        for conv in self.training_data['conversations']:
            if conv['language'] == language:
                conversation_text = ""
                for turn in conv['conversation']:
                    if turn['language'] == language:
                        conversation_text += f"{turn['role']}: {turn['content']}\n"
                formatted_data.append(conversation_text)
        
        return formatted_data
    
    async def train_models(self):
        """Train models for each language"""
        try:
            logger.info("Starting model training...")
            
            for language in ['english', 'tamil', 'hindi']:
                logger.info(f"Training model for {language}...")
                await self._train_language_model(language)
                logger.info(f"Completed training for {language}")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise e
    
    async def _train_language_model(self, language: str):
        """Train model for specific language"""
        try:
            # Use a lightweight model for POC
            model_name = "microsoft/DialoGPT-medium"
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Add padding token
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Prepare training data
            training_texts = self.training_data[f'{language}_formatted']
            
            # Tokenize data
            def tokenize_function(examples):
                return tokenizer(examples, truncation=True, padding=True, max_length=512)
            
            # Create dataset
            dataset = Dataset.from_dict({"text": training_texts})
            tokenized_dataset = dataset.map(tokenize_function, batched=True)
            
            # Split data
            train_test = tokenized_dataset.train_test_split(test_size=0.1)
            train_dataset = train_test["train"]
            eval_dataset = train_test["test"]
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=f"./models/{language}",
                overwrite_output_dir=True,
                num_train_epochs=3,
                per_device_train_batch_size=4,
                per_device_eval_batch_size=4,
                warmup_steps=100,
                logging_steps=10,
                evaluation_strategy="steps",
                eval_steps=100,
                save_steps=500,
                save_total_limit=2,
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False,
            )
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                data_collator=data_collator,
            )
            
            # Train model
            trainer.train()
            
            # Save model
            trainer.save_model()
            tokenizer.save_pretrained(f"./models/{language}")
            
            # Store in memory
            self.models[language] = model
            self.tokenizers[language] = tokenizer
            
            logger.info(f"Model for {language} trained and saved successfully")
            
        except Exception as e:
            logger.error(f"Error training model for {language}: {e}")
            raise e
    
    async def evaluate_models(self):
        """Evaluate trained models"""
        try:
            logger.info("Evaluating trained models...")
            
            for language in ['english', 'tamil', 'hindi']:
                if language in self.models:
                    # Simple evaluation - generate responses
                    test_prompts = [
                        "What are the symptoms of heart disease?",
                        "How is diabetes managed?",
                        "What should I do if I have chest pain?"
                    ]
                    
                    if language == 'tamil':
                        test_prompts = [
                            "இதய நோயின் அறிகுறிகள் என்ன?",
                            "மதுநீரிழிவு எவ்வாறு நிர்வகிக்கப்படுகிறது?",
                            "மார்பு வலி இருந்தால் நான் என்ன செய்ய வேண்டும்?"
                        ]
                    elif language == 'hindi':
                        test_prompts = [
                            "हृदय रोग के लक्षण क्या हैं?",
                            "मधुमेह का प्रबंधन कैसे किया जाता है?",
                            "अगर मुझे छाती में दर्द है तो मुझे क्या करना चाहिए?"
                        ]
                    
                    logger.info(f"Testing {language} model...")
                    for prompt in test_prompts:
                        response = self._generate_response(prompt, language)
                        logger.info(f"Prompt: {prompt}")
                        logger.info(f"Response: {response}")
                        logger.info("---")
            
        except Exception as e:
            logger.error(f"Error evaluating models: {e}")
            raise e
    
    def _generate_response(self, prompt: str, language: str) -> str:
        """Generate response using trained model"""
        try:
            if language not in self.models or language not in self.tokenizers:
                return f"Model for {language} not available"
            
            model = self.models[language]
            tokenizer = self.tokenizers[language]
            
            # Tokenize input
            inputs = tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove input from response
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response for {language}"
    
    async def save_training_artifacts(self):
        """Save training artifacts and metadata"""
        try:
            logger.info("Saving training artifacts...")
            
            # Create models directory
            import os
            os.makedirs("./models", exist_ok=True)
            
            # Save metadata
            metadata = {
                "training_date": str(datetime.now()),
                "languages": ['english', 'tamil', 'hindi'],
                "model_base": "microsoft/DialoGPT-medium",
                "training_data_size": {
                    "english": len(self.training_data.get('english_formatted', [])),
                    "tamil": len(self.training_data.get('tamil_formatted', [])),
                    "hindi": len(self.training_data.get('hindi_formatted', []))
                },
                "medical_categories": ["cardiology", "endocrinology", "general"],
                "features": [
                    "multilingual_support",
                    "medical_qa",
                    "conversation_handling",
                    "symptom_analysis"
                ]
            }
            
            with open("./models/training_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("Training artifacts saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving training artifacts: {e}")
            raise e

async def main():
    """Main training function"""
    try:
        logger.info("Starting Multilingual AI Training for MedAgg Healthcare")
        
        trainer = MultilingualAITrainer()
        
        # Load datasets
        await trainer.load_medical_datasets()
        
        # Prepare training data
        await trainer.prepare_training_data()
        
        # Train models
        await trainer.train_models()
        
        # Evaluate models
        await trainer.evaluate_models()
        
        # Save artifacts
        await trainer.save_training_artifacts()
        
        logger.info("Multilingual AI training completed successfully!")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(main())


