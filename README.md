# MedAgg Healthcare POC

A comprehensive AI-powered healthcare appointment booking system that provides automated patient calls, intelligent diagnosis, and seamless appointment scheduling.

## 🚀 Features

### Core Functionality
- **AI-Powered Patient Calls**: Automated conversational AI that calls patients after form submission
- **Multilingual Support**: Full support for English, Tamil, and Hindi with native conversation flows
- **Intelligent Diagnosis**: AI analyzes symptoms and recommends appropriate specialists
- **Smart Appointment Scheduling**: Automatically books appointments with the best available specialists
- **Real-time Call Tracking**: Live status updates and conversation logging
- **Email Notifications**: Automated confirmation and reminder emails
- **Language-Specific Medical Terminology**: Comprehensive medical vocabulary in all supported languages

### Admin Dashboard
- **Complete System Overview**: Real-time statistics and analytics
- **Patient Management**: View, edit, and manage all patient records
- **Hospital Management**: Manage hospital database and specializations
- **Appointment Management**: Track and manage all appointments
- **Call Session Monitoring**: Real-time call status and conversation logs
- **Analytics & Reporting**: Comprehensive system analytics and trends

### Technical Features
- **Modern React Frontend**: Beautiful, responsive UI with Tailwind CSS
- **FastAPI Backend**: High-performance Python API with async support
- **PostgreSQL Database**: Robust data storage with proper relationships
- **Redis Caching**: Fast data caching and session management
- **Docker Support**: Easy deployment with Docker Compose
- **Real-time Updates**: Live data refresh and status updates

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │  PostgreSQL DB  │
│                 │◄──►│                 │◄──►│                 │
│  - Patient Form │    │  - AI Services  │    │  - Patients     │
│  - Admin Panel  │    │  - Call Service │    │  - Hospitals    │
│  - Call Status  │    │  - Email Service│    │  - Appointments │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Redis Cache    │
                       │                 │
                       │  - Sessions     │
                       │  - Call Data    │
                       └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database
- **Redis**: In-memory data structure store for caching
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Whisper**: OpenAI's speech-to-text model
- **Coqui TTS**: Text-to-speech synthesis
- **Celery**: Distributed task queue

### Frontend
- **React 18**: Modern React with hooks and functional components
- **React Router**: Client-side routing
- **React Query**: Data fetching and caching
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icon library
- **React Hook Form**: Form handling and validation

### AI/ML
- **OpenAI Whisper**: Multilingual speech-to-text conversion
- **Coqui TTS**: Multilingual text-to-speech synthesis
- **Hugging Face Models**: Pre-trained and fine-tuned multilingual LLMs
- **Custom Medical LLM**: Fine-tuned conversational AI for healthcare
- **Multilingual Training**: Support for English, Tamil, and Hindi training data

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd medagg-healthcare
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Set up multilingual AI (Optional but recommended)**
   ```bash
   # Windows
   setup_multilingual_ai.bat
   
   # Linux/Mac
   ./setup_multilingual_ai.sh
   ```

4. **Start the services**
   ```bash
   docker-compose up -d
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin Dashboard: http://localhost:3000/admin

### Local Development

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Database Setup**
   ```bash
   # Start PostgreSQL and Redis
   # Update DATABASE_URL in .env
   # Run migrations
   ```

## 📱 Usage

### For Patients

1. **Book Appointment**
   - Visit the homepage
   - Click "Book Appointment Now"
   - Fill out the patient form with your details and symptoms
   - **Select your preferred language** (English, Tamil, or Hindi)
   - Select your medical category and sub-category
   - Submit the form

2. **AI Call Process**
   - Our multilingual AI assistant will call you within 5 minutes
   - **Conversation will be in your selected language**
   - Answer questions about your symptoms in your native language
   - Ask any questions you have - the AI understands medical terminology in all languages
   - The AI will schedule your appointment automatically

3. **Confirmation**
   - Receive email confirmation with appointment details
   - Get reminder emails before your appointment
   - Track your call status in real-time

### Multilingual Features

- **Language Selection**: Choose from English, Tamil (தமிழ்), or Hindi (हिन्दी)
- **Native Conversations**: AI speaks naturally in your selected language
- **Medical Terminology**: Comprehensive medical vocabulary in all languages
- **Cultural Sensitivity**: Conversations adapted to cultural contexts
- **Language-Specific Q&A**: AI can answer medical questions in your preferred language

### For Administrators

1. **Access Admin Dashboard**
   - Navigate to /admin
   - View comprehensive system overview
   - Monitor all patients, hospitals, and appointments

2. **Manage System**
   - View real-time statistics and analytics
   - Manage patient records
   - Update hospital information
   - Monitor call sessions and conversations
   - Send custom emails and notifications

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://medagg_user:medagg_password@localhost:5432/medagg
REDIS_URL=redis://localhost:6379

# Twilio (for production calls)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# AI Models
MODEL_PATH=/app/models
WHISPER_MODEL=base
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
```

## 🏥 Medical Categories

### Interventional Cardiology
- **Chronic Total Occlusion (CTO)**: Treatment for completely blocked coronary arteries
- **Radiofrequency Ablation**: Treatment for heart rhythm disorders

## 📊 System Features

### AI Conversation Flow
1. **Greeting**: AI introduces itself and confirms patient identity
2. **Symptom Inquiry**: Detailed questions about patient's condition
3. **Diagnosis Summary**: AI provides preliminary assessment
4. **Q&A Session**: Patient can ask questions about their condition
5. **Appointment Scheduling**: Automatic booking with appropriate specialist

### Hospital Matching Algorithm
- Matches patients based on:
  - Medical specialization requirements
  - Geographic location
  - Hospital availability
  - Patient preferences

### Real-time Monitoring
- Live call status updates
- Conversation logging
- Appointment tracking
- System health monitoring

## 🔒 Security & Privacy

- **Data Encryption**: All sensitive data is encrypted
- **HIPAA Compliance**: Healthcare data protection standards
- **Secure Communication**: Encrypted API endpoints
- **Access Control**: Admin-only system management

## 🚀 Deployment

### Production Deployment

1. **Set up production environment**
   ```bash
   # Configure production database
   # Set up SSL certificates
   # Configure reverse proxy (nginx)
   ```

2. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Monitor system**
   - Check logs: `docker-compose logs -f`
   - Monitor health: `/api/admin/system/health`

## 📈 Monitoring & Analytics

### Admin Dashboard Metrics
- Total patients and recent registrations
- Hospital capacity and specializations
- Appointment statistics and trends
- Call success rates and performance
- System health and uptime

### Real-time Updates
- Auto-refresh every 30 seconds
- Live call status tracking
- Real-time conversation logs
- Instant appointment updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the admin dashboard for system status

## 🔮 Future Enhancements

- **Advanced AI Models**: Integration with GPT-4 or Claude for better conversations
- **Video Calls**: Support for video consultations
- **Mobile App**: Native mobile applications
- **Multi-language Support**: Support for multiple languages
- **Advanced Analytics**: Machine learning-powered insights
- **Integration APIs**: Connect with hospital management systems

---

**MedAgg Healthcare POC** - Revolutionizing healthcare with AI-powered appointment booking and patient care.
