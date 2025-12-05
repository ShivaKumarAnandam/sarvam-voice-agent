# Setup Guide for Sarvam Voice Agent

## Step 1: Get API Credentials

### Sarvam AI API Key
1. Visit https://www.sarvam.ai/
2. Sign up for an account
3. Go to your dashboard → API Keys
4. Generate a new API key
5. Copy the key (format: `sarvam_xxxxxxxxxxxxx`)

### Twilio Credentials
1. Visit https://www.twilio.com/
2. Sign up for a free trial (get $15 credit)
3. From the Console Dashboard:
   - Copy **Account SID** (starts with `AC...`)
   - Click "Show" and copy **Auth Token**
4. Go to Phone Numbers → Buy a Number
   - Choose a number with Voice capability
   - Copy the phone number (format: `+1234567890`)

## Step 2: Configure Environment

Edit `.env` file and replace the placeholder values:

```ini
SARVAM_API_KEY=your_actual_sarvam_key
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_actual_token
TWILIO_PHONE_NUMBER=+1234567890
```

## Step 3: Install Dependencies

```bash
# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Test Locally

```bash
# Run the server
python twilio_server.py
```

Server will start on http://localhost:8000

## Step 5: Expose to Internet (for Twilio)

Twilio needs a public URL to send webhooks. Use one of these:

### Option A: ngrok (Recommended for testing)
```bash
# Install ngrok from https://ngrok.com/
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Option B: Deploy to Cloud
- Render.com (free tier)
- Railway.app (free tier)
- Heroku (paid)

## Step 6: Configure Twilio Webhook

1. Go to Twilio Console → Phone Numbers → Manage → Active Numbers
2. Click on your phone number
3. Scroll to "Voice Configuration"
4. Set "A CALL COMES IN" webhook:
   - URL: `https://your-domain.com/voice/incoming`
   - Method: POST
5. Click Save

## Step 7: Test the Call

1. Call your Twilio phone number
2. You'll hear language selection menu:
   - Press 1 for Telugu
   - Press 2 for Hindi
   - Press 3 for English
3. Start speaking after the prompt
4. The AI will respond in your selected language

## Troubleshooting

### Server won't start
- Check Python version: `python --version` (need 3.10+)
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

### No audio on call
- Check Twilio webhook URL is correct
- Ensure URL is HTTPS (not HTTP)
- Check server logs for errors

### API errors
- Verify Sarvam API key is correct
- Check Twilio credentials
- Ensure you have credits in both accounts

### Call disconnects immediately
- Check webhook URL is publicly accessible
- Verify WebSocket connection in logs
- Check firewall/network settings

## Monitoring

Check server logs for:
- `🔔 WEBHOOK HIT!` - Twilio connected
- `🌐 User selected language` - Language chosen
- `🔌 WebSocket connected` - Audio stream started
- `👤 User said` - Speech recognized
- `🤖 AI responds` - Response generated

## Cost Estimates

- **Sarvam AI**: Check their pricing page
- **Twilio**: ~$0.013/min for calls (free trial: $15 credit)
- **ngrok**: Free for testing (paid for custom domains)

## Next Steps

- Customize system prompt in `twilio_server.py`
- Add custom business logic
- Deploy to production
- Monitor usage and costs
