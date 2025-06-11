#!/bin/bash
# Cloud Build Permissions Diagnostic Script

echo "🔍 Cloud Build Permissions Diagnostic"
echo "======================================"

PROJECT_ID="my-ai-projects-422803"
SERVICE_ACCOUNT="github-actions-deployer@my-ai-projects-422803.iam.gserviceaccount.com"

echo "📋 Project: $PROJECT_ID"
echo "🔐 Service Account: $SERVICE_ACCOUNT"
echo ""

echo "1️⃣ Checking current IAM policy for the service account..."
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:$SERVICE_ACCOUNT"

echo ""
echo "2️⃣ Checking required permissions for Cloud Build..."
echo "Required roles for Cloud Run deployment:"
echo "  - roles/cloudbuild.builds.builder"
echo "  - roles/run.admin" 
echo "  - roles/storage.admin"
echo "  - roles/artifactregistry.writer"
echo "  - roles/iam.serviceAccountUser"

echo ""
echo "3️⃣ Checking Cloud Build API status..."
gcloud services list --enabled --filter="name:cloudbuild.googleapis.com" --format="value(name)" 2>/dev/null || echo "❌ Cloud Build API not enabled"

echo ""
echo "4️⃣ Checking Cloud Build quotas..."
gcloud compute project-info describe --format="yaml(quotas)" | grep -A 5 -B 5 -i build || echo "ℹ️ No quota info available"

echo ""
echo "5️⃣ Getting recent Cloud Build history..."
gcloud builds list --limit=5 --format="table(id,status,createTime,logUrl)" 