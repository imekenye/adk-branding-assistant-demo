#!/bin/bash
# Debug build issues for ADK Branding Assistant

echo "🔍 Debug Build Script for ADK Branding Assistant"
echo "=================================================="

# Function to test minimal build
test_minimal() {
    echo "🧪 Testing minimal build..."
    
    # Backup original files
    cp pyproject.toml pyproject.toml.backup
    cp Dockerfile Dockerfile.backup
    
    # Use minimal versions
    cp pyproject.minimal.toml pyproject.toml
    cp Dockerfile.minimal Dockerfile
    
    echo "📋 Dependencies in minimal build:"
    grep -A 10 "dependencies = \[" pyproject.toml
    
    # Test with uv
    echo "🔧 Testing uv sync with minimal dependencies..."
    uv sync --no-dev
    
    if [ $? -eq 0 ]; then
        echo "✅ Minimal dependencies work!"
        
        echo "🧪 Testing adk command..."
        uv run adk --help
        
        if [ $? -eq 0 ]; then
            echo "✅ adk command works with minimal dependencies!"
        else
            echo "❌ adk command failed with minimal dependencies"
        fi
    else
        echo "❌ Minimal dependencies failed to install"
    fi
    
    # Restore original files
    cp pyproject.toml.backup pyproject.toml
    cp Dockerfile.backup Dockerfile
    rm pyproject.toml.backup Dockerfile.backup
}

# Function to test full build
test_full() {
    echo "🧪 Testing full build..."
    
    echo "📋 Dependencies in full build:"
    grep -A 20 "dependencies = \[" pyproject.toml
    
    # Test with uv
    echo "🔧 Testing uv sync with full dependencies..."
    uv sync --no-dev
    
    if [ $? -eq 0 ]; then
        echo "✅ Full dependencies work!"
        
        echo "🧪 Testing adk command..."
        uv run adk --help
        
        if [ $? -eq 0 ]; then
            echo "✅ adk command works with full dependencies!"
        else
            echo "❌ adk command failed with full dependencies"
        fi
    else
        echo "❌ Full dependencies failed to install"
        echo "This is likely the cause of your Cloud Run build failure!"
    fi
}

# Function to analyze problematic dependencies
analyze_deps() {
    echo "🔍 Analyzing problematic dependencies..."
    
    echo "📦 Heavy dependencies that might cause issues:"
    echo "- google-adk (has many sub-dependencies)"
    echo "- opencv-python (large binary)"
    echo "- numpy (large binary)"
    
    echo "🧪 Testing individual problematic dependencies..."
    
    # Test google-adk
    echo "Testing google-adk..."
    if uv pip show google-adk > /dev/null 2>&1; then
        echo "✅ google-adk is installed"
        echo "📋 google-adk dependencies:"
        uv pip show google-adk | grep "Requires:"
    else
        echo "❌ google-adk not found"
    fi
}

# Main execution
case "${1:-all}" in
    minimal)
        test_minimal
        ;;
    full)
        test_full
        ;;
    analyze)
        analyze_deps
        ;;
    all)
        echo "🚀 Running all tests..."
        test_minimal
        echo ""
        test_full
        echo ""
        analyze_deps
        ;;
    *)
        echo "Usage: $0 [minimal|full|analyze|all]"
        echo "  minimal - Test with minimal dependencies"
        echo "  full    - Test with full dependencies"
        echo "  analyze - Analyze problematic dependencies"
        echo "  all     - Run all tests (default)"
        ;;
esac

echo ""
echo "🎯 Next steps based on results:"
echo "1. If minimal works but full doesn't -> Use minimal for deployment"
echo "2. If both fail -> Check uv/Python installation"
echo "3. If both work locally but Cloud Run fails -> Check Cloud Run logs" 