# FastMCP Browser Integration with PyScript

This guide demonstrates how to integrate FastMCP with PyScript to run MCP servers directly in web browsers, enabling rich web application context for LLMs.

## Overview

The FastMCP browser integration allows you to:

- **Provide Web Context**: Give LLMs access to current page content, DOM state, and user interactions
- **Authenticated Operations**: Use the user's existing session and cookies for API calls
- **Real-time Updates**: Dynamically update page content based on LLM responses
- **Seamless Integration**: Embed MCP functionality directly into web applications

## Use Cases

### 1. Context-Aware Chatbots

```html
<!-- Chatbot that understands the current page -->
<script type="py">
@mcp.tool
def get_page_context() -> dict:
    """Extract current page context for chatbot"""
    return {
        "title": document.title,
        "content": document.body.innerText[:1000],
        "form_data": extract_form_data(),
        "user_state": get_user_session_data()
    }
</script>
```

### 2. Dynamic Content Generation

```html
<!-- Tools that can modify page content -->
<script type="py">
@mcp.tool
def update_page_content(element_id: str, new_content: str) -> bool:
    """Update page element based on LLM response"""
    element = document.getElementById(element_id)
    if element:
        element.innerHTML = new_content
        return True
    return False
</script>
```

### 3. Authenticated API Integration

```html
<!-- Make API calls using user's session -->
<script type="py">
@mcp.tool
async def fetch_user_data(endpoint: str) -> dict:
    """Fetch data using user's authentication"""
    response = await fetch(endpoint, {
        'credentials': 'include',  # Include cookies
        'headers': get_auth_headers()
    })
    return await response.json()
</script>
```

## Implementation Guide

### 1. Basic Setup

Create an HTML file with PyScript and FastMCP:

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://pyscript.net/releases/2025.8.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2025.8.1/core.js"></script>
</head>
<body>
    <py-config>
        packages = ["fastmcp", "pydantic"]
    </py-config>
    
    <script type="py" src="mcp_server.py"></script>
</body>
</html>
```

### 2. Create MCP Tools

Define browser-specific MCP tools in `mcp_server.py`:

```python
from fastmcp import FastMCP
from pyscript import document, window

mcp = FastMCP("Browser MCP Server")

@mcp.tool
def analyze_page_content() -> dict:
    """Analyze current web page for LLM context"""
    return {
        "title": document.title,
        "url": str(window.location.href),
        "text_content": document.body.innerText,
        "links": [a.href for a in document.querySelectorAll("a[href]")],
        "forms": analyze_forms(),
        "meta_data": extract_meta_tags()
    }

@mcp.tool
def get_user_session() -> dict:
    """Extract user session information"""
    return {
        "logged_in": check_auth_state(),
        "user_data": extract_user_data(),
        "preferences": get_user_preferences(),
        "session_id": get_session_identifier()
    }

@mcp.tool
def make_authenticated_request(url: str, method: str = "GET") -> dict:
    """Make API request with user's authentication"""
    # Use fetch API with credentials: 'include'
    return make_request_with_cookies(url, method)
```

### 3. Browser-Specific Features

#### DOM Access
```python
@mcp.tool
def get_form_data() -> dict:
    """Extract all form data from the page"""
    forms = {}
    for form in document.querySelectorAll("form"):
        form_data = {}
        for input_elem in form.querySelectorAll("input, select, textarea"):
            if input_elem.name:
                form_data[input_elem.name] = input_elem.value
        forms[form.id or form.action or "unnamed"] = form_data
    return forms
```

#### Local Storage Integration
```python
@mcp.tool
def store_conversation_context(context: dict) -> bool:
    """Store conversation context in browser storage"""
    from js import localStorage
    import json
    
    try:
        localStorage.setItem("mcp_context", json.dumps(context))
        return True
    except Exception:
        return False

@mcp.tool
def get_stored_context() -> dict:
    """Retrieve stored conversation context"""
    from js import localStorage
    import json
    
    try:
        stored = localStorage.getItem("mcp_context")
        return json.loads(stored) if stored else {}
    except Exception:
        return {}
