#!/bin/bash
# Deploy ADK Branding Assistant to Google Cloud Run

set -e  # Exit on any error

PROJECT_ID="my-ai-projects-422803"
SERVICE_NAME="adk-branding-assistant"
REGION="us-central1"

echo "🚀 Deploying ADK Branding Assistant to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first."
    exit 1
fi

# Check authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run 'gcloud auth login'"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

echo "📋 Current project configuration:"
gcloud config get-value project

# Build and deploy with proper error handling
echo "🏗️ Starting deployment..."

# Deploy with better logging and error handling
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars "PORT=8000" \
    --verbosity=debug \
    2>&1 | tee deployment.log

# Check if deployment was successful
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Deployment successful!"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
        --region $REGION \
        --format 'value(status.url)')
    
    echo "🌐 Service URL: $SERVICE_URL"
    echo "🔍 Health check: $SERVICE_URL/health"
    
    # Test the health endpoint
    echo "🧪 Testing health endpoint..."
    if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
        echo "✅ Health check passed!"
    else
        echo "⚠️  Health check failed, but deployment completed"
    fi
else
    echo "❌ Deployment failed. Check deployment.log for details."
    echo "📋 Last 20 lines of log:"
    tail -20 deployment.log
    exit 1
fi 