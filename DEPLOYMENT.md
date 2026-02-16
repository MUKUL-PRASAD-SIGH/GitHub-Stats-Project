# 🚀 Deployment Guide

This guide will help you deploy your GitHub Stats API to production.

## Option 1: Render (Recommended - Free Tier Available)

### Step-by-Step Instructions:

1. **Create a Render Account**
   - Go to [https://render.com](https://render.com)
   - Sign up with your GitHub account

2. **Push Your Code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/MUKUL-PRASAD-SIGH/github-stats-api.git
   git push -u origin main
   ```

3. **Create a New Web Service on Render**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `github-stats-api` repository

4. **Configure the Service**
   - **Name**: `github-stats-api` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables**
   - Click "Environment" tab
   - Add the following:
     - **Key**: `GITHUB_TOKEN`
     - **Value**: Your GitHub Personal Access Token
   - (Optional) Add `CACHE_TTL` if you want custom cache duration

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (usually 2-3 minutes)
   - Your API will be live at: `https://your-service-name.onrender.com`

7. **Test Your Deployment**
   ```bash
   curl https://your-service-name.onrender.com/health
   ```

### Free Tier Limitations:
- ✅ 750 hours/month (enough for 24/7 uptime)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Cold start takes 30-60 seconds

---

## Option 2: Railway (Easy Alternative)

### Step-by-Step Instructions:

1. **Create a Railway Account**
   - Go to [https://railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `github-stats-api`

3. **Add Environment Variables**
   - Go to "Variables" tab
   - Add `GITHUB_TOKEN` with your token

4. **Deploy**
   - Railway will auto-detect Python and deploy
   - Your API will be at: `https://your-app.railway.app`

### Free Tier:
- ✅ $5 credit/month
- ✅ No sleep/cold starts
- ⚠️ Limited to ~500 hours/month

---

## Option 3: Vercel (Serverless)

### Step-by-Step Instructions:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Create `vercel.json`**
   Already included in the project!

3. **Deploy**
   ```bash
   vercel
   ```

4. **Add Environment Variable**
   ```bash
   vercel env add GITHUB_TOKEN
   ```

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

### Free Tier:
- ✅ Unlimited deployments
- ✅ Serverless (no cold starts)
- ✅ Global CDN
- ⚠️ 10-second execution limit

---

## Post-Deployment Checklist

### 1. Test All Endpoints

```bash
# Replace YOUR_URL with your deployment URL
export API_URL="https://your-service-name.onrender.com"

# Test health
curl $API_URL/health

# Test stats
curl "$API_URL/stats?user=MUKUL-PRASAD-SIGH"

# Test streak
curl "$API_URL/streak?user=MUKUL-PRASAD-SIGH"

# Test languages
curl "$API_URL/languages?user=MUKUL-PRASAD-SIGH"

# Test trophy
curl "$API_URL/trophy?user=MUKUL-PRASAD-SIGH"

# Test heatmap
curl "$API_URL/heatmap?user=MUKUL-PRASAD-SIGH"

# Test snake
curl "$API_URL/snake?user=MUKUL-PRASAD-SIGH"
```

### 2. Update Your GitHub README

Add badges to your profile README:

```markdown
## 📊 GitHub Stats

![Stats](https://your-service-name.onrender.com/stats?user=MUKUL-PRASAD-SIGH&theme=dark)

![Streak](https://your-service-name.onrender.com/streak?user=MUKUL-PRASAD-SIGH&theme=dark)

![Languages](https://your-service-name.onrender.com/languages?user=MUKUL-PRASAD-SIGH&limit=8&theme=dark)

![Trophy](https://your-service-name.onrender.com/trophy?user=MUKUL-PRASAD-SIGH&theme=dark)

![Heatmap](https://your-service-name.onrender.com/heatmap?user=MUKUL-PRASAD-SIGH&theme=light)

![Snake](https://your-service-name.onrender.com/snake?user=MUKUL-PRASAD-SIGH&theme=dark)
```

### 3. Set Up Monitoring (Optional)

#### UptimeRobot (Free)
1. Go to [https://uptimerobot.com](https://uptimerobot.com)
2. Add monitor for `https://your-url.com/health`
3. Get alerts if your API goes down

#### Better Uptime (Free)
1. Go to [https://betteruptime.com](https://betteruptime.com)
2. Monitor your endpoints
3. Get status page

### 4. Enable CORS (If Needed)

If you want to use the API from a web app, add CORS middleware to `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### Issue: "GitHub API Rate Limit Exceeded"

**Solution**: Make sure your `GITHUB_TOKEN` is set correctly. Without a token, you're limited to 60 requests/hour.

### Issue: "Cold Start Takes Too Long"

**Solutions**:
1. Use Railway instead of Render (no cold starts)
2. Set up a cron job to ping your API every 10 minutes
3. Upgrade to Render's paid plan

### Issue: "SVG Not Rendering in README"

**Solutions**:
1. Make sure the URL is publicly accessible
2. Check if GitHub is caching old version (add `?v=1` to URL)
3. Verify the endpoint returns valid SVG

### Issue: "Deployment Failed"

**Solutions**:
1. Check build logs for errors
2. Verify `requirements.txt` is correct
3. Ensure Python version matches `runtime.txt`
4. Check environment variables are set

---

## Performance Optimization

### 1. Increase Cache TTL

```env
CACHE_TTL=7200  # 2 hours instead of 1
```

### 2. Use Redis (Production)

Replace in-memory cache with Redis:

```python
# app/cache.py
import redis
from .config import settings

redis_client = redis.from_url(settings.redis_url)
```

### 3. Add Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

## Next Steps

1. ✅ Deploy to Render/Railway
2. ✅ Test all endpoints
3. ✅ Add badges to your GitHub profile
4. ✅ Share with the community!
5. 🎉 Star the repo if you found it useful!

---

## Need Help?

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/MUKUL-PRASAD-SIGH/github-stats-api/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/MUKUL-PRASAD-SIGH/github-stats-api/discussions)

---

**Happy Deploying! 🚀**
