
# 🚀 Deployment Guide

## Quick Deploy Options:

### 1. Streamlit Community Cloud (Recommended)
```bash
# Push to GitHub first
git add .
git commit -m "Deploy submission processor"
git push origin main

# Then go to: https://share.streamlit.io
# Connect your GitHub repo and deploy!
```

### 2. Railway
```bash
# Install Railway CLI: https://railway.app/cli
railway login
railway init
railway up
```

### 3. Heroku
```bash
# Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
heroku create your-app-name
heroku config:set GOOGLE_CLIENT_ID="your_value"
heroku config:set GOOGLE_CLIENT_SECRET="your_value"
git push heroku main
```

### 4. Docker (Any Cloud Provider)
```bash
# Build and run locally first
docker build -t submission-processor .
docker run -p 8501:8501 submission-processor

# Then deploy to your preferred cloud provider
```

## Environment Variables Needed:
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- GOOGLE_TOKEN_PATH (optional, defaults to token.json)

## Important Notes:
- OAuth token will need to be regenerated in production
- Make sure to set up proper secrets management
- Consider using environment-specific configurations
