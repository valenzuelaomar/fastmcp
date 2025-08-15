"""
Browser-compatible FastMCP Server Example

This example shows how to adapt FastMCP for browser environments,
with tools that can access web page content and make authenticated requests.
"""

from fastmcp import FastMCP
from typing import Dict, Any, Optional
import asyncio

# Create a browser-friendly MCP server
mcp = FastMCP("Browser Web Assistant")

@mcp.tool
async def read_page_text(selector: str = "body") -> str:
    """
    Read text content from the current web page using CSS selector.
    Useful for LLMs to understand what's currently displayed.
    
    Args:
        selector: CSS selector to target specific elements (default: "body")
    """
    # This would be implemented using PyScript's DOM access
    # In actual browser environment, this would use:
    # from js import document
    # element = document.querySelector(selector)
    # return element.textContent if element else "Element not found"
    return f"[Browser] Would read content from selector: {selector}"

@mcp.tool  
async def get_page_metadata() -> Dict[str, str]:
    """
    Extract metadata from the current page (title, URL, meta tags, etc.).
    Provides context about the current page to the LLM.
    """
    # In browser environment:
    # from js import document
    # return {
    #     "title": document.title,
    #     "url": document.location.href,
    #     "description": document.querySelector('meta[name="description"]')?.content || "",
    #     "keywords": document.querySelector('meta[name="keywords"]')?.content || ""
    # }
    return {
        "title": "[Browser] Current Page Title",
        "url": "[Browser] https://example.com",
        "description": "Page description from meta tag",
        "keywords": "web, mcp, fastmcp"
    }

@mcp.tool
async def extract_form_data(form_selector: str = "form") -> Dict[str, Any]:
    """
    Extract current values from web forms on the page.
    Allows LLM to understand user input and form state.
    
    Args:
        form_selector: CSS selector for the form to analyze
    """
    # Browser implementation would iterate through form elements:
    # form = document.querySelector(form_selector)
    # Extract input values, selections, etc.
    return {
        "form_found": True,
        "fields": {
            "username": "user_input_value",
            "email": "user@example.com",
            "preferences": ["option1", "option2"]
        }
    }

@mcp.tool
async def make_authenticated_request(
    url: str, 
    method: str = "GET", 
    include_cookies: bool = True
) -> str:
    """
    Make HTTP request with user's authentication context.
    This allows the LLM to access APIs the user has access to.
    
    Args:
        url: The URL to request
        method: HTTP method (GET, POST, etc.)
        include_cookies: Whether to include cookies for authentication
    """
    # Browser implementation using fetch API:
    # from js import fetch
    # response = await fetch(url, {
    #     "method": method,
    #     "credentials": "include" if include_cookies else "omit",
    #     "headers": {"Content-Type": "application/json"}
    # })
    # return await response.text()
    return f"[Browser] Would make {method} request to {url} with cookies: {include_cookies}"

@mcp.tool
async def get_user_session_info() -> Dict[str, Any]:
    """
    Get information about the user's current session.
    Helps LLM understand user context and permissions.
    """
    # Browser implementation:
    # from js import document, navigator, localStorage
    # return {
    #     "cookies": document.cookie,
    #     "localStorage_keys": list(localStorage.keys()),
    #     "userAgent": navigator.userAgent,
    #     "language": navigator.language
    # }
    return {
        "session_active": True,
        "user_preferences": {"theme": "dark", "language": "en"},
        "permissions": ["read", "write"],
        "browser": "Chrome/Safari/Firefox"
    }

@mcp.tool
async def inject_content(selector: str, content: str, mode: str = "replace") -> str:
    """
    Inject content into the web page at specified location.
    Allows LLM to make live updates to the UI.
    
    Args:
        selector: CSS selector for target element
        content: HTML/text content to inject
        mode: How to inject - "replace", "append", "prepend"
    """
    # Browser implementation:
    # element = document.querySelector(selector)
    # if mode == "replace":
    #     element.innerHTML = content
    # elif mode == "append":
    #     element.innerHTML += content
    # elif mode == "prepend":
    #     element.innerHTML = content + element.innerHTML
    return f"[Browser] Would {mode} content in {selector}: {content[:50]}..."

@mcp.resource("page://current")
async def current_page_resource() -> str:
    """Resource providing the current page's full content"""
    return "[Browser] Full current page HTML content would be returned here"

@mcp.resource("session://user")
async def user_session_resource() -> Dict[str, Any]:
    """Resource providing user session data"""
    return {
        "authenticated": True,
        "user_id": "user_123",
        "permissions": ["read_content", "make_requests"],
        "session_start": "2024-01-15T10:30:00Z"
    }

@mcp.prompt("web_context")
async def web_context_prompt(task: str) -> str:
    """
    Generate a prompt with current web page context for the LLM.
    
    Args:
        task: The task the LLM should perform
    """
    return f"""
You are an AI assistant with access to the user's current web browser session.

Current Context:
- Page: [Browser] Current page title and URL
- Available Tools: {list(mcp.tools.keys())}
- User Task: {task}

You can:
1. Read content from the current page
2. Make authenticated requests using the user's cookies
3. Extract form data and user inputs
4. Update page content dynamically
5. Access user session information

How can I help you with: {task}
"""

# Export the server for use in different contexts
__all__ = ["mcp"]

if __name__ == "__main__":
    # This would run in a standard Python environment
    # In browser, the server would be imported and used directly
    print(f"FastMCP Browser Server '{mcp.name}' ready")
    print(f"Tools: {list(mcp.tools.keys())}")
    print(f"Resources: {list(mcp.resources.keys())}")
    print(f"Prompts: {list(mcp.prompts.keys())}")