# 🚀 Render Deployment - Quick Guide

## Why Render Instead of ngrok?

✅ **Permanent URL** - Never changes  
✅ **24/7 Availability** - Always online  
✅ **Auto-deploy** - Push to GitHub, auto-updates  
✅ **Free Tier** - Good for testing  
✅ **Production Ready** - Scale when needed  

❌ ngrok URL changes every restart  
❌ ngrok requires terminal running  
❌ ngrok free tier has limitations  

---

## 🎯 Deployment in 3 Steps

### 1️⃣ Push to GitHub (5 min)

**Option A: Use the script**
```bash
cd "Sarvam_Voice_Agent-main"
DEPLOY_TO_RENDER.bat
```

**Option B: Manual commands**
```bash
cd "Sarvam_Voice_Agent-main"
git init
git add .
git commit -m "Deploy to Render"

# Create repo at: https://github.com/new
# Then:
git remote add origin https://github.com/YOUR_USERNAME/sarvam-voice-agent.git
git branch -M main
git push -u origin main
```

### 2️⃣ Deploy on Render (10 min)

1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect GitHub repo: `sarvam-voice-agent`
4. Settings:
   - Name: `sarvam-voice-agent`
   - Build: `pip install -r requirements.txt`
   - Start: `python twilio_server.py`
   - Plan: **Free**

5. Environment Variables (click "Add Environment Variable"):
   ```
   ENVIRONMENT = production
   SARVAM_API_KEY = your_sarvam_api_key_from_env_file
   TWILIO_ACCOUNT_SID = your_twilio_account_sid_from_env_file
   TWILIO_AUTH_TOKEN = your_twilio_auth_token_from_env_file
   TWILIO_PHONE_NUMBER = your_twilio_phone_number_from_env_file
   ```

6. Click "Create Web Service"
7. Wait 5-10 minutes for deployment

### 3️⃣ Configure Twilio (2 min)

1. Copy your Render URL: `https://sarvam-voice-agent.onrender.com`
2. Go to: https://console.twilio.com/
3. Phone Numbers → (850) 930-1790
4. Voice Configuration:
   - **URL**: `https://sarvam-voice-agent.onrender.com/voice/incoming`
   - **Method**: HTTP POST
5. Save

---

## ✅ Test Your Deployment

**Call**: +1 (850) 930-1790

Expected:
1. 🎙️ "Welcome to Electrical Department..."
2. 🔢 Press 1 (Telugu), 2 (Hindi), or 3 (English)
3. 🗣️ Speak your question
4. 🤖 AI responds in your language

---

## 📊 Monitor Your Service

### Render Dashboard
- URL: https://dashboard.render.com/
- Click your service → "Logs" tab
- Watch real-time logs

### Twilio Console
- URL: https://console.twilio.com/
- Monitor → Logs → Calls
- See call details

---

## 🔄 Update Your Code

When you make changes:

```bash
cd "Sarvam_Voice_Agent-main"
git add .
git commit -m "Your update message"
git push
```

Render automatically:
- Detects the push
- Rebuilds your service
- Deploys new version
- Zero downtime!

---

## ⚠️ Free Tier Notes

**Render Free Tier:**
- ✅ 750 hours/month (enough for testing)
- ✅ Automatic HTTPS
- ✅ Custom domain support
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ First call takes 30-60 sec to wake up

**Solution for Cold Starts:**
- Upgrade to $7/month for always-on
- Or use UptimeRobot to ping every 5 min

---

## 💰 Cost Comparison

### With ngrok (Testing)
- ngrok: Free (manual, temporary)
- Sarvam AI: Pay per use
- Twilio: ~$0.013/min
- **Total**: ~$0.02/call

### With Render Free (Testing)
- Render: Free (auto, permanent)
- Sarvam AI: Pay per use
- Twilio: ~$0.013/min
- **Total**: ~$0.02/call + cold starts

### With Render Paid (Production)
- Render: $7/month (always-on)
- Sarvam AI: Pay per use
- Twilio: ~$0.013/min
- **Total**: $7/month + ~$0.02/call

---

## 🆘 Troubleshooting

### Deployment Failed
- Check Render logs for errors
- Verify all environment variables are set
- Ensure requirements.txt is correct

### Call Connects but No Audio
- Check Render logs for WebSocket errors
- Test health endpoint: `/health`
- Verify Twilio webhook URL is correct

### Service Sleeping
- Normal on free tier
- First call wakes it up (30-60 sec)
- Upgrade to paid for instant response

---

## 📚 Documentation Files

- `RENDER_DEPLOYMENT.md` - Detailed deployment guide
- `DEPLOY_CHECKLIST.md` - Step-by-step checklist
- `DEPLOY_TO_RENDER.bat` - Automated git setup
- `render.yaml` - Render configuration
- `.gitignore` - Git ignore rules

---

## 🎉 You're All Set!

Your voice agent is now:
- ✅ Deployed to Render
- ✅ Accessible 24/7
- ✅ Has permanent URL
- ✅ Auto-updates on git push
- ✅ Production ready

**No more ngrok needed!**

Call +1 (850) 930-1790 to test! 📞
