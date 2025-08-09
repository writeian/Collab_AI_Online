#!/usr/bin/env python3
"""
Test script to verify industry-standard padding across all pages.
Checks that pages have proper container structure and padding.
"""

import re
import os

def test_page_padding():
    """Test that all pages have proper industry-standard padding."""
    
    print("🔍 Testing industry-standard padding across all pages...")
    
    # Pages to check
    pages_to_check = [
        'templates/chat/edit.html',
        'templates/login.html', 
        'templates/register.html',
        'templates/profile.html',
        'templates/room/view.html',
        'templates/room/index.html'
    ]
    
    results = []
    
    for page_path in pages_to_check:
        if not os.path.exists(page_path):
            print(f"⚠️  Page not found: {page_path}")
            continue
            
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        page_name = os.path.basename(page_path)
        print(f"\n📄 Checking {page_name}...")
        
        # Check for proper container structure
        has_container = 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8' in content
        has_proper_padding = has_container
        
        # Check for proper form styling (for forms)
        if 'form method="POST"' in content:
            has_form_styling = all([
                'w-full px-3 py-2' in content,  # Input styling
                'border border-border rounded-md' in content,  # Border styling
                'focus:outline-none focus:ring-2' in content,  # Focus styling
            ])
        else:
            has_form_styling = True  # Not applicable
        
        # Check for proper card structure
        has_card_structure = 'bg-card border border-border rounded-lg' in content
        
        # Check for proper button styling
        has_button_styling = any([
            'bg-primary text-primary-foreground' in content,
            'border border-border rounded-md' in content
        ])
        
        # Overall assessment
        is_compliant = all([has_proper_padding, has_form_styling, has_card_structure, has_button_styling])
        
        results.append({
            'page': page_name,
            'has_container': has_container,
            'has_form_styling': has_form_styling,
            'has_card_structure': has_card_structure,
            'has_button_styling': has_button_styling,
            'is_compliant': is_compliant
        })
        
        # Print results
        if has_container:
            print("  ✅ Proper container structure")
        else:
            print("  ❌ Missing proper container structure")
            
        if has_form_styling:
            print("  ✅ Proper form styling")
        else:
            print("  ❌ Missing proper form styling")
            
        if has_card_structure:
            print("  ✅ Proper card structure")
        else:
            print("  ❌ Missing proper card structure")
            
        if has_button_styling:
            print("  ✅ Proper button styling")
        else:
            print("  ❌ Missing proper button styling")
    
    # Summary
    print(f"\n📊 Summary:")
    compliant_pages = [r for r in results if r['is_compliant']]
    total_pages = len(results)
    
    print(f"  ✅ Compliant pages: {len(compliant_pages)}/{total_pages}")
    
    if len(compliant_pages) == total_pages:
        print("  🎉 All pages have industry-standard padding!")
        return True
    else:
        print("  ⚠️  Some pages need padding improvements:")
        for result in results:
            if not result['is_compliant']:
                print(f"    - {result['page']}")
        return False

def test_css_cache_version():
    """Test that CSS cache version was updated."""
    
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for updated CSS version
        if 'css/components.css?v=3.2' in content:
            print("✅ CSS cache version updated to v3.2")
            return True
        else:
            print("❌ CSS cache version not updated")
            return False
    except Exception as e:
        print(f"❌ Error checking CSS cache version: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Industry-Standard Padding Compliance")
    print("=" * 50)
    
    padding_ok = test_page_padding()
    css_ok = test_css_cache_version()
    
    print("\n" + "=" * 50)
    if padding_ok and css_ok:
        print("🎉 All tests passed! Pages have industry-standard padding.")
    else:
        print("⚠️  Some issues found. Please review the results above.") 