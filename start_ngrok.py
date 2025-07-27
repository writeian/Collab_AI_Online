#!/usr/bin/env python3
"""
Start ngrok to expose Flask app for mobile testing
"""

from pyngrok import ngrok
import time

def start_ngrok():
    """Start ngrok tunnel to Flask app"""
    
    print("🚀 Starting ngrok tunnel...")
    
    try:
        # Create HTTP tunnel to localhost:5000
        public_url = ngrok.connect(5000)
        
        print("✅ ngrok tunnel created successfully!")
        print(f"🌐 Public URL: {public_url}")
        print("\n📱 You can now access your app from your phone using this URL")
        print("🔗 Share this URL with anyone to test your app")
        print("\n⏹️  Press Ctrl+C to stop the tunnel")
        
        # Keep the tunnel open
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping ngrok tunnel...")
            ngrok.kill()
            print("✅ Tunnel stopped")
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        print("💡 Make sure your Flask app is running on port 5000")

if __name__ == "__main__":
    start_ngrok() 