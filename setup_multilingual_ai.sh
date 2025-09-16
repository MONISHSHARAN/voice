#!/bin/bash

echo "🌍 Setting up Multilingual AI for MedAgg Healthcare..."
echo "=================================================="

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data
mkdir -p models
mkdir -p logs

# Install additional Python packages for multilingual AI
echo "📦 Installing multilingual AI packages..."
pip install datasets pandas numpy scikit-learn
pip install transformers[torch] accelerate bitsandbytes
pip install openai-whisper coqui-tts

# Collect medical data
echo "📊 Collecting medical data from various sources..."
cd backend
python collect_medical_data.py

# Train multilingual models
echo "🤖 Training multilingual AI models..."
python train_multilingual_ai.py

# Test the models
echo "🧪 Testing multilingual models..."
python -c "
import asyncio
from services.multilingual_ai_service import MultilingualAIService

async def test_models():
    ai = MultilingualAIService()
    await ai.initialize_models()
    
    # Test English
    response = await ai.process_conversation('test_session', 'I have chest pain', {
        'name': 'John', 'language_preference': 'english', 'medical_category': 'interventional_cardiology'
    })
    print(f'English Response: {response}')
    
    # Test Tamil
    response = await ai.process_conversation('test_session_tamil', 'எனக்கு மார்பு வலி இருக்கிறது', {
        'name': 'ராஜா', 'language_preference': 'tamil', 'medical_category': 'interventional_cardiology'
    })
    print(f'Tamil Response: {response}')
    
    # Test Hindi
    response = await ai.process_conversation('test_session_hindi', 'मुझे छाती में दर्द है', {
        'name': 'राम', 'language_preference': 'hindi', 'medical_category': 'interventional_cardiology'
    })
    print(f'Hindi Response: {response}')

asyncio.run(test_models())
"

echo "✅ Multilingual AI setup completed successfully!"
echo ""
echo "🚀 Features available:"
echo "- English, Tamil, and Hindi language support"
echo "- Multilingual STT and TTS"
echo "- Trained medical conversation models"
echo "- Language-specific medical terminology"
echo "- Patient language preference handling"
echo ""
echo "📋 Next steps:"
echo "1. Start the application: docker-compose up -d"
echo "2. Test with different languages in the patient form"
echo "3. Monitor conversation logs in the admin dashboard"
echo ""
echo "Happy multilingual healthcare! 🌍🏥"