```

#### Cookie and Session Access
```python
@mcp.tool
def get_session_info() -> dict:
    """Get browser session information"""
    from js import navigator, location
    
    return {
        "user_agent": str(navigator.userAgent),
        "language": str(navigator.language),
        "current_url": str(location.href),
        "referrer": str(document.referrer),
        "cookies_enabled": bool(navigator.cookieEnabled)
    }
```

## Compatibility Considerations

### PyScript Environment
- **Limited Packages**: Not all Python packages work in PyScript/Pyodide
- **Async Handling**: Use PyScript's async capabilities for non-blocking operations
- **Memory Constraints**: Browser environments have memory limitations

### FastMCP Adaptations
For full compatibility, create a browser-compatible FastMCP wrapper:

```python
class BrowserFastMCP:
    """Browser-optimized FastMCP implementation"""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.resources = {}
    
    def tool(self, func):
        """Register tool with browser-safe execution"""
        self.tools[func.__name__] = func
        return func
    
    def call_tool(self, name: str, args: dict = None):
        """Execute tool with error handling"""
        try:
            return self.tools[name](**(args or {}))
        except Exception as e:
            return {"error": str(e)}
```

## Security Considerations

### Same-Origin Policy
- Browser security restrictions apply
- Cross-origin requests need proper CORS headers
- Local file access is limited

### Data Privacy
- Be mindful of sensitive data in page content
- Implement proper sanitization for user inputs
- Consider privacy implications of context extraction

### Authentication
```python
@mcp.tool
def make_secure_request(url: str, data: dict = None) -> dict:
    """Make authenticated request with proper security"""
    # Validate URL is allowed
    if not is_allowed_domain(url):
        return {"error": "Domain not allowed"}
    
    # Include CSRF protection
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json"
    }
    
    # Get CSRF token from page
    csrf_token = get_csrf_token()
    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token
    
    return make_request(url, headers, data)
```

## Complete Example

See `examples/browser_pyscript_demo.html` for a full working demonstration that includes:

- ✅ Real FastMCP integration (not mock)
- 🌐 DOM content analysis
- 👤 User session extraction
- 💾 Local storage tools
- 🔧 Browser API access
- 📊 Live status updates

## Running the Demo

1. Clone the FastMCP repository
2. Open `examples/browser_pyscript_demo.html` in a modern web browser
3. The demo will automatically initialize and show available tools
4. Click the buttons to test different MCP capabilities

## Integration Patterns

### For Existing Web Apps
```javascript
// Initialize MCP integration
window.initializeMCP = async function(config) {
    // Load PyScript dynamically
    await loadPyScript();
    
    // Initialize MCP server
    await pyodide.runPython(`
        mcp = FastMCP("${config.serverName}")
        # Add your tools here
    `);
    
    // Create interface for your app
    window.mcpTools = {
        analyzeContent: () => pyodide.runPython("mcp.call_tool('analyze_page_content')"),
        getUserContext: () => pyodide.runPython("mcp.call_tool('get_user_context')")
    };
};
```

### For Chat Interfaces
```python
@mcp.tool
def get_chat_context() -> dict:
    """Get context for chat interface"""
    return {
        "page_title": document.title,
        "page_content": get_relevant_content(),
        "user_inputs": get_recent_user_inputs(),
        "conversation_history": get_stored_conversation(),
        "user_preferences": get_user_settings()
    }

@mcp.tool
def update_chat_ui(message: str, sender: str) -> bool:
    """Update chat interface with new message"""
    chat_container = document.getElementById("chat-messages")
    if chat_container:
        message_elem = document.createElement("div")
        message_elem.className = f"message {sender}"
        message_elem.textContent = message
        chat_container.appendChild(message_elem)
        chat_container.scrollTop = chat_container.scrollHeight
        return True
    return False
```

This integration enables powerful web-native MCP servers that can provide rich context to LLMs while maintaining the security and capabilities of the browser environment.