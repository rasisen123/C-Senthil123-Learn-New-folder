# Deployment Guide - International Cricket Statistics App

This guide covers multiple deployment options for your FastAPI cricket statistics application.

## Prerequisites

- Your cricket API key: `48e8c9c5-77c8-45f7-bda6-f5555f4c9dc2`
- Git installed (for most platforms)
- Account on your chosen platform

---

## Option 1: Render (Recommended - Free Tier Available)

### Steps:

1. **Create a Render account**: https://render.com

2. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

3. **Deploy on Render**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: cricket-stats-app
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add Environment Variable:
     - Key: `CRICKET_API_KEY`
     - Value: `48e8c9c5-77c8-45f7-bda6-f5555f4c9dc2`
   - Click "Create Web Service"

4. **Access your app**: Render will provide a URL like `https://cricket-stats-app.onrender.com`

---

## Option 2: Railway (Free Tier Available)

### Steps:

1. **Create a Railway account**: https://railway.app

2. **Deploy**:
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo" or "Empty Project"
   - If empty project, use Railway CLI:
     ```bash
     npm i -g @railway/cli
     railway login
     railway init
     railway up
     ```

3. **Configure**:
   - Railway auto-detects Python
   - Add environment variable `CRICKET_API_KEY` in settings

4. **Generate domain**: Railway provides a free domain

---

## Option 3: Docker Deployment (Any Platform)

### Build and Run Locally:

```bash
# Build the Docker image
docker build -t cricket-stats-app .

# Run the container
docker run -p 8000:8000 -e CRICKET_API_KEY=48e8c9c5-77c8-45f7-bda6-f5555f4c9dc2 cricket-stats-app
```

### Deploy to Docker Hub + Cloud:

```bash
# Tag and push to Docker Hub
docker tag cricket-stats-app yourusername/cricket-stats-app
docker push yourusername/cricket-stats-app

# Then deploy to any cloud platform that supports Docker
```

---

## Option 4: Heroku (Paid Plans Only Now)

### Steps:

1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

2. Create `Procfile`:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. Deploy:
   ```bash
   heroku login
   heroku create cricket-stats-app
   heroku config:set CRICKET_API_KEY=48e8c9c5-77c8-45f7-bda6-f5555f4c9dc2
   git push heroku main
   ```

---

## Option 5: DigitalOcean App Platform

### Steps:

1. **Create DigitalOcean account**: https://www.digitalocean.com

2. **Deploy**:
   - Go to "Apps" → "Create App"
   - Connect GitHub repository
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Run Command**: `uvicorn main:app --host 0.0.0.0 --port 8080`
   - Add environment variable `CRICKET_API_KEY`

3. **Deploy**: DigitalOcean builds and deploys automatically

---

## Option 6: AWS (EC2 or Elastic Beanstalk)

### Quick EC2 Setup:

1. Launch an EC2 instance (Ubuntu)
2. SSH into the instance
3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements.txt
   ```
4. Run with screen/tmux:
   ```bash
   screen -S cricket-app
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

## Post-Deployment Checklist

- ✅ App is accessible via the provided URL
- ✅ API key is set as environment variable (not hardcoded)
- ✅ Matches are loading correctly
- ✅ Auto-refresh is working
- ✅ All filters (domestic, state teams) are active

---

## Troubleshooting

### App won't start:
- Check logs for errors
- Verify `requirements.txt` has all dependencies
- Ensure port binding is correct (`0.0.0.0` not `127.0.0.1`)

### No matches showing:
- Verify API key is set correctly
- Check API rate limits (100 requests/day on free tier)
- View debug endpoint: `https://your-app-url/api/debug/raw`

### Slow performance:
- Consider adding Redis caching
- Reduce auto-refresh interval
- Use CDN for static files

---

## Recommended: Render

For this project, **Render** is the best choice because:
- Free tier available
- Easy setup (no credit card required)
- Auto-deploys from GitHub
- Good for FastAPI/Python apps
- Provides HTTPS by default

**Estimated deployment time: 5-10 minutes**
