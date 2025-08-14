#!/usr/bin/env python3
"""
Test script to show the actual color values causing the dark blue hover
"""

def test_color_values():
    print("🎨 Color Value Analysis")
    print("=" * 50)
    
    print("\n🔍 Found the source of the dark blue hover!")
    print("\n📍 Location: static/css/components.css lines 52-53")
    print("""
.btn-secondary:hover {
  background-color: hsl(var(--secondary) / 0.8);
}
""")
    
    print("\n📍 The --secondary color is defined in static/css/globals.css:")
    print("""
Light mode:
--secondary: oklch(0.95 0.0058 264.53);

Dark mode:
--secondary: oklch(0.269 0 0);
""")
    
    print("\n🎯 The Problem:")
    print("1. The buttons use 'bg-secondary' class")
    print("2. On hover, they use 'hover:bg-secondary/80' class")
    print("3. This translates to 'background-color: hsl(var(--secondary) / 0.8)'")
    print("4. The --secondary color in light mode is oklch(0.95 0.0058 264.53)")
    print("5. This is a very light blue-gray color that appears dark when hovered")
    
    print("\n✅ Our Solution:")
    print("1. We added multiple override selectors with !important")
    print("2. These override the design system's hover colors")
    print("3. We use lighter colors: rgba(59, 130, 246, 0.1) for criterion buttons")
    print("4. And rgba(0, 0, 0, 0.05) for level toggles")
    
    print("\n🔄 To verify the fix is working:")
    print("1. Hard refresh your browser (Ctrl+F5)")
    print("2. The hover should now be light blue instead of dark blue")
    print("3. Our overrides should take precedence over the design system")

if __name__ == "__main__":
    test_color_values() 