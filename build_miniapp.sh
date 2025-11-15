#!/bin/bash
# Build script for Telegram Mini App
# Run this before deploying to production

echo "🔨 Building Telegram Mini App..."

cd client

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the app
echo "⚡ Building production bundle..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Mini App built successfully!"
    echo "📁 Build output: client/dist/"
    ls -lah dist/
else
    echo "❌ Build failed!"
    exit 1
fi
