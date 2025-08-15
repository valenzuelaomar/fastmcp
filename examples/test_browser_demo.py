#!/usr/bin/env python3
"""
Test script for browser demo files
"""
import os
import sys

def test_html_files():
    """Test that HTML demo files are properly structured"""
    html_files = [
        'simple_browser_demo.html',
        'pyscript_browser_demo.html'  
    ]
    
    for filename in html_files:
        filepath = os.path.join('examples', filename)
        if not os.path.exists(filepath):
            print(f"❌ {filename}: File not found")
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Basic HTML validation
        if not content.startswith('<!DOCTYPE html>'):
            print(f"❌ {filename}: Missing DOCTYPE")
            continue
            
        if '</html>' not in content:
            print(f"❌ {filename}: Missing closing HTML tag")
            continue
            
        if 'pyscript.net' not in content:
            print(f"❌ {filename}: Missing PyScript CDN")
            continue
            
        if 'py-script' not in content:
            print(f"❌ {filename}: Missing PyScript code")
            continue
            
        print(f"✅ {filename}: Valid HTML structure with PyScript")

def test_python_server():
    """Test that the Python server file imports correctly"""
    # Add src to path for import
    sys.path.insert(0, 'src')
    
    try:
        from examples.browser_mcp_server import mcp
        
        print(f"✅ browser_mcp_server.py: Imports successfully")
        print(f"   Server name: {mcp.name}")
        print(f"   Tools: {len(mcp.tools)} ({', '.join(list(mcp.tools.keys())[:3])}...)")
        print(f"   Resources: {len(mcp.resources)}")
        
        # Test tool registry
        expected_tools = [
            'read_page_text',
            'get_page_metadata', 
            'extract_form_data',
            'make_authenticated_request',
            'get_user_session_info',
            'inject_content'
        ]
        
        for tool in expected_tools:
            if tool in mcp.tools:
                print(f"   ✅ Tool '{tool}' registered")
            else:
                print(f"   ❌ Tool '{tool}' missing")
                
    except ImportError as e:
        print(f"❌ browser_mcp_server.py: Import failed - {e}")
    except Exception as e:
        print(f"❌ browser_mcp_server.py: Error - {e}")

def test_markdown_guide():
    """Test that the integration guide exists and has content"""
    filepath = os.path.join('examples', 'pyscript_integration_guide.md')
    
    if not os.path.exists(filepath):
        print("❌ pyscript_integration_guide.md: File not found")
        return
        
    with open(filepath, 'r') as f:
        content = f.read()
        
    if len(content) < 1000:
        print("❌ pyscript_integration_guide.md: Content too short")
        return
        
    required_sections = [
        'Use Cases',
        'Implementation Approaches', 
        'PyScript Compatibility',
        'Browser Security',
        'Integration Examples'
    ]
    
    for section in required_sections:
        if section not in content:
            print(f"❌ pyscript_integration_guide.md: Missing section '{section}'")
            return
            
    print("✅ pyscript_integration_guide.md: Complete integration guide")

if __name__ == "__main__":
    print("Testing FastMCP PyScript Browser Demo...")
    print("=" * 50)
    
    test_html_files()
    print()
    test_python_server() 
    print()
    test_markdown_guide()
    
    print("=" * 50)
    print("Test completed!")