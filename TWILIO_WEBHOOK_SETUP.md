# Twilio Webhook Configuration Guide

## Step 1: Start Your Server

Open a terminal and run:
```bash
cd "Sarvam_Voice_Agent-main"
venv\Scripts\activate
python twilio_server.py
```

You should see:
```
Starting Twilio server on port 8000 (development mode)
```

**Keep this terminal open!**

## Step 2: Expose with ngrok

Open a **NEW terminal** and run:
```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

**Keep this terminal open too!**

## Step 3: Configure Twilio Webhook

1. Go to: https://console.twilio.com/
2. Navigate to: **Phone Numbers → Manage → Active Numbers**
3. Click on your number: **(850) 930-1790**
4. Scroll to **"Voice Configuration"** section
5. Under **"A call comes in"**:
   - Dropdown: **Webhook**
   - URL: `https://YOUR-NGROK-URL/voice/incoming`
     - Example: `https://abc123.ngrok-free.app/voice/incoming`
   - Method: **HTTP POST**
6. Click **Save** at the bottom

## Step 4: Test Your Voice Agent

Call your Twilio number: **+1 (850) 930-1790**

You should hear:
1. "Welcome to Electrical Department Customer Support"
2. Language selection menu
3. Press 1 for Telugu, 2 for Hindi, 3 for English
4. Start speaking your question
5. AI responds in your selected language

## Troubleshooting

### "Webhook Error" when calling
- Check that both terminals (server + ngrok) are running
- Verify the webhook URL in Twilio is correct
- Make sure URL is HTTPS (not HTTP)
- Check server logs for errors

### No audio on call
- Verify WebSocket connection in server logs
- Check for `🔌 WebSocket connected` message
- Ensure ngrok URL is publicly accessible

### Call disconnects immediately
- Check server logs for errors
- Verify Sarvam API key is valid
- Check Twilio account has credits

## Monitoring

Watch your server terminal for:
- `🔔 WEBHOOK HIT!` - Twilio connected successfully
- `🌐 User selected language: Telugu` - Language chosen
- `🔌 WebSocket connected` - Audio stream started
- `👤 User said: [text]` - Your speech recognized
- `🤖 AI responds: [text]` - AI response generated
- `📤 Sending X mulaw bytes` - Audio being sent back

## Example Test Flow

1. Call +1 (850) 930-1790
2. Hear welcome message
3. Press **1** for Telugu
4. Say: "నా విద్యుత్ బిల్లు ఎంత?" (What is my electricity bill?)
5. AI responds in Telugu
6. Continue conversation

## Important Notes

- **ngrok URL changes** every time you restart ngrok (free tier)
- You'll need to **update Twilio webhook** each time ngrok restarts
- For production, deploy to a cloud service with a permanent URL
- Keep both terminals running during testing

## Next Steps

Once testing is successful:
- Deploy to Render/Railway/Heroku for permanent URL
- Update Twilio webhook with production URL
- Monitor usage and costs
- Customize AI responses for your use case
