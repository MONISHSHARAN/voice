@echo off
echo 🌍 Setting up Multilingual AI for MedAgg Healthcare...
echo ==================================================

REM Create necessary directories
echo 📁 Creating directories...
if not exist data mkdir data
if not exist models mkdir models
if not exist logs mkdir logs

REM Install additional Python packages for multilingual AI
echo 📦 Installing multilingual AI packages...
pip install datasets pandas numpy scikit-learn
pip install transformers[torch] accelerate bitsandbytes
pip install openai-whisper coqui-tts

REM Collect medical data
echo 📊 Collecting medical data from various sources...
cd backend
python collect_medical_data.py

REM Train multilingual models
echo 🤖 Training multilingual AI models...
python train_multilingual_ai.py

REM Test the models
echo 🧪 Testing multilingual models...
python -c "import asyncio; from services.multilingual_ai_service import MultilingualAIService; print('Multilingual AI models loaded successfully!')"

echo ✅ Multilingual AI setup completed successfully!
echo.
echo 🚀 Features available:
echo - English, Tamil, and Hindi language support
echo - Multilingual STT and TTS
echo - Trained medical conversation models
echo - Language-specific medical terminology
echo - Patient language preference handling
echo.
echo 📋 Next steps:
echo 1. Start the application: docker-compose up -d
echo 2. Test with different languages in the patient form
echo 3. Monitor conversation logs in the admin dashboard
echo.
echo Happy multilingual healthcare! 🌍🏥
pause


