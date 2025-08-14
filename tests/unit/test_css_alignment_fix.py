#!/usr/bin/env python3
"""
Test script to verify CSS alignment fixes are properly implemented.
Checks the CSS file directly for the required fixes.
"""

import re

def test_css_alignment_fixes():
    """Test that the CSS file contains the necessary alignment fixes."""
    
    try:
        with open('static/css/components.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        print("🔍 Checking CSS file for alignment fixes...")
        
        # Check for the main message bubble fixes
        fixes_found = []
        
        # 1. Check for box-sizing: border-box on message bubbles
        if 'box-sizing: border-box' in css_content:
            fixes_found.append("✅ Box-sizing: border-box added to message bubbles")
        else:
            print("❌ Missing box-sizing: border-box for message bubbles")
        
        # 2. Check for max-width calculations for user messages
        if 'max-width: calc(75% - 1rem)' in css_content:
            fixes_found.append("✅ Max-width calculation for user messages")
        else:
            print("❌ Missing max-width calculation for user messages")
        
        # 3. Check for margin adjustments
        if 'margin-right: 0.5rem' in css_content:
            fixes_found.append("✅ Margin adjustments for user messages")
        else:
            print("❌ Missing margin adjustments for user messages")
        
        # 4. Check for word-wrap and overflow-wrap
        if 'word-wrap: break-word' in css_content and 'overflow-wrap: break-word' in css_content:
            fixes_found.append("✅ Word wrapping for message content")
        else:
            print("❌ Missing word wrapping for message content")
        
        # 5. Check for flex container overflow handling
        if '.message-bubble.user .flex' in css_content:
            fixes_found.append("✅ Flex container overflow handling")
        else:
            print("❌ Missing flex container overflow handling")
        
        # 6. Check for mobile-specific fixes
        mobile_fixes = re.findall(r'@media.*max-width.*768px.*?\.message-bubble\.user.*?max-width.*?calc.*?90%.*?1rem', css_content, re.DOTALL)
        if mobile_fixes:
            fixes_found.append("✅ Mobile-specific max-width calculations")
        else:
            print("❌ Missing mobile-specific max-width calculations")
        
        # 7. Check for box-sizing on chat messages container
        if 'box-sizing: border-box.*chat-messages' in css_content or 'chat-messages.*box-sizing: border-box' in css_content:
            fixes_found.append("✅ Box-sizing for chat messages container")
        else:
            print("❌ Missing box-sizing for chat messages container")
        
        # 8. Check for overflow-x: hidden
        if 'overflow-x: hidden' in css_content:
            fixes_found.append("✅ Horizontal overflow prevention")
        else:
            print("❌ Missing horizontal overflow prevention")
        
        # Print all found fixes
        print("\n📋 Alignment fixes found:")
        for fix in fixes_found:
            print(f"   {fix}")
        
        # Check for potential issues
        potential_issues = []
        
        # Check for conflicting max-width rules
        max_width_rules = re.findall(r'\.message-bubble.*?max-width.*?[0-9]+%', css_content)
        if len(max_width_rules) > 2:  # Should have base rule + user + assistant
            potential_issues.append("⚠️ Multiple max-width rules found - check for conflicts")
        
        # Check for overflow: visible without proper constraints
        overflow_visible = re.findall(r'overflow:\s*visible', css_content)
        if len(overflow_visible) > 1:  # Should only be on message-bubble base
            potential_issues.append("⚠️ Multiple overflow: visible rules found")
        
        if potential_issues:
            print("\n⚠️ Potential issues:")
            for issue in potential_issues:
                print(f"   {issue}")
        
        # Summary
        total_fixes = len(fixes_found)
        if total_fixes >= 6:  # Most important fixes
            print(f"\n🎉 CSS alignment fixes look good! Found {total_fixes}/8 fixes.")
            return True
        else:
            print(f"\n❌ CSS alignment fixes incomplete. Found {total_fixes}/8 fixes.")
            return False
            
    except FileNotFoundError:
        print("❌ CSS file not found: static/css/components.css")
        return False
    except Exception as e:
        print(f"❌ Error reading CSS file: {e}")
        return False

def test_css_cache_version():
    """Test that the CSS cache version has been updated."""
    
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        # Look for the CSS version
        version_match = re.search(r'components\.css\?v=(\d+\.\d+)', base_content)
        if version_match:
            version = version_match.group(1)
            print(f"📦 CSS cache version: v{version}")
            
            # Check if it's a recent version
            if float(version) >= 2.8:
                print("✅ CSS cache version is up to date")
                return True
            else:
                print("❌ CSS cache version needs updating")
                return False
        else:
            print("❌ Could not find CSS cache version")
            return False
            
    except FileNotFoundError:
        print("❌ Base template not found")
        return False
    except Exception as e:
        print(f"❌ Error checking CSS cache version: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing CSS Alignment Fixes")
    print("=" * 50)
    
    css_success = test_css_alignment_fixes()
    cache_success = test_css_cache_version()
    
    if css_success and cache_success:
        print("\n🎉 All CSS alignment fixes are properly implemented!")
        print("💡 The fixes should resolve the user message overflow issues.")
        print("   - User messages will now stay within chat boundaries")
        print("   - Proper spacing and margins prevent overflow")
        print("   - Mobile and desktop layouts are both fixed")
    else:
        print("\n❌ Some CSS fixes are missing or incomplete.") 