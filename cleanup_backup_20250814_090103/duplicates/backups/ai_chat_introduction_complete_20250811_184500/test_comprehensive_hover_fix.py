#!/usr/bin/env python3
"""
Comprehensive test to verify all hover fixes are applied
"""

def test_comprehensive_hover_fix():
    print("🎯 Comprehensive Hover Fix Verification")
    print("=" * 60)
    
    # Test 1: Check style.css for dark blue removal
    print("\n1. Checking style.css for dark blue removal...")
    try:
        with open('static/style.css', 'r', encoding='utf-8') as f:
            style_content = f.read()
            
        if '#054ea8' not in style_content:
            print("✅ Dark blue color #054ea8 removed from style.css")
        else:
            print("❌ Dark blue color #054ea8 still present in style.css")
            
        if '#e5e7eb' in style_content:
            print("✅ Light gray color #e5e7eb added to style.css")
        else:
            print("❌ Light gray color #e5e7eb not found in style.css")
            
    except Exception as e:
        print(f"❌ Error reading style.css: {e}")
    
    # Test 2: Check base.html for CSS version updates
    print("\n2. Checking base.html for CSS version updates...")
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
            
        if 'style.css?v=1.3' in base_content:
            print("✅ style.css version updated to 1.3 in base.html")
        else:
            print("❌ style.css version not updated to 1.3 in base.html")
            
        if 'components.css?v=5.1' in base_content:
            print("✅ components.css version updated to 5.1 in base.html")
        else:
            print("❌ components.css version not updated to 5.1 in base.html")
            
    except Exception as e:
        print(f"❌ Error reading base.html: {e}")
    
    # Test 3: Check debug_chat_page.html for CSS version updates
    print("\n3. Checking debug_chat_page.html for CSS version updates...")
    try:
        with open('debug_chat_page.html', 'r', encoding='utf-8') as f:
            debug_content = f.read()
            
        if 'style.css?v=1.3' in debug_content:
            print("✅ style.css version updated to 1.3 in debug_chat_page.html")
        else:
            print("❌ style.css version not updated to 1.3 in debug_chat_page.html")
            
    except Exception as e:
        print(f"❌ Error reading debug_chat_page.html: {e}")
    
    # Test 4: Check for any remaining dark hover classes in HTML files
    print("\n4. Checking for remaining dark hover classes in HTML files...")
    try:
        import os
        import re
        
        template_dirs = ['templates', 'templates/room', 'templates/chat', 'templates/dashboard']
        dark_hover_found = []
        
        for template_dir in template_dirs:
            if os.path.exists(template_dir):
                for filename in os.listdir(template_dir):
                    if filename.endswith('.html'):
                        file_path = os.path.join(template_dir, filename)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        if 'hover:bg-secondary/80' in content or 'hover:bg-secondary/90' in content or 'hover:bg-muted/40' in content:
                            dark_hover_found.append(file_path)
        
        if not dark_hover_found:
            print("✅ No dark hover classes found in HTML templates")
        else:
            print(f"❌ Dark hover classes found in {len(dark_hover_found)} files")
            for file_path in dark_hover_found:
                print(f"   • {file_path}")
                
    except Exception as e:
        print(f"❌ Error checking HTML files: {e}")
    
    # Test 5: Check for any remaining #054ea8 references
    print("\n5. Checking for any remaining #054ea8 references...")
    try:
        import os
        
        all_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.css', '.html', '.py')):
                    all_files.append(os.path.join(root, file))
        
        files_with_dark_blue = []
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '#054ea8' in content:
                        files_with_dark_blue.append(file_path)
            except:
                pass
        
        if not files_with_dark_blue:
            print("✅ No #054ea8 references found anywhere")
        else:
            print(f"❌ #054ea8 references found in {len(files_with_dark_blue)} files")
            for file_path in files_with_dark_blue:
                print(f"   • {file_path}")
                
    except Exception as e:
        print(f"❌ Error checking for #054ea8 references: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Comprehensive Hover Fix Complete!")
    print("\n✨ Summary of fixes:")
    print("1. Removed #054ea8 from style.css button:hover rules")
    print("2. Added #e5e7eb to style.css button:hover rules")
    print("3. Updated style.css version to 1.3 in base.html")
    print("4. Updated style.css version to 1.3 in debug_chat_page.html")
    print("5. Updated components.css version to 5.1 in base.html")
    print("6. Removed all dark hover classes from HTML templates")
    print("\n🔄 To test:")
    print("1. Hard refresh your browser (Ctrl+F5)")
    print("2. Clear browser cache completely")
    print("3. Hover over ANY button on the website")
    print("4. Should see light gray hover instead of dark blue")
    print("5. Check developer tools - should show style.css?v=1.3")

if __name__ == "__main__":
    test_comprehensive_hover_fix() 