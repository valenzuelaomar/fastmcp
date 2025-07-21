"""Test OAuth protected resource metadata endpoint."""

import httpx
import pytest

from fastmcp import FastMCP
from fastmcp.server.auth.auth import ClientRegistrationOptions
from fastmcp.server.auth.providers.in_memory import InMemoryOAuthProvider


@pytest.fixture
def oauth_server():
    """Create a FastMCP server with OAuth enabled."""
    server = FastMCP(
        "TestServer",
        auth=InMemoryOAuthProvider(
            issuer_url="http://localhost:8000",
            client_registration_options=ClientRegistrationOptions(enabled=True),
        ),
    )

    @server.tool
    def test_tool() -> str:
        return "test"

    return server


@pytest.fixture
def oauth_app(oauth_server):
    """Create HTTP app with OAuth enabled."""
    return oauth_server.http_app()


async def test_oauth_protected_resource_endpoint(oauth_app):
    """Test that the OAuth protected resource metadata endpoint exists and returns correct data."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=oauth_app), base_url="http://localhost:8000"
    ) as client:
        # Test GET request
        response = await client.get("/.well-known/oauth-protected-resource")
        assert response.status_code == 200

        data = response.json()
        assert "resource" in data
        assert "authorization_servers" in data
        assert "bearer_methods_supported" in data

        # Check that authorization servers contains our issuer URL
        # The issuer URL might have a trailing slash
        assert len(data["authorization_servers"]) == 1
        assert data["authorization_servers"][0].rstrip("/") == "http://localhost:8000"
        assert data["bearer_methods_supported"] == ["header"]

        # Check CORS headers
        assert response.headers.get("Access-Control-Allow-Origin") == "*"


async def test_oauth_protected_resource_cors_preflight(oauth_app):
    """Test that the OAuth protected resource endpoint handles CORS preflight requests."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=oauth_app), base_url="http://localhost:8000"
    ) as client:
        # Test OPTIONS request
        response = await client.options("/.well-known/oauth-protected-resource")
        assert response.status_code == 200

        # Check CORS headers
        assert response.headers.get("Access-Control-Allow-Origin") == "*"
        assert "GET" in response.headers.get("Access-Control-Allow-Methods", "")
        assert "OPTIONS" in response.headers.get("Access-Control-Allow-Methods", "")
        assert "Authorization" in response.headers.get(
            "Access-Control-Allow-Headers", ""
        )


async def test_oauth_authorization_server_endpoint_still_exists(oauth_app):
    """Test that the existing OAuth authorization server endpoint still works."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=oauth_app), base_url="http://localhost:8000"
    ) as client:
        response = await client.get("/.well-known/oauth-authorization-server")
        assert response.status_code == 200

        data = response.json()
        assert "issuer" in data
        assert "authorization_endpoint" in data
        assert "token_endpoint" in data
        assert "registration_endpoint" in data


async def test_www_authenticate_header_includes_resource_metadata():
    """Test that 401 responses include the resource metadata URL in WWW-Authenticate header."""
    server = FastMCP(
        "TestServer",
        auth=InMemoryOAuthProvider(
            issuer_url="http://localhost:8000",
        ),
    )

    app = server.http_app()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://localhost:8000"
    ) as client:
        # Make a request without authentication
        response = await client.get("/mcp/")
        assert response.status_code == 401

        # Check WWW-Authenticate header
        www_auth = response.headers.get("www-authenticate")
        assert www_auth is not None
        assert "Bearer" in www_auth
        assert (
            'resource_metadata="http://localhost:8000/.well-known/oauth-protected-resource"'
            in www_auth
        )
        assert 'error="invalid_token"' in www_auth
