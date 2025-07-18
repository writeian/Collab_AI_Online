# Railway Deployment Guide

## 🚀 Quick Deploy to Railway

### Step 1: Push to GitHub
Make sure your code is pushed to a GitHub repository.

### Step 2: Connect to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

### Step 3: Configure Environment Variables
In Railway dashboard, go to "Variables" tab and add:

**Required:**
- `FLASK_ENV=production`
- `SECRET_KEY=your-secure-secret-key-here`

**Optional (for AI features):**
- `ANTHROPIC_API_KEY=your-key`
- `OPENAI_API_KEY=your-key`
- `USE_OLLAMA=false`

### Step 4: Deploy
Railway will automatically:
- Detect it's a Python Flask app
- Install dependencies from `requirements.txt`
- Start with `gunicorn wsgi:app`
- Provide HTTPS URL

### Step 5: Get Your URL
Your app will be available at:
`https://your-app-name.railway.app`

## 🔄 Updates
- Push to GitHub → Auto-deploy
- Or manually deploy from Railway dashboard

## 📝 Notes
- Railway provides PostgreSQL database automatically
- HTTPS is included
- Free tier: 500 hours/month
- Custom domains supported 