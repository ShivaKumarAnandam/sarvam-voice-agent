# Deploy to Render - Step by Step Guide

## Prerequisites
- GitHub account
- Render account (free tier available)
- Your credentials ready (from your .env file):
  - Sarvam API Key
  - Twilio Account SID
  - Twilio Auth Token
  - Twilio Phone Number

---

## Step 1: Push Code to GitHub

### Option A: Create New Repository (Recommended)

1. Go to https://github.com/new
2. Create a new repository:
   - Name: `sarvam-voice-agent`
   - Visibility: Private (recommended) or Public
   - Don't initialize with README
3. Click "Create repository"

4. In your terminal, run:
```bash
cd "Sarvam_Voice_Agent-main"

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Sarvam Voice Agent"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/sarvam-voice-agent.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option B: Use Existing Repository

If you already have this in a GitHub repo, just make sure it's pushed:
```bash
cd "Sarvam_Voice_Agent-main"
git add .
git commit -m "Ready for Render deployment"
git push
```

---

## Step 2: Deploy to Render

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/
   - Sign up or log in (can use GitHub account)

2. **Create New Web Service**
   - Click "New +" button (top right)
   - Select "Web Service"

3. **Connect GitHub Repository**
   - Click "Connect account" if first time
   - Authorize Render to access your GitHub
   - Find and select your `sarvam-voice-agent` repository
   - Click "Connect"

4. **Configure Service**
   - **Name**: `sarvam-voice-agent` (or any name you prefer)
   - **Region**: Choose closest to you (e.g., Oregon, Singapore)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python twilio_server.py`
   - **Plan**: Free

5. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable" and add these:

   | Key | Value |
   |-----|-------|
   | `ENVIRONMENT` | `production` |
   | `SARVAM_API_KEY` | `your_sarvam_api_key_from_env_file` |
   | `TWILIO_ACCOUNT_SID` | `your_twilio_account_sid_from_env_file` |
   | `TWILIO_AUTH_TOKEN` | `your_twilio_auth_token_from_env_file` |
   | `TWILIO_PHONE_NUMBER` | `your_twilio_phone_number_from_env_file` |

   **Note**: Render automatically sets `PORT` environment variable

6. **Create Web Service**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Watch the logs for any errors

---

## Step 3: Get Your Render URL

Once deployed successfully:
1. You'll see "Live" status with a green dot
2. Your URL will be shown at the top (e.g., `https://sarvam-voice-agent.onrender.com`)
3. **Copy this URL** - you'll need it for Twilio

Test the health endpoint:
- Visit: `https://your-app.onrender.com/health`
- Should return JSON with status "healthy"

---

## Step 4: Configure Twilio Webhook

1. **Go to Twilio Console**
   - Visit: https://console.twilio.com/
   - Navigate to: Phone Numbers → Manage → Active Numbers
   - Click on: **(850) 930-1790**

2. **Update Voice Configuration**
   - Scroll to "Voice Configuration"
   - Under "A call comes in":
     - **Webhook**: `https://your-app.onrender.com/voice/incoming`
     - **Method**: HTTP POST
   - Click **Save**

---

## Step 5: Test Your Deployment

1. **Call your Twilio number**: +1 (850) 930-1790
2. You should hear the welcome message
3. Select language (1, 2, or 3)
4. Speak your question
5. AI responds!

---

## Monitoring & Logs

### View Render Logs
1. Go to Render Dashboard
2. Click on your service
3. Click "Logs" tab
4. Watch real-time logs for:
   - `🔔 WEBHOOK HIT!`
   - `🌐 User selected language`
   - `👤 User said`
   - `🤖 AI responds`

### Check Twilio Logs
1. Go to Twilio Console
2. Navigate to: Monitor → Logs → Calls
3. See call details and any errors

---

## Important Notes

### Free Tier Limitations
- **Render Free Tier**:
  - Service spins down after 15 minutes of inactivity
  - First call after inactivity takes 30-60 seconds to wake up
  - 750 hours/month free (enough for testing)

### Cold Start Issue
When service is asleep:
- First caller hears silence for 30-60 seconds
- Subsequent calls are instant
- **Solution**: Upgrade to paid plan ($7/month) for always-on service

### Keep Service Awake (Optional)
Use a service like UptimeRobot to ping your health endpoint every 5 minutes:
- URL to ping: `https://your-app.onrender.com/health`
- Interval: 5 minutes
- This keeps your service awake (within free tier limits)

---

## Troubleshooting

### Deployment Failed
- Check Render logs for errors
- Verify `requirements.txt` has all dependencies
- Ensure Python version compatibility

### Call Connects but No Audio
- Check Render logs for WebSocket errors
- Verify environment variables are set correctly
- Test health endpoint: `/health`

### API Errors
- Verify Sarvam API key is valid
- Check Twilio credentials
- Ensure both accounts have credits

### Service Keeps Sleeping
- Upgrade to paid plan ($7/month)
- Or use UptimeRobot to keep it awake

---

## Updating Your Deployment

When you make code changes:

```bash
cd "Sarvam_Voice_Agent-main"
git add .
git commit -m "Your update message"
git push
```

Render will automatically:
1. Detect the push
2. Rebuild your service
3. Deploy the new version
4. Zero downtime deployment

---

## Cost Estimate

### Free Tier (Testing)
- Render: Free (with cold starts)
- Sarvam AI: Pay per use
- Twilio: ~$0.013/min
- **Total**: ~$0.02-0.05 per call

### Paid Tier (Production)
- Render: $7/month (always-on)
- Sarvam AI: Pay per use
- Twilio: ~$0.013/min
- **Total**: $7/month + per-call costs

---

## Next Steps

1. ✅ Deploy to Render
2. ✅ Configure Twilio webhook
3. ✅ Test with real calls
4. 📊 Monitor usage and costs
5. 🎨 Customize AI responses
6. 🚀 Scale as needed

---

## Support

- **Render Docs**: https://render.com/docs
- **Twilio Docs**: https://www.twilio.com/docs
- **Sarvam AI Docs**: https://www.sarvam.ai/docs

Your permanent URL will be:
`https://sarvam-voice-agent.onrender.com`

No more ngrok needed! 🎉
