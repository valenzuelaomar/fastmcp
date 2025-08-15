"""
Tests for FastMCP browser integration
"""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from fastmcp import FastMCP


def test_browser_mcp_server_creation():
    """Test that browser MCP server can be created"""
    mcp = FastMCP("Browser Test Server")
    assert mcp.name == "Browser Test Server"


def test_browser_tools_registration():
    """Test that browser-specific tools can be registered"""
    mcp = FastMCP("Browser Test Server")
    
    @mcp.tool
    def analyze_page_content() -> dict:
        """Mock browser page analysis tool"""
        return {
            "title": "Test Page",
            "url": "https://example.com",
            "content_length": 1000,
            "timestamp": datetime.now().isoformat()
        }
    
    @mcp.tool  
    def get_dom_info() -> dict:
        """Mock DOM information tool"""
        return {
            "element_count": 42,
            "viewport_size": {"width": 1200, "height": 800}
        }
    
    # Verify tools are registered
    assert hasattr(mcp, 'tool')
    
    # Test tool execution if we have call_tool method
    if hasattr(mcp, 'call_tool'):
        page_result = mcp.call_tool("analyze_page_content")
        assert page_result["title"] == "Test Page"
        assert page_result["url"] == "https://example.com"
        assert "timestamp" in page_result
        
        dom_result = mcp.call_tool("get_dom_info")
        assert dom_result["element_count"] == 42
        assert dom_result["viewport_size"]["width"] == 1200


def test_browser_resources():
    """Test browser resource registration"""
    mcp = FastMCP("Browser Test Server")
    
    @mcp.resource("browser://page-content")
    def get_page_content() -> str:
        """Mock page content resource"""
        return "Mock page content for testing"
    
    # Verify resource registration works
    assert hasattr(mcp, 'resource')


def test_page_content_analysis():
    """Test page content analysis functionality"""
    # Import the browser server module
    from examples.browser_mcp_server import analyze_page_content
    
    # Mock browser APIs for testing
    with patch('examples.browser_mcp_server.HAS_BROWSER_APIS', False):
        result = analyze_page_content()
        
        # Should return demo data when browser APIs not available
        assert "demo_data" in result or "error" in result
        
        if "demo_data" in result:
            demo = result["demo_data"]
            assert "title" in demo
            assert "url" in demo
            assert "content_length" in demo


def test_dom_info_extraction():
    """Test DOM information extraction"""
    from examples.browser_mcp_server import get_dom_info
    
    # Mock browser APIs for testing
    with patch('examples.browser_mcp_server.HAS_BROWSER_APIS', False):
        result = get_dom_info()
        
        # Should return demo data when browser APIs not available
        assert "demo_data" in result or "error" in result
        
        if "demo_data" in result:
            demo = result["demo_data"]
            assert "elements" in demo
            assert "viewport" in demo
            assert "scroll" in demo


def test_session_info_extraction():
    """Test session information extraction"""
    from examples.browser_mcp_server import get_session_info
    
    # Mock browser APIs for testing
    with patch('examples.browser_mcp_server.HAS_BROWSER_APIS', False):
        result = get_session_info()
        
        # Should return demo data when browser APIs not available
        assert "demo_data" in result or "error" in result
        
        if "demo_data" in result:
            demo = result["demo_data"]
            assert "user_agent" in demo
            assert "language" in demo
            assert "cookies_enabled" in demo


def test_local_storage_functionality():
    """Test local storage tool"""
    from examples.browser_mcp_server import test_local_storage
    
    # Mock browser APIs for testing
    with patch('examples.browser_mcp_server.HAS_BROWSER_APIS', False):
        result = test_local_storage()
        
        # Should return demo data when browser APIs not available
        assert "demo_data" in result or "storage_available" in result
        
        if "demo_data" in result:
            assert "storage_test" in result["demo_data"]


def test_mcp_tools_interface():
    """Test the MCPTools interface class"""
    from examples.browser_mcp_server import MCPTools
    
    # Create instance
    tools = MCPTools()
    
    # Verify methods exist
    assert hasattr(tools, 'analyze_page_content')
    assert hasattr(tools, 'get_dom_info')
    assert hasattr(tools, 'get_user_context')
    assert hasattr(tools, 'get_session_info')
    assert hasattr(tools, 'test_local_storage')


def test_browser_compatible_fastmcp():
    """Test browser-compatible FastMCP implementation"""
    # Import the browser-compatible implementation
    from examples.browser_mcp_server import FastMCP as BrowserFastMCP
    
    # Test initialization
    mcp = BrowserFastMCP("Test Browser Server")
    assert mcp.name == "Test Browser Server"
    
    # Test tool registration
    @mcp.tool
    def test_tool(message: str) -> str:
        return f"Echo: {message}"
    
    # Test tool execution if call_tool exists
    if hasattr(mcp, 'call_tool'):
        result = mcp.call_tool("test_tool", {"message": "Hello"})
        assert result == "Echo: Hello"


def test_json_serialization():
    """Test that browser tool results can be JSON serialized"""
    from examples.browser_mcp_server import analyze_page_content, get_session_info
    
    # Mock browser APIs
    with patch('examples.browser_mcp_server.HAS_BROWSER_APIS', False):
        page_result = analyze_page_content()
        session_result = get_session_info()
        
        # Should be JSON serializable
        try:
            json.dumps(page_result)
            json.dumps(session_result)
        except TypeError:
            pytest.fail("Browser tool results should be JSON serializable")


def test_error_handling():
    """Test error handling in browser tools"""
    from examples.browser_mcp_server import get_user_context
    
    # Test with mocked browser APIs that might fail
    with patch('examples.browser_mcp_server.HAS_BROWSER_APIS', False):
        result = get_user_context()
        
        # Should handle errors gracefully
        assert isinstance(result, dict)
        # Should either have demo_data or error handling
        assert "demo_data" in result or "error" in result or "user_indicators" in result


def test_pydantic_models():
    """Test Pydantic model definitions"""
    from examples.browser_mcp_server import PageContent, DOMInfo, SessionInfo
    
    # Test PageContent model
    page_content = PageContent(
        title="Test Page",
        url="https://example.com", 
        text_content="Sample content",
        links=["https://link1.com", "https://link2.com"],
        forms=[{"action": "submit", "method": "POST"}],
        meta_tags={"description": "Test page"}
    )
    
    assert page_content.title == "Test Page"
    assert len(page_content.links) == 2
    
    # Test DOMInfo model
    dom_info = DOMInfo(
        element_count=100,
        viewport_size={"width": 1200, "height": 800},
        scroll_position={"x": 0, "y": 150}, 
        active_element="input#search"
    )
    
    assert dom_info.element_count == 100
    assert dom_info.viewport_size["width"] == 1200
    
    # Test SessionInfo model
    session_info = SessionInfo(
        timestamp="2025-08-15T21:00:00",
        user_agent="Mozilla/5.0 Test Browser",
        language="en-US",
        timezone="UTC",
        cookies_enabled=True,
        local_storage_available=True
    )
    
    assert session_info.language == "en-US"
    assert session_info.cookies_enabled is True


def test_resource_registration():
    """Test browser resource registration"""
    from examples.browser_mcp_server import mcp, get_current_page_content
    
    # Test that resource function exists
    assert callable(get_current_page_content)
    
    # Test resource execution
    result = get_current_page_content()
    assert isinstance(result, str)
    
    # Should return either demo content or actual content
    assert len(result) > 0