#!/usr/bin/env python3
"""
Test script to verify mobile access to the Flask application
"""

import requests
import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Could not determine IP"

def test_connection():
    """Test the Flask application connection"""
    print("🌐 Testing Flask Application Access")
    print("=" * 50)
    
    # Test URLs
    urls = [
        "http://127.0.0.1:5000",
        "http://localhost:5000",
        "http://192.168.5.98:5000",
        "http://10.26.8.133:5000"
    ]
    
    local_ip = get_local_ip()
    if local_ip != "Could not determine IP":
        urls.append(f"http://{local_ip}:5000")
    
    print(f"📱 Your local IP address: {local_ip}")
    print(f"🖥️  Flask app should be accessible at:")
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} - WORKING")
                if "AI Collaboration" in response.text:
                    print(f"   📄 Landing page detected")
                elif "Login" in response.text:
                    print(f"   🔐 Login page detected")
                else:
                    print(f"   ❓ Unknown page content")
            else:
                print(f"❌ {url} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - Connection refused")
        except requests.exceptions.Timeout:
            print(f"⏰ {url} - Timeout")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    
    print("\n" + "=" * 50)
    print("📱 For mobile access:")
    print(f"   1. Make sure your phone is on the same WiFi")
    print(f"   2. Try: http://{local_ip}:5000")
    print(f"   3. Or try: http://192.168.5.98:5000")
    print(f"   4. Or try: http://10.26.8.133:5000")
    print("\n🔧 If none work, check:")
    print("   • Windows Firewall settings")
    print("   • Antivirus software")
    print("   • Router settings")

if __name__ == "__main__":
    test_connection() 