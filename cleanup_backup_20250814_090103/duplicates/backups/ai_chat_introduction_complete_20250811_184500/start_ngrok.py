#!/usr/bin/env python3
"""
Start ngrok tunnel for mobile access from public WiFi
"""

from pyngrok import ngrok
import time

def start_ngrok_tunnel():
    """Start ngrok tunnel for Flask app"""
    print("🚀 Starting ngrok tunnel for mobile access...")
    print("=" * 50)
    
    try:
        # Start ngrok tunnel
        public_url = ngrok.connect(5000)
        print(f"✅ ngrok tunnel started!")
        print(f"🌐 Public URL: {public_url}")
        print(f"📱 Access from your phone: {public_url}")
        print("\n" + "=" * 50)
        print("📋 Next steps:")
        print("   1. Copy the URL above")
        print("   2. Open it on your phone")
        print("   3. Login/register to test the mobile accordion")
        print("   4. Go to Room Creation to see the rubric accordion")
        print("\n⏹️  Press Ctrl+C to stop the tunnel")
        print("=" * 50)
        
        # Keep the tunnel open
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping ngrok tunnel...")
        ngrok.kill()
        print("✅ Tunnel stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have ngrok installed and authenticated")

if __name__ == "__main__":
    start_ngrok_tunnel() 