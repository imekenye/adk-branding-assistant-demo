#!/bin/bash
# Test Docker build locally before deploying

echo "🐳 Testing Docker build locally..."

# Clean up any previous builds
docker rmi adk-branding-assistant:test 2>/dev/null || true

# Build the image
echo "🏗️ Building Docker image..."
docker build -t adk-branding-assistant:test . --progress=plain

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    
    echo "🚀 Testing container startup..."
    # Run container in background
    CONTAINER_ID=$(docker run -d -p 8001:8000 adk-branding-assistant:test)
    
    # Wait a moment for startup
    sleep 5
    
    # Test health endpoint
    echo "🧪 Testing health endpoint..."
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ Container is running and healthy!"
    else
        echo "⚠️  Health check failed"
        docker logs $CONTAINER_ID
    fi
    
    # Clean up
    docker stop $CONTAINER_ID > /dev/null
    docker rm $CONTAINER_ID > /dev/null
    
    echo "🎉 Local Docker test completed successfully!"
else
    echo "❌ Docker build failed!"
    exit 1
fi 