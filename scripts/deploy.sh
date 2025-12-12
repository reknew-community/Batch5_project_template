#!/bin/bash

# Deployment script

set -e

ENVIRONMENT=${1:-staging}

echo "🚀 Deploying to $ENVIRONMENT..."

# Run tests first
echo "🧪 Running tests..."
./scripts/test.sh

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t your-project:$ENVIRONMENT .

# Deploy based on environment
case $ENVIRONMENT in
    "staging")
        echo "📦 Deploying to staging..."
        # Add staging deployment commands
        echo "Staging deployment completed!"
        ;;
    "production")
        echo "🎯 Deploying to production..."
        # Add production deployment commands
        echo "Production deployment completed!"
        ;;
    *)
        echo "❌ Unknown environment: $ENVIRONMENT"
        echo "Usage: $0 [staging|production]"
        exit 1
        ;;
esac

echo "✅ Deployment to $ENVIRONMENT completed!"
