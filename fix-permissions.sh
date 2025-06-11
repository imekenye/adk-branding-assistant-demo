#!/bin/bash
# Fix Cloud Build Permissions Script

echo "🔧 Fixing Cloud Build Permissions"
echo "================================="

PROJECT_ID="my-ai-projects-422803"
SERVICE_ACCOUNT="github-actions-deployer@my-ai-projects-422803.iam.gserviceaccount.com"

echo "📋 Project: $PROJECT_ID"
echo "🔐 Service Account: $SERVICE_ACCOUNT"
echo ""

echo "1️⃣ Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID

echo ""
echo "2️⃣ Adding required IAM roles..."

# Cloud Build permissions
echo "Adding Cloud Build Builder role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudbuild.builds.builder"

# Cloud Run permissions
echo "Adding Cloud Run Admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.admin"

# Storage permissions for build artifacts
echo "Adding Storage Admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.admin"

# Artifact Registry permissions
echo "Adding Artifact Registry Writer role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/artifactregistry.writer"

# Service Account User for Cloud Run
echo "Adding Service Account User role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/iam.serviceAccountUser"

# Cloud Build Service Account role
echo "Adding Cloud Build Service Account role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudbuild.builds.editor"

echo ""
echo "3️⃣ Verification - checking updated permissions..."
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:$SERVICE_ACCOUNT"

echo ""
echo "✅ Permissions update complete!"
echo "🔄 Try the deployment again - it should work now." 