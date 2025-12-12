# Deployment Guide

## Docker Deployment

### Build Image

```bash
docker build -t your-project .
```

### Run Container

```bash
docker run -p 8000:8000 your-project
```

### Using Docker Compose

```bash
docker-compose up -d
```

## Cloud Deployment

### Heroku

1. Create a Heroku app
2. Set environment variables
3. Deploy: `git push heroku main`

### AWS Lambda

1. Install serverless framework
2. Configure `serverless.yml`
3. Deploy: `serverless deploy`

### Google Cloud Run

1. Build and push image to Google Container Registry
2. Deploy to Cloud Run
3. Configure environment variables

## Environment Variables

Make sure to set these environment variables in production:

- `APP_ENV=production`
- `DEBUG=false`
- `SECRET_KEY=your-production-secret`
- Any database or API credentials

## Health Checks

The application provides health check endpoints for monitoring:

- `/health` - Basic health check
- `/health/detailed` - Detailed system status
