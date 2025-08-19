"""Tests for OpenAPI parameter style and explode handling in experimental parser."""

import httpx

from fastmcp.experimental.server.openapi import FastMCPOpenAPI
from fastmcp.experimental.utilities.openapi import convert_openapi_schema_to_json_schema


def _make_server_and_capture_urls(openapi_dict: dict, args: dict) -> list[str]:
    """Helper to create a server and capture URLs generated during tool calls."""
    calls: list[str] = []

    async def handler(request: httpx.Request):
        calls.append(str(request.url))
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(base_url="https://api.test", transport=transport)
    spec = convert_openapi_schema_to_json_schema(openapi_dict)
    server = FastMCPOpenAPI(openapi_spec=spec, client=client, name="TestServer")

    # Use the MCP call path to exercise the generated tool
    import anyio

    anyio.run(server._mcp_call_tool, "echo", args)  # type: ignore[arg-type]
    return calls


def test_query_array_form_explode_false_works_correctly():
    """Test that form style with explode=false generates comma-delimited values."""
    # Minimal OpenAPI spec: array query param with style=form, explode=false
    openapi = {
        "openapi": "3.1.0",
        "info": {"title": "T", "version": "1.0.0"},
        "paths": {
            "/echo": {
                "get": {
                    "operationId": "echo",
                    "parameters": [
                        {
                            "name": "ids",
                            "in": "query",
                            "style": "form",
                            "explode": False,
                            "schema": {"type": "array", "items": {"type": "string"}},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    urls = _make_server_and_capture_urls(openapi, {"ids": ["1", "2", "3"]})

    # Expected per OpenAPI (form+explode=false): `ids=1,2,3`
    # Actual (bug): multiple entries: `ids=1&ids=2&ids=3`
    assert any(url.endswith("/echo?ids=1%2C2%2C3") for url in urls), (
        f"Expected comma-delimited value, got: {urls}"
    )


def test_query_array_pipe_explode_false_works_correctly():
    """Test that pipeDelimited style with explode=false generates pipe-delimited values."""
    # pipeDelimited example: expect ids=1|2|3 when explode=false
    openapi = {
        "openapi": "3.1.0",
        "info": {"title": "T", "version": "1.0.0"},
        "paths": {
            "/echo": {
                "get": {
                    "operationId": "echo",
                    "parameters": [
                        {
                            "name": "ids",
                            "in": "query",
                            "style": "pipeDelimited",
                            "explode": False,
                            "schema": {"type": "array", "items": {"type": "string"}},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    urls = _make_server_and_capture_urls(openapi, {"ids": ["1", "2", "3"]})
    assert any(url.endswith("/echo?ids=1%7C2%7C3") for url in urls), (
        f"Expected pipe-delimited value, got: {urls}"
    )


def test_query_array_form_explode_true_works():
    """Test that form style with explode=true works as expected (generates repeated params)."""
    openapi = {
        "openapi": "3.1.0",
        "info": {"title": "T", "version": "1.0.0"},
        "paths": {
            "/echo": {
                "get": {
                    "operationId": "echo",
                    "parameters": [
                        {
                            "name": "ids",
                            "in": "query",
                            "style": "form",
                            "explode": True,
                            "schema": {"type": "array", "items": {"type": "string"}},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    urls = _make_server_and_capture_urls(openapi, {"ids": ["1", "2", "3"]})

    # With explode=true, we expect repeated parameters: ids=1&ids=2&ids=3
    # The order may vary, so we check for all possible combinations
    expected_patterns = [
        "ids=1&ids=2&ids=3",
        "ids=1&ids=3&ids=2",
        "ids=2&ids=1&ids=3",
        "ids=2&ids=3&ids=1",
        "ids=3&ids=1&ids=2",
        "ids=3&ids=2&ids=1",
    ]

    assert any(any(pattern in url for pattern in expected_patterns) for url in urls), (
        f"Expected repeated params for explode=true, got: {urls}"
    )


def test_query_array_space_explode_false_works_correctly():
    """Test that spaceDelimited style with explode=false generates space-delimited values."""
    openapi = {
        "openapi": "3.1.0",
        "info": {"title": "T", "version": "1.0.0"},
        "paths": {
            "/echo": {
                "get": {
                    "operationId": "echo",
                    "parameters": [
                        {
                            "name": "ids",
                            "in": "query",
                            "style": "spaceDelimited",
                            "explode": False,
                            "schema": {"type": "array", "items": {"type": "string"}},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    urls = _make_server_and_capture_urls(openapi, {"ids": ["1", "2", "3"]})
    # Space delimited should be URL encoded as + (or %20)
    assert any(
        url.endswith("/echo?ids=1+2+3") or url.endswith("/echo?ids=1%202%203")
        for url in urls
    ), f"Expected space-delimited value, got: {urls}"
