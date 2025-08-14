#!/usr/bin/env python3
"""
Test Google Docs integration
"""

import os
from google_docs import get_google_docs_service, validate_google_docs_url

def test_google_docs_setup():
    """Test if Google Docs integration is properly configured."""
    
    print("🔍 Testing Google Docs Integration Setup...")
    
    # Check if service account file exists
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service-account-key.json')
    print(f"📁 Service account file: {service_account_file}")
    
    if os.path.exists(service_account_file):
        print(f"✅ Service account file found: {service_account_file}")
    else:
        print(f"❌ Service account file NOT found: {service_account_file}")
        print("   You need to create a Google Cloud service account and download the JSON key file.")
        return False
    
    # Test Google Docs service
    print("\n🔧 Testing Google Docs service...")
    service = get_google_docs_service()
    
    if service:
        print("✅ Google Docs service initialized successfully")
        return True
    else:
        print("❌ Google Docs service failed to initialize")
        print("   Check your service account credentials and permissions")
        return False

def test_url_validation():
    """Test URL validation."""
    print("\n🔗 Testing URL validation...")
    
    # Test valid URLs
    test_urls = [
        "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZgKQbE8q5J6H8Q/edit",
        "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZgKQbE8q5J6H8Q/view",
        "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZgKQbE8q5J6H8Q"
    ]
    
    for url in test_urls:
        is_valid, doc_id = validate_google_docs_url(url)
        if is_valid:
            print(f"✅ Valid URL: {url}")
            print(f"   Document ID: {doc_id}")
        else:
            print(f"❌ Invalid URL: {url}")
            print(f"   Error: {doc_id}")

if __name__ == "__main__":
    print("🚀 Google Docs Integration Test")
    print("=" * 40)
    
    setup_ok = test_google_docs_setup()
    test_url_validation()
    
    if setup_ok:
        print("\n✅ Google Docs integration is ready!")
        print("\n📋 Next steps:")
        print("1. Create a Google Cloud project")
        print("2. Enable Google Docs API")
        print("3. Create a service account")
        print("4. Download the JSON key file as 'service-account-key.json'")
        print("5. Share documents with the service account email")
    else:
        print("\n❌ Google Docs integration needs setup")
        print("   See GOOGLE_DOCS_SETUP.md for instructions") 