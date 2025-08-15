# FastMCP + PyScript Browser Integration Guide

This guide demonstrates how to run FastMCP servers in the browser using PyScript, enabling web applications to provide LLM context through the Model Context Protocol.

## Use Cases

### 1. Chatbot Web Integration
- **Problem**: Web chatbots lack access to current page content, user session, and authenticated APIs
- **Solution**: FastMCP tools can read DOM, access cookies, and make authenticated requests

### 2. Context-Aware Web Assistants  
- **Problem**: AI assistants need understanding of current user context in web apps
- **Solution**: MCP resources provide real-time page state, form data, and session info

### 3. Dynamic Content Generation
- **Problem**: AI needs to update web UI based on conversation
- **Solution**: MCP tools can inject content, update elements, and modify page state

## Implementation Approaches

### Approach 1: Pure PyScript (Demo)
```python
# Simplified FastMCP implementation for browser
class FastMCP:
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
    
    def tool(self, func):
        self.tools[func.__name__] = func
        return func

# Browser-specific tools
@mcp.tool
async def get_page_content(selector: str) -> str:
    from js import document
    element = document.querySelector(selector)
    return element.textContent if element else ""
```

### Approach 2: Hybrid Client-Server
```python
# Server runs FastMCP normally
# Browser client connects via WebSocket/HTTP
# Tools proxy between browser DOM and server

# Browser side
async def proxy_dom_access(selector: str) -> str:
    content = document.querySelector(selector).textContent
    return await send_to_server("dom_content", {"content": content})
```

### Approach 3: FastMCP Lite (Recommended)
```python
# Subset of FastMCP optimized for browser
# Direct DOM integration
# Minimal dependencies
```

## PyScript Compatibility Analysis

### Compatible Components ✅
- **Core FastMCP classes**: Server, tool decorators, resource management  
- **Pydantic models**: For data validation and serialization
- **Basic HTTP clients**: Using fetch API through JS interop
- **JSON/dict operations**: Native Python data handling

### Incompatible Components ❌  
- **HTTPX**: Uses threading/async libraries not available in PyScript
- **Rich console**: Terminal formatting not relevant in browser
- **File system operations**: Browser security restrictions
- **Process management**: No subprocess support in browser

### Workarounds 🔧
- Replace HTTPX with JavaScript fetch API
- Use browser console instead of Rich
- Store data in localStorage/sessionStorage instead of files
- Use Web Workers for concurrent operations

## Browser Security Considerations

### Same-Origin Policy
```python
@mcp.tool
async def make_request(url: str) -> str:
    # Must respect CORS policies
    # Can only access same-origin or CORS-enabled endpoints
    response = await fetch(url, {"credentials": "include"})
    return await response.text()
```

### Cookie Access
```python
@mcp.tool  
async def get_auth_context() -> dict:
    # Can access cookies for same domain
    # Enables authenticated API calls
    from js import document
    return {"cookies": document.cookie}
```

### DOM Manipulation
```python
@mcp.tool
async def update_ui(selector: str, content: str) -> str:
    # Full DOM access within page
    # Can modify any page element
    element = document.querySelector(selector)
    element.innerHTML = content
    return "Updated successfully"
```

## Integration Examples

### Example 1: E-commerce Assistant
```python
@mcp.tool
async def get_cart_items() -> list:
    """Read current shopping cart contents"""
    cart_elements = document.querySelectorAll('.cart-item')
    return [item.textContent for item in cart_elements]

@mcp.tool
async def get_product_details() -> dict:
    """Extract current product information"""
    return {
        "name": document.querySelector('.product-name').textContent,
        "price": document.querySelector('.price').textContent,
        "availability": document.querySelector('.stock-status').textContent
    }
```

### Example 2: Dashboard Analytics
```python
@mcp.tool
async def get_dashboard_metrics() -> dict:
    """Read current dashboard metrics"""
    return {
        "revenue": document.querySelector('#revenue').textContent,
        "users": document.querySelector('#active-users').textContent,
        "conversion": document.querySelector('#conversion-rate').textContent
    }

@mcp.tool
async def update_dashboard_filter(date_range: str) -> str:
    """Update dashboard date filter"""
    filter_select = document.querySelector('#date-filter')
    filter_select.value = date_range
    filter_select.dispatchEvent(Event('change'))
    return f"Updated filter to {date_range}"
```

### Example 3: Form Assistant
```python
@mcp.tool
async def analyze_form_fields() -> dict:
    """Analyze current form state and validation"""
    form = document.querySelector('form')
    fields = {}
    
    for input_elem in form.querySelectorAll('input, select, textarea'):
        fields[input_elem.name] = {
            "value": input_elem.value,
            "valid": input_elem.checkValidity(),
            "required": input_elem.required
        }
    
    return fields

@mcp.tool
async def fill_form_field(field_name: str, value: str) -> str:
    """Fill a form field with provided value"""
    field = document.querySelector(f'[name="{field_name}"]')
    if field:
        field.value = value
        field.dispatchEvent(Event('input'))
        return f"Filled {field_name} with {value}"
    return f"Field {field_name} not found"
```

## Performance Considerations

### Memory Management
- PyScript runs in browser memory constraints
- Limit large data processing in tools
- Use streaming for large responses

### Async Operations  
- All browser APIs are async
- FastMCP tools should use async/await
- Consider request timeouts

### Bundle Size
- PyScript loads full Python runtime
- Minimize dependencies
- Consider lazy loading for complex tools

## Getting Started

1. **Create HTML page** with PyScript CDN
2. **Define FastMCP server** with browser-specific tools
3. **Test DOM access** and API integration  
4. **Add error handling** for browser-specific issues
5. **Deploy and test** in target browsers

## Deployment Options

### Static Hosting
- Deploy HTML + PyScript to CDN
- No server required for basic functionality
- Suitable for client-side only features

### Hybrid Architecture
- FastMCP server for heavy processing
- Browser client for UI interaction
- WebSocket connection between them

### Progressive Enhancement
- Start with basic web functionality
- Add MCP features as enhancement layer
- Graceful degradation if PyScript fails

## Future Possibilities

- **WebAssembly integration**: Faster Python execution
- **Service Worker**: Background MCP processing
- **Web Components**: Reusable MCP-enabled UI elements
- **Extension APIs**: Browser extension integration