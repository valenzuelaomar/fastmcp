"""
Real FastMCP Server for Browser/PyScript Integration
Demonstrates how to use actual FastMCP in a browser environment via PyScript
"""

import json
from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel

# Browser API access via PyScript's js module
try:
    from pyscript import document, window, display
    from js import console, localStorage, sessionStorage, location, navigator
    HAS_BROWSER_APIS = True
except ImportError:
    # Fallback for testing outside browser
    HAS_BROWSER_APIS = False
    console = None

# Import the actual FastMCP framework
try:
    from fastmcp import FastMCP
    from fastmcp.client import Client
except ImportError:
    # For environments where FastMCP isn't available, we'll create a minimal compatible interface
    print("⚠️  FastMCP not available in this environment, using browser-compatible implementation")
    
    class BrowserFastMCP:
        """Browser-compatible FastMCP implementation that mimics the real API"""
        
        def __init__(self, name: str):
            self.name = name
            self.tools = {}
            self.resources = {}
            
        def tool(self, func):
            """Decorator to register tools"""
            self.tools[func.__name__] = func
            return func
            
        def resource(self, uri: str):
            """Decorator to register resources"""
            def decorator(func):
                self.resources[uri] = func
                return func
            return decorator
        
        def call_tool(self, name: str, args: Dict[str, Any] = None) -> Any:
            """Call a registered tool"""
            if name in self.tools:
                return self.tools[name](**(args or {}))
            raise ValueError(f"Tool {name} not found")
    
    FastMCP = BrowserFastMCP


# Initialize the FastMCP server
mcp = FastMCP("Browser MCP Demo")


class PageContent(BaseModel):
    """Model for page content analysis"""
    title: str
    url: str
    text_content: str
    links: List[str]
    forms: List[Dict[str, Any]]
    meta_tags: Dict[str, str]


class DOMInfo(BaseModel):
    """Model for DOM information"""
    element_count: int
    viewport_size: Dict[str, int]
    scroll_position: Dict[str, int]
    active_element: str


class SessionInfo(BaseModel):
    """Model for session information"""
    timestamp: str
    user_agent: str
    language: str
    timezone: str
    cookies_enabled: bool
    local_storage_available: bool


