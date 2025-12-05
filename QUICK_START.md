# Quick Start Checklist

Follow these steps to get your voice agent running:

## ☐ Step 1: Get Sarvam AI API Key (5 minutes)
1. Go to https://www.sarvam.ai/
2. Sign up / Login
3. Navigate to API Keys section
4. Generate new API key
5. Copy the key

## ☐ Step 2: Get Twilio Credentials (10 minutes)
1. Go to https://www.twilio.com/
2. Sign up for free trial ($15 credit)
3. From Console Dashboard:
   - Copy **Account SID** (starts with AC...)
   - Copy **Auth Token** (click "Show")
4. Go to Phone Numbers → Buy a Number
   - Select a number with Voice capability
   - Copy the phone number (format: +1234567890)

## ☐ Step 3: Configure Environment (2 minutes)
1. Open `Sarvam_Voice_Agent-main/.env` file
2. Replace these values:
   ```ini
   SARVAM_API_KEY=paste_your_sarvam_key_here
   TWILIO_ACCOUNT_SID=paste_your_account_sid_here
   TWILIO_AUTH_TOKEN=paste_your_auth_token_here
   TWILIO_PHONE_NUMBER=paste_your_phone_number_here
   ```
3. Save the file

## ☐ Step 4: Install Dependencies (5 minutes)
```bash
cd "Sarvam_Voice_Agent-main"

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## ☐ Step 5: Test Setup (2 minutes)
```bash
python test_setup.py
```

If all tests pass ✅, continue to next step.
If any test fails ❌, check the error messages and fix them.

## ☐ Step 6: Start Server (1 minute)
```bash
python twilio_server.py
```

You should see:
```
Starting Twilio server on port 8000 (development mode)
```

Keep this terminal open!

## ☐ Step 7: Expose to Internet (2 minutes)

### Option A: Using ngrok (Recommended)
1. Download ngrok from https://ngrok.com/download
2. Open a NEW terminal
3. Run:
   ```bash
   ngrok http 8000
   ```
4. Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

### Option B: Deploy to Cloud
- Use Render.com, Railway.app, or Heroku
- Deploy the code
- Get your public URL

## ☐ Step 8: Configure Twilio Webhook (3 minutes)
1. Go to https://console.twilio.com/
2. Navigate to: Phone Numbers → Manage → Active Numbers
3. Click on your phone number
4. Scroll to "Voice Configuration"
5. Under "A CALL COMES IN":
   - URL: `https://your-ngrok-url.ngrok-free.app/voice/incoming`
   - Method: **POST**
6. Click **Save**

## ☐ Step 9: Test Your Voice Agent! 🎉
1. Call your Twilio phone number from your mobile
2. You'll hear: "Welcome to Electrical Department..."
3. Press:
   - **1** for Telugu
   - **2** for Hindi
   - **3** for English
4. Start speaking your question
5. The AI will respond in your selected language!

## Example Questions to Try

### Telugu
- "నా విద్యుత్ బిల్లు ఎంత?"
- "కరెంట్ లేదు, ఎప్పుడు వస్తుంది?"
- "లైన్‌మ్యాన్ నంబర్ ఇవ్వండి"

### Hindi
- "मेरा बिजली बिल कितना है?"
- "बिजली नहीं है, कब आएगी?"
- "लाइनमैन का नंबर दें"

### English
- "What is my electricity bill?"
- "There is no power, when will it come?"
- "Give me lineman number"

## Monitoring

Watch the server terminal for logs:
- `🔔 WEBHOOK HIT!` - Call received
- `🌐 User selected language` - Language chosen
- `👤 User said` - Your speech recognized
- `🤖 AI responds` - AI response generated

## Troubleshooting

### Call connects but no audio
- Check ngrok URL is correct in Twilio webhook
- Ensure URL is HTTPS (not HTTP)
- Verify WebSocket connection in logs

### "Configuration error" in test
- Double-check your API keys in .env
- Make sure no extra spaces or quotes
- Verify keys are active

### Server won't start
- Check Python version: `python --version` (need 3.10+)
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

## Need Help?

1. Check server logs for error messages
2. Run `python test_setup.py` to diagnose issues
3. See SETUP_GUIDE.md for detailed troubleshooting
4. Check Twilio Console → Monitor → Logs for call details

---

**Total Setup Time: ~30 minutes**

Once configured, you can:
- Customize the AI responses
- Add your own business logic
- Deploy to production
- Scale to handle multiple calls
