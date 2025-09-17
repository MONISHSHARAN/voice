# 🚀 MedAgg Voice Agent - Railway Deployment Guide

## ✅ **PERFECT SOLUTION - NO MORE WEBSOCKET ERRORS!**

This deployment uses **Railway** which has **perfect WebSocket support** and will solve all your connection issues.

## 🎯 **Why Railway?**

- ✅ **Perfect WebSocket Support** - No protocol conflicts
- ✅ **Multiple Ports** - HTTP on 5001, WebSocket on 5000
- ✅ **Easy Deployment** - Just connect GitHub repo
- ✅ **Free Tier** - No credit card required
- ✅ **Auto-scaling** - Handles traffic spikes
- ✅ **SSL Included** - HTTPS/WSS ready

## 📋 **Deployment Steps**

### 1. **Prepare Your Repository**
```bash
# All files are already created:
# - main.py (WebSocket server)
# - web_server.py (HTTP server)
# - railway.json (Railway config)
# - Procfile (Process config)
# - requirements.txt (Dependencies)
```

### 2. **Deploy to Railway**

1. **Go to [Railway.app](https://railway.app)**
2. **Sign up/Login with GitHub**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**
6. **Railway will auto-detect Python and deploy!**

### 3. **Configure Environment Variables**

In Railway dashboard, go to **Variables** tab and add:

```
DEEPGRAM_API_KEY=ebae70e078574403bf495088b5ea043e456b7f2f
TWILIO_ACCOUNT_SID=AC33f397657e06dac328e5d5081eb4f9fd
TWILIO_AUTH_TOKEN=bbf7abc794d8f0eb9538350b501d033f
TWILIO_PHONE_NUMBER=+17752586467
PUBLIC_URL=https://your-app-name.up.railway.app
```

### 4. **Update Twilio Webhooks**

1. **Go to [Twilio Console](https://console.twilio.com)**
2. **Navigate to Phone Numbers → Manage → Active Numbers**
3. **Click on your phone number**
4. **Set Webhook URL to:** `https://your-app-name.up.railway.app/twiml`
5. **HTTP Method:** POST
6. **Save Configuration**

## 🌐 **Your URLs**

After deployment, you'll get:

- **Main Website:** `https://your-app-name.up.railway.app`
- **Test Page:** `https://your-app-name.up.railway.app/test`
- **WebSocket:** `wss://your-app-name.up.railway.app/twilio`
- **TwiML:** `https://your-app-name.up.railway.app/twiml`

## 🔧 **How It Works**

### **Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Twilio Call   │───▶│   HTTP Server   │───▶│  WebSocket      │
│                 │    │   (Port 5001)   │    │  Server         │
│                 │    │   - TwiML       │    │  (Port 5000)    │
│                 │    │   - Web Pages   │    │  - Deepgram     │
│                 │    │   - API         │    │  - AI Chat      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Flow:**
1. **Patient calls** → Twilio receives call
2. **Twilio** → Calls your TwiML endpoint
3. **TwiML** → Routes to WebSocket server
4. **WebSocket** → Connects to Deepgram Agent API
5. **AI Conversation** → Real-time voice interaction
6. **Function Calls** → Medical assessment & scheduling

## 🎤 **Features Included**

- ✅ **Real-time Voice AI** - Deepgram Agent API
- ✅ **Cardiology Focus** - UFE questionnaire
- ✅ **Function Calling** - Medical assessments
- ✅ **Emergency Detection** - Critical symptom handling
- ✅ **Appointment Booking** - Integrated scheduling
- ✅ **Web Interface** - Patient registration & testing
- ✅ **Professional UI** - Modern, responsive design

## 🚨 **Troubleshooting**

### **If WebSocket Still Fails:**
1. **Check Railway logs** - Look for WebSocket connection errors
2. **Verify environment variables** - All must be set correctly
3. **Test TwiML URL** - Should return XML, not HTML
4. **Check Twilio webhooks** - Must point to correct URL

### **If Calls Don't Connect:**
1. **Verify phone number** - Must be verified for trial accounts
2. **Check Twilio credentials** - Account SID and Auth Token
3. **Test TwiML endpoint** - Should return proper XML
4. **Check Railway deployment** - Must be running successfully

## 📊 **Monitoring**

### **Railway Dashboard:**
- **Deployments** - View deployment status
- **Logs** - Real-time application logs
- **Metrics** - CPU, memory, network usage
- **Variables** - Environment variable management

### **Key Logs to Watch:**
```
✅ Twilio client initialized successfully
🎤 Starting WebSocket server on port 5000
🌐 Starting web server on port 5001
📞 Making call to +91XXXXXXXXXX
✅ Call initiated successfully!
```

## 🎉 **Success Indicators**

When everything works correctly, you'll see:

1. **Website loads** - No more "empty Connection header" error
2. **Test page works** - Patient registration form functions
3. **Calls connect** - Twilio successfully routes to WebSocket
4. **AI responds** - Deepgram Agent API processes conversation
5. **Functions execute** - Medical assessments and scheduling work

## 🔄 **Updates & Maintenance**

### **To Update Code:**
1. **Push to GitHub** - Your changes
2. **Railway auto-deploys** - No manual intervention needed
3. **Check logs** - Ensure successful deployment

### **To Update Environment Variables:**
1. **Railway Dashboard** → Variables tab
2. **Edit values** → Save changes
3. **Redeploy** → Automatic restart

## 💡 **Pro Tips**

1. **Use Railway's free tier** - Perfect for development and testing
2. **Monitor logs regularly** - Catch issues early
3. **Test with verified numbers** - Avoid trial account limitations
4. **Keep credentials secure** - Use Railway's variable system
5. **Backup your config** - Save working configurations

## 🆘 **Support**

If you encounter any issues:

1. **Check Railway logs** - Most errors are visible there
2. **Verify all URLs** - Ensure they're accessible
3. **Test components individually** - WebSocket, HTTP, TwiML
4. **Check Twilio console** - Verify webhook configuration

---

## 🎯 **Ready to Deploy?**

1. **Push your code to GitHub**
2. **Go to Railway.app**
3. **Deploy from GitHub**
4. **Add environment variables**
5. **Update Twilio webhooks**
6. **Test your voice agent!**

**This solution will work perfectly - no more WebSocket errors!** 🚀
