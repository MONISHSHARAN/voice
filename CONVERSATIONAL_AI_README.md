# MedAgg Healthcare POC - Conversational AI System

## 🏥 Overview

This is a comprehensive healthcare POC that implements **Twilio Conversational Intelligence** with real-time AI conversations. The system provides multilingual medical assistance through intelligent voice conversations powered by OpenAI's GPT-4.

## 🚀 Key Features

### 🤖 Conversational Intelligence
- **Real-time AI Conversations**: Patients can have natural conversations with Dr. MedAgg (AI)
- **Multilingual Support**: English, Tamil (தமிழ்), and Hindi (हिन्दी)
- **Medical Expertise**: AI trained specifically for healthcare scenarios
- **Symptom Assessment**: Initial triage and medical guidance
- **Appointment Scheduling**: Intelligent appointment booking

### 📞 Twilio Integration
- **Voice Calls**: Real-time voice conversations
- **TwiML Generation**: Dynamic call flows
- **Media Streams**: Real-time audio processing
- **ConversationRelay**: Seamless AI integration

### 🌍 Multilingual Support
- **English**: Full conversational support
- **Tamil**: Native Tamil language support
- **Hindi**: Native Hindi language support
- **Cultural Adaptation**: Language-specific medical terminology

## 🛠️ Technical Architecture

### Backend Components
1. **Conversational AI Backend** (`conversational_ai_backend.py`)
   - Handles patient registration
   - Manages Twilio call flows
   - Integrates with OpenAI GPT-4
   - Processes multilingual conversations

2. **WebSocket Server** (`websocket_server.py`)
   - Real-time audio streaming
   - OpenAI Realtime API integration
   - Conversation management

3. **Frontend** (`frontend/index.html`)
   - Patient registration form
   - Real-time status monitoring
   - Admin dashboard

### AI Integration
- **OpenAI GPT-4**: Core conversational AI
- **Whisper**: Speech-to-text transcription
- **TTS**: Text-to-speech synthesis
- **Medical Prompts**: Healthcare-specific AI instructions

## 📋 Prerequisites

### Required Software
- Python 3.8+
- Node.js (for frontend)
- Git

### Required Accounts
- **Twilio Account**: For voice calls
- **OpenAI Account**: For AI conversations

### API Keys
- Twilio Account SID and Auth Token
- OpenAI API Key

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo>
cd Voice
python setup_conversational_ai.py
```

### 2. Configure Environment
```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Or create .env file
cp .env.template .env
# Edit .env with your API keys
```

### 3. Start the System
```bash
# Terminal 1: Start Conversational AI Backend
python conversational_ai_backend.py

# Terminal 2: Start Frontend
python -m http.server 3000 --directory frontend

# Terminal 3: Start WebSocket Server (optional)
python websocket_server.py
```

### 4. Test the System
```bash
python test_conversational_ai.py
```

## 🔧 Configuration

### Twilio Configuration
The system is pre-configured with your Twilio credentials:
- Account SID: `AC33f397657e06dac328e5d5081eb4f9fd`
- Auth Token: `bbf7abc794d8f0eb9538350b501d033f`
- Phone Number: `+17752586467`

### OpenAI Configuration
Set your OpenAI API key:
```bash
export OPENAI_API_KEY="sk-your-openai-api-key-here"
```

### Language Configuration
The system supports three languages:
- **English**: Default language
- **Tamil**: Set `language_preference: "Tamil"`
- **Hindi**: Set `language_preference: "Hindi"`

## 📱 Usage

### Patient Registration
1. Open http://localhost:3000
2. Fill out the patient form
3. Select language preference
4. Click "Register & Get Conversational AI Call"
5. Receive intelligent AI call

### AI Conversation Flow
1. **Greeting**: AI greets in selected language
2. **Symptom Assessment**: Patient describes symptoms
3. **Medical Guidance**: AI provides medical advice
4. **Appointment Scheduling**: AI can schedule appointments
5. **Follow-up**: AI provides next steps

### Admin Dashboard
- View registered patients
- Monitor active conversations
- Track system status

## 🧪 Testing

### Automated Tests
```bash
python test_conversational_ai.py
```

### Manual Testing
1. **Backend API**: Test all endpoints
2. **Frontend**: Test patient registration
3. **Twilio Calls**: Verify call initiation
4. **AI Conversations**: Test multilingual responses

### Test Scenarios
- English conversation
- Tamil conversation
- Hindi conversation
- Emergency scenarios
- Appointment scheduling

## 🔍 API Endpoints

### Patient Management
- `POST /register-patient` - Register new patient
- `GET /patients` - Get all patients
- `GET /conversations` - Get active conversations

### Twilio Integration
- `GET /twiml` - TwiML for calls
- `POST /process-input` - Process user input

### System Status
- `GET /` - Backend status
- `GET /hospitals` - Available hospitals

## 🌐 WebSocket Endpoints

### Real-time Communication
- `ws://localhost:8765/conversation/{id}` - Conversation stream
- Handles Twilio Media Streams
- Integrates with OpenAI Realtime API

## 📊 Monitoring

### System Status
- Backend API status
- AI service status
- Active conversations
- Call statistics

### Logs
- Conversation logs
- Error logs
- Performance metrics

## 🚨 Troubleshooting

### Common Issues

1. **Backend API Offline**
   - Check if port 8000 is available
   - Restart the backend server
   - Check for Python process conflicts

2. **OpenAI API Errors**
   - Verify API key is set correctly
   - Check API key permissions
   - Monitor API usage limits

3. **Twilio Call Issues**
   - Verify phone number is verified
   - Check Twilio account status
   - Verify webhook URLs

4. **Multilingual Issues**
   - Check language preference setting
   - Verify TwiML generation
   - Test with different languages

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python conversational_ai_backend.py
```

## 🔒 Security

### API Key Management
- Store API keys in environment variables
- Never commit API keys to version control
- Use .env files for local development

### Data Privacy
- Patient data is stored in memory (development)
- Implement database encryption for production
- Follow HIPAA guidelines for healthcare data

## 🚀 Production Deployment

### Requirements
- Production database (PostgreSQL)
- Redis for caching
- Load balancer for high availability
- SSL certificates for HTTPS
- Domain name for webhooks

### Environment Variables
```bash
# Production configuration
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
OPENAI_API_KEY=your_key
```

## 📈 Performance

### Optimization
- Connection pooling for databases
- Caching for frequent requests
- Async processing for AI calls
- Load balancing for high traffic

### Monitoring
- Response time monitoring
- Error rate tracking
- Resource usage monitoring
- AI API usage tracking

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Code Standards
- Follow PEP 8 for Python
- Use type hints
- Write comprehensive tests
- Document all functions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- Twilio Docs: https://www.twilio.com/docs
- OpenAI Docs: https://platform.openai.com/docs
- This README

### Contact
- GitHub Issues for bug reports
- Pull requests for contributions
- Email for support questions

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Basic conversational AI
- ✅ Multilingual support
- ✅ Twilio integration
- ✅ Patient registration

### Phase 2 (Next)
- 🔄 Real-time audio streaming
- 🔄 Advanced medical AI prompts
- 🔄 Appointment scheduling
- 🔄 Email notifications

### Phase 3 (Future)
- 📋 Database integration
- 📋 Advanced analytics
- 📋 Mobile app
- 📋 Integration with hospital systems

---

**Built with ❤️ for Healthcare Innovation**
