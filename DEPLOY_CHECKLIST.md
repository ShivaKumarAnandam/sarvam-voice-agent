# Render Deployment Checklist

## ☐ Step 1: Push to GitHub (5 minutes)

```bash
cd "Sarvam_Voice_Agent-main"

# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit - Sarvam Voice Agent"

# Create repo on GitHub: https://github.com/new
# Name it: sarvam-voice-agent

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/sarvam-voice-agent.git

# Push
git branch -M main
git push -u origin main
```

## ☐ Step 2: Deploy on Render (10 minutes)

1. Go to: https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `sarvam-voice-agent`
   - **Runtime**: Python 3
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `python twilio_server.py`
   - **Plan**: Free

5. Add Environment Variables (copy from your .env file):
   ```
   ENVIRONMENT = production
   SARVAM_API_KEY = your_sarvam_api_key
   TWILIO_ACCOUNT_SID = your_twilio_account_sid
   TWILIO_AUTH_TOKEN = your_twilio_auth_token
   TWILIO_PHONE_NUMBER = your_twilio_phone_number
   ```

6. Click "Create Web Service"
7. Wait for deployment (5-10 min)

## ☐ Step 3: Get Your URL

Once deployed:
- Copy your Render URL (e.g., `https://sarvam-voice-agent.onrender.com`)
- Test health: `https://your-url.onrender.com/health`

## ☐ Step 4: Configure Twilio

1. Go to: https://console.twilio.com/
2. Phone Numbers → Manage → Active Numbers
3. Click: (850) 930-1790
4. Voice Configuration:
   - URL: `https://your-url.onrender.com/voice/incoming`
   - Method: HTTP POST
5. Click Save

## ☐ Step 5: Test!

Call: **+1 (850) 930-1790**

Expected flow:
1. Welcome message
2. Language selection (press 1, 2, or 3)
3. Speak your question
4. AI responds

## 🎉 Done!

Your voice agent is now live 24/7 with a permanent URL!

**No more ngrok needed!**

---

## Quick Commands

### View Logs
```bash
# In Render Dashboard → Your Service → Logs
```

### Update Code
```bash
git add .
git commit -m "Update message"
git push
# Render auto-deploys!
```

### Test Health
```bash
curl https://your-url.onrender.com/health
```

---

## Important Notes

- **Free tier**: Service sleeps after 15 min inactivity
- **First call**: May take 30-60 sec to wake up
- **Upgrade**: $7/month for always-on service
- **Logs**: Available in Render dashboard

---

## Your URLs

- **Render Dashboard**: https://dashboard.render.com/
- **Your Service**: https://sarvam-voice-agent.onrender.com
- **Health Check**: https://sarvam-voice-agent.onrender.com/health
- **Webhook**: https://sarvam-voice-agent.onrender.com/voice/incoming
- **Twilio Console**: https://console.twilio.com/