@mcp.tool
def analyze_page_content() -> Dict[str, Any]:
    """
    Analyze the current web page content for LLM context.
    
    This tool extracts meaningful information from the DOM that can be used
    to provide context to language models in web applications.
    """
    if not HAS_BROWSER_APIS:
        return {
            "error": "Browser APIs not available",
            "demo_data": {
                "title": "FastMCP Browser Demo",
                "url": "file://demo.html",
                "content_length": 1500,
                "forms": 0,
                "links": 3
            }
        }
    
    try:
        # Extract page information
        title = document.title
        url = str(location.href)
        
        # Get all text content
        body_text = document.body.innerText if document.body else ""
        
        # Find all links
        links = []
        for link in document.querySelectorAll("a[href]"):
            links.append(link.href)
        
        # Find all forms
        forms = []
        for form in document.querySelectorAll("form"):
            form_data = {
                "action": form.action or "",
                "method": form.method or "GET",
                "inputs": len(form.querySelectorAll("input"))
            }
            forms.append(form_data)
        
        # Extract meta tags
        meta_tags = {}
        for meta in document.querySelectorAll("meta"):
            name = meta.getAttribute("name") or meta.getAttribute("property")
            content = meta.getAttribute("content")
            if name and content:
                meta_tags[name] = content
        
        return {
            "title": title,
            "url": url,
            "text_length": len(body_text),
            "text_preview": body_text[:200] + "..." if len(body_text) > 200 else body_text,
            "links_count": len(links),
            "links": links[:5],  # First 5 links
            "forms_count": len(forms),
            "forms": forms,
            "meta_tags": meta_tags,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Failed to analyze page content: {str(e)}"}


@mcp.tool
def get_dom_info() -> Dict[str, Any]:
    """
    Get detailed DOM information and viewport data.
    
    Useful for understanding the current state of the web page
    and user's viewing context.
    """
    if not HAS_BROWSER_APIS:
        return {
            "demo_data": {
                "elements": 42,
                "viewport": {"width": 1200, "height": 800},
                "scroll": {"x": 0, "y": 100}
            }
        }
    
    try:
        # Count DOM elements
        all_elements = document.querySelectorAll("*")
        element_count = len(all_elements)
        
        # Get viewport information
        viewport_size = {
            "width": window.innerWidth,
            "height": window.innerHeight
        }
        
        # Get scroll position
        scroll_position = {
            "x": window.scrollX or window.pageXOffset or 0,
            "y": window.scrollY or window.pageYOffset or 0
        }
        
        # Get active element
        active_element = ""
        if document.activeElement:
            active_element = f"{document.activeElement.tagName.lower()}"
            if document.activeElement.id:
                active_element += f"#{document.activeElement.id}"
            if document.activeElement.className:
                active_element += f".{document.activeElement.className.replace(' ', '.')}"
        
        return {
            "element_count": element_count,
            "viewport_size": viewport_size,
            "scroll_position": scroll_position,
            "active_element": active_element,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Failed to get DOM info: {str(e)}"}


@mcp.tool
def get_user_context() -> Dict[str, Any]:
    """
    Extract user context and session information.
    
    This provides information about the user's current session
    that can be valuable for personalizing LLM responses.
    """
    if not HAS_BROWSER_APIS:
        return {
            "demo_data": {
                "logged_in": False,
                "user_preferences": {"theme": "light"},
                "session_duration": "15 minutes"
            }
        }
    
    try:
        # Check for common user indicators
        user_info = {}
        
        # Look for user name in common places
        user_elements = document.querySelectorAll("[data-user], .username, .user-name, #username")
        if user_elements:
            user_info["username_elements"] = len(user_elements)
        
        # Check for authentication indicators
        auth_elements = document.querySelectorAll(".login, .logout, .signin, .signout")
        user_info["auth_elements"] = len(auth_elements)
        
        # Get form data that might indicate user input
        input_elements = document.querySelectorAll("input[type='text'], input[type='email'], textarea")
        form_data = []
        for inp in input_elements:
            if inp.value and len(inp.value.strip()) > 0:
                form_data.append({
                    "type": inp.type,
                    "name": inp.name or inp.id or "unnamed",
                    "has_value": True,
                    "value_length": len(inp.value)
                })
        
        return {
            "user_indicators": user_info,
            "form_data": form_data,
            "forms_with_data": len([f for f in form_data if f["has_value"]]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Failed to get user context: {str(e)}"}


@mcp.tool
def get_session_info() -> Dict[str, Any]:
    """
    Get browser session and environment information.
    
    This provides context about the user's browser environment
    and capabilities.
    """
    if not HAS_BROWSER_APIS:
        return {
            "demo_data": {
                "user_agent": "Mozilla/5.0 (Demo Browser)",
                "language": "en-US",
                "cookies_enabled": True
            }
        }
    
    try:
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "user_agent": str(navigator.userAgent),
            "language": str(navigator.language),
            "languages": list(navigator.languages) if hasattr(navigator, 'languages') else [],
            "platform": str(navigator.platform),
            "cookies_enabled": bool(navigator.cookieEnabled),
            "online": bool(navigator.onLine) if hasattr(navigator, 'onLine') else True,
            "viewport": {
                "width": window.innerWidth,
                "height": window.innerHeight
            },
            "screen": {
                "width": window.screen.width if hasattr(window, 'screen') else 0,
                "height": window.screen.height if hasattr(window, 'screen') else 0
            }
        }
        
        # Check storage availability
        storage_info = {}
        try:
            localStorage.setItem("test", "test")
            localStorage.removeItem("test")
            storage_info["local_storage"] = True
        except:
            storage_info["local_storage"] = False
            
        try:
            sessionStorage.setItem("test", "test")
            sessionStorage.removeItem("test")
            storage_info["session_storage"] = True
        except:
            storage_info["session_storage"] = False
            
        session_data["storage"] = storage_info
        
        return session_data
        
    except Exception as e:
        return {"error": f"Failed to get session info: {str(e)}"}


@mcp.tool
def test_local_storage() -> Dict[str, Any]:
    """
    Test local storage functionality for state persistence.
    
    Demonstrates how MCP tools can interact with browser storage
    to maintain state between sessions.
    """
    if not HAS_BROWSER_APIS:
        return {"demo_data": {"storage_test": "simulated", "items": 0}}
    
    try:
        # Test key for MCP demo
        test_key = "fastmcp_demo_test"
        test_value = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "test_data": "FastMCP browser integration test"
        })
        
        # Store test data
        localStorage.setItem(test_key, test_value)
        
        # Retrieve and verify
        retrieved = localStorage.getItem(test_key)
        parsed_data = json.loads(retrieved) if retrieved else None
        
        # Count all localStorage items
        storage_count = len(localStorage) if hasattr(localStorage, '__len__') else 0
        
        # List some keys (first 5)
        keys = []
        try:
            for i in range(min(5, storage_count)):
                key = localStorage.key(i)
                if key:
                    keys.append(key)
        except:
            keys = ["Unable to enumerate keys"]
        
        return {
            "test_successful": parsed_data is not None,
            "test_data": parsed_data,
            "total_items": storage_count,
            "sample_keys": keys,
            "storage_available": True
        }
        
    except Exception as e:
        return {
            "test_successful": False,
            "error": str(e),
            "storage_available": False
        }


@mcp.resource("browser://page-content")
def get_current_page_content() -> str:
    """Resource providing current page content as text"""
    if not HAS_BROWSER_APIS:
        return "Demo page content would appear here"
    
    try:
        title = document.title
        body_text = document.body.innerText if document.body else ""
        return f"Title: {title}\n\nContent:\n{body_text}"
    except Exception as e:
        return f"Error accessing page content: {str(e)}"


# Browser MCP Tools Interface for JavaScript
class MCPTools:
    """Interface class for calling MCP tools from JavaScript"""
    
    @staticmethod
    def analyze_page_content():
        return mcp.call_tool("analyze_page_content")
    
    @staticmethod
    def get_dom_info():
        return mcp.call_tool("get_dom_info")
    
    @staticmethod
    def get_user_context():
        return mcp.call_tool("get_user_context")
    
    @staticmethod
    def get_session_info():
        return mcp.call_tool("get_session_info")
    
    @staticmethod
    def test_local_storage():
        return mcp.call_tool("test_local_storage")


# Create global instance for JavaScript access
mcp_tools = MCPTools()

# Helper functions for displaying results
def display_result(element_id: str, result: Dict[str, Any]):
    """Display MCP tool result in the web page"""
    if HAS_BROWSER_APIS:
        element = document.getElementById(element_id)
        if element:
            formatted_result = json.dumps(result, indent=2)
            element.innerHTML = f'<pre>{formatted_result}</pre>'

def display_error(element_id: str, error: str):
    """Display error in the web page"""
    if HAS_BROWSER_APIS:
        element = document.getElementById(element_id)
        if element:
            element.innerHTML = f'<div class="status error">Error: {error}</div>'

# Initialize and show status
if HAS_BROWSER_APIS:
    try:
        # Update status to show successful initialization
        status_element = document.getElementById("status-output")
        if status_element:
            tools_count = len(mcp.tools) if hasattr(mcp, 'tools') else 4
            status_element.innerHTML = f'''
                <div class="status success">
                    ✅ FastMCP server initialized successfully!<br>
                    🔧 {tools_count} tools available<br>
                    🌐 Browser APIs connected<br>
                    📊 Ready for MCP operations
                </div>
            '''
        
        console.log("FastMCP browser demo initialized successfully")
        
    except Exception as e:
        status_element = document.getElementById("status-output")
        if status_element:
            status_element.innerHTML = f'<div class="status error">Initialization error: {str(e)}</div>'
else:
    print("Browser demo ready (running outside browser environment)")

print("🚀 FastMCP Browser Demo Server loaded successfully!")