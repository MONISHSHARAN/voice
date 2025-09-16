# 🏥 MedAgg Healthcare POC - Conversational AI System

A comprehensive healthcare proof-of-concept system featuring multilingual conversational AI, Twilio integration, and real-time patient communication.

## 🌟 Features

- **Multilingual Support**: English, Tamil, Hindi
- **Conversational AI**: Open-source AI models with fallback to rule-based responses
- **Twilio Integration**: Real-time voice calls and SMS
- **Patient Management**: Registration, appointment scheduling
- **Admin Dashboard**: Real-time monitoring and analytics
- **Email Notifications**: Automated appointment confirmations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Twilio Account (with verified phone numbers)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/medagg-healthcare.git
   cd medagg-healthcare
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Set your Twilio credentials
   export TWILIO_ACCOUNT_SID="your_account_sid"
   export TWILIO_AUTH_TOKEN="your_auth_token"
   export TWILIO_PHONE_NUMBER="your_twilio_number"
   ```

4. **Start the backend**
   ```bash
   python app.py
   ```

5. **Start the frontend** (in another terminal)
   ```bash
   python -m http.server 3000 --directory frontend
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## 🌐 Deployment

### Render Deployment

1. **Connect to GitHub**
   - Push your code to GitHub
   - Connect your GitHub repository to Render

2. **Configure Environment Variables**
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
   - `TWILIO_PHONE_NUMBER`: Your Twilio Phone Number
   - `PORT`: 8000

3. **Deploy**
   - Render will automatically build and deploy using `render.yaml`
   - Your app will be available at `https://your-app-name.onrender.com`

### Twilio Webhook Configuration

After deployment, configure your Twilio webhooks:

1. **Voice Webhook URL**: `https://your-app-name.onrender.com/twiml`
2. **Status Callback URL**: `https://your-app-name.onrender.com/status`

## 📱 Usage

### Patient Registration
1. Visit the frontend URL
2. Fill out the patient form with language preference
3. Submit to receive an AI-powered call

### Admin Dashboard
- View patient registrations
- Monitor call status
- Access conversation logs

## 🔧 API Endpoints

- `POST /register-patient` - Register new patient
- `GET /patients` - Get all patients
- `GET /conversations` - Get conversation logs
- `GET /ai/status` - Check AI service status
- `POST /twiml` - Twilio webhook for call handling

## 🛠️ Technical Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Hugging Face Transformers, Open-source models
- **Communication**: Twilio Voice API
- **Deployment**: Render, GitHub

## 📋 Requirements

See `requirements.txt` for Python dependencies.

## 🔒 Security

- Environment variables for sensitive data
- Input validation and sanitization
- CORS protection
- Rate limiting (recommended for production)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the GitHub Issues
- Review Twilio documentation
- Contact the development team

---

**Note**: This is a proof-of-concept system. For production use, implement additional security measures, error handling, and monitoring.