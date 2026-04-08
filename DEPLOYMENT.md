# ResumeIQ Pro - Complete Deployment Guide

## 📋 Table of Contents
1. [Backend Deployment (Render)](#backend-deployment-render)
2. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
3. [Connect Backend & Frontend](#connect-backend--frontend)
4. [Testing](#testing)
5. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Backend Deployment (Render)

### Step 1: Prepare Backend Files ✅
- requirements.txt - ✅ Already configured
- Procfile - ✅ Already created
- runtime.txt - ✅ Already created

### Step 2: Push to GitHub
```bash
cd "/c/Users/Yug/Desktop/ResumeIQ Pro"
git add .
git commit -m "Add deployment configuration files"
git push origin main
```

### Step 3: Create Render Account
1. Visit https://render.com
2. Sign up with GitHub account
3. Click "Authorize Render"

### Step 4: Deploy Backend on Render

**Step 4A: Create Web Service**
1. Dashboard → "New +" → "Web Service"
2. Select repository: "ResumeIQ-Pro"
3. Select branch: "main"

**Step 4B: Configure Service**
- **Name**: `resumeiq-api` (or any name)
- **Environment**: `Python 3`
- **Region**: Choose closest to users
- **Branch**: `main`
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`
- **Root Directory**: Leave empty (or set to `backend`)

**Step 4C: Add Environment Variables** (Optional for now)
- Click "Advanced"
- Add Environment Variables:
  ```
  ENVIRONMENT=production
  DEBUG=false
  ```

**Step 4D: Deploy**
- Click "Create Web Service"
- Wait 3-5 minutes for deployment
- Copy your backend URL: `https://resumeiq-api-xxxx.onrender.com`

### Step 5: Test Backend
```bash
# In browser or terminal
curl https://resumeiq-api-xxxx.onrender.com/health

# Should return:
# {"status":"healthy","message":"AI Resume Analyzer API is running!","version":"2.0.0"}
```

### Step 6: Add to GitHub Secrets (for auto-deploy)
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add:
   - `RENDER_API_KEY`: From Render account → API Token
   - `RENDER_SERVICE_ID`: From Render dashboard → Service ID

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Frontend Files ✅
- package.json - ✅ Already configured
- .env.production - ✅ Already created
- vite.config.js - ✅ Already configured

### Step 2: Update Environment Variable
Edit `frontend/.env.production`:
```env
VITE_API_URL=https://resumeiq-api-xxxx.onrender.com
```
Replace `xxxx` with your actual Render service ID.

### Step 3: Create Vercel Account
1. Visit https://vercel.com
2. Sign up with GitHub account
3. Click "Install" for GitHub integration

### Step 4: Deploy Frontend on Vercel

**Step 4A: Import Project**
1. Dashboard → "Add New" → "Project"
2. Select repository: "ResumeIQ-Pro"
3. Click "Import"

**Step 4B: Configure Project**
- **Project Name**: `resumeiq-pro` (optional)
- **Framework Preset**: Select "Vite"
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

**Step 4C: Add Environment Variables**
- Click "Environment Variables"
- Add:
  - Name: `VITE_API_URL`
  - Value: `https://resumeiq-api-xxxx.onrender.com`
  - Environments: Production, Preview, Development
- Click "Save"

**Step 4D: Deploy**
- Click "Deploy"
- Wait 2-3 minutes for deployment
- Copy your frontend URL: `https://resumeiq-pro.vercel.app`

### Step 5: Test Frontend
```bash
# Visit in browser
https://resumeiq-pro.vercel.app
```

---

## Connect Backend & Frontend

### Update CORS in Backend
Edit `backend/main.py` (lines 56-61):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "https://resumeiq-pro.vercel.app",  # Your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Push Update to GitHub
```bash
git add backend/main.py
git commit -m "Update CORS for production URLs"
git push origin main
```

Render will automatically redeploy with the new CORS settings.

---

## Testing

### Test 1: Check Backend Health
```bash
curl https://resumeiq-api-xxxx.onrender.com/health
```
Expected response: `{"status":"healthy",...}`

### Test 2: Check API Documentation
Visit: `https://resumeiq-api-xxxx.onrender.com/docs`
You should see Swagger UI with all endpoints.

### Test 3: Upload Resume in Frontend
1. Go to https://resumeiq-pro.vercel.app
2. Upload a test resume (PDF or DOCX)
3. Check browser console (F12) for errors
4. Analyze the resume and verify scoring works

### Test 4: Check All Features
- ✅ Upload Resume
- ✅ Analyze Resume
- ✅ Generate Interview Questions
- ✅ Evaluate Answers
- ✅ View Skill Roadmap
- ✅ Get Project Suggestions
- ✅ View Progress Tracking

---

## Monitoring & Maintenance

### Backend Monitoring (Render)
1. Go to Render dashboard
2. Select your service
3. View:
   - **Logs**: Real-time application logs
   - **Metrics**: CPU, Memory usage
   - **Events**: Deployment history

### Frontend Monitoring (Vercel)
1. Go to Vercel dashboard
2. Select your project
3. View:
   - **Analytics**: Performance metrics
   - **Deployments**: Deployment history
   - **Logs**: Build and runtime logs

### Set Up Error Tracking (Optional)
Install Sentry for error monitoring:

**Backend** (`backend/main.py`):
```python
import sentry_sdk
sentry_sdk.init("your-sentry-dsn-here")
```

**Frontend** (`frontend/src/main.jsx`):
```javascript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn-here",
  integrations: [
    new Sentry.Replay(),
  ],
});
```

---

## Common Issues & Solutions

### Issue 1: Backend URL Not Accessible
**Solution**:
- Wait 5 minutes for Render build to complete
- Check Render logs for build errors
- Verify service is running (green status)

### Issue 2: CORS Errors in Frontend
**Solution**:
- Check CORS settings in `backend/main.py`
- Add frontend URL to `allow_origins`
- Redeploy backend after updating CORS

### Issue 3: "Cannot GET /health"
**Solution**:
- Backend might still be building
- Check Render logs: Dashboard → Service → Logs
- Wait for build completion (~3-5 min)

### Issue 4: .env Variables Not Loading
**Solution**:
- For Vercel: Environment variables apply on next deployment
- For Render: Redeploy service after adding env variables
- Check that variable names exactly match code

---

## Update Your Code

### When You Update Backend
1. Make changes locally
2. Test locally: `uvicorn backend/main:app --reload`
3. Push to GitHub: `git push origin main`
4. Render auto-deploys (~2-3 minutes)
5. Test deployed version

### When You Update Frontend
1. Make changes locally
2. Test locally: `npm run dev` (in frontend folder)
3. Push to GitHub: `git push origin main`
4. Vercel auto-deploys (~1-2 minutes)
5. Test deployed version

---

## Add a Custom Domain (Optional)

### For Frontend (Vercel)
1. Buy domain (GoDaddy, Namecheap, Route53)
2. Vercel dashboard → Project → Settings → Domains
3. Add domain and follow Domain Configuration
4. Point DNS to Vercel nameservers
5. Wait 24-48 hours for DNS propagation

### For Backend (Render)
1. Buy domain
2. Render dashboard → Service → Settings → Custom Domain
3. Add domain
4. Update DNS CNAME to Render
5. Wait for propagation

---

## Final Checklist

- [ ] Backend deployed on Render
- [ ] Frontend deployed on Vercel
- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] Resume upload works
- [ ] API calls return expected data
- [ ] No CORS errors in browser console
- [ ] All features tested
- [ ] Monitoring set up (optional)
- [ ] Environment variables configured
- [ ] GitHub auto-deploy workflows active

---

## Support

- **Problems with Render?** → https://render.com/docs
- **Problems with Vercel?** → https://vercel.com/docs
- **Problems with FastAPI?** → https://fastapi.tiangolo.com/
- **Problems with React?** → https://react.dev/

---

**Deployment Complete! 🎉**
Your ResumeIQ Pro is now live on the internet!
