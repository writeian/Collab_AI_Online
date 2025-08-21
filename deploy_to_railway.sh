#!/bin/bash

# Railway Deployment Script for AI Collab Online
# This script helps prepare and deploy your application to Railway

echo "🚀 Railway Deployment Script for AI Collab Online"
echo "=================================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
else
    echo "✅ Railway CLI found"
fi

# Check if we're in the right directory
if [ ! -f "wsgi.py" ] || [ ! -f "Procfile" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project structure verified"

# Check if all required files exist
echo "📋 Checking required files..."
required_files=("Procfile" "railway.toml" "requirements_railway.txt" "wsgi.py")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file found"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "🔧 Railway Configuration:"
echo "========================="
echo "• Procfile: $(cat Procfile)"
echo "• Health check: /health"
echo "• WSGI entry point: wsgi.py"
echo "• Requirements: requirements_railway.txt"

echo ""
echo "📝 Next Steps:"
echo "=============="
echo "1. Login to Railway: railway login"
echo "2. Create new project: railway init"
echo "3. Set environment variables:"
echo "   - ANTHROPIC_API_KEY=your_key_here"
echo "   - SECRET_KEY=your_secret_here"
echo "   - FLASK_ENV=production"
echo "4. Deploy: railway up"
echo ""
echo "📖 For detailed instructions, see: RAILWAY_DEPLOYMENT.md"
echo ""
echo "🎯 Your application is ready for Railway deployment!"

