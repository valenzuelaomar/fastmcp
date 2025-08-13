from typing import Any

from fastmcp.client.transports import ClientTransport
from fastmcp.mcp_config import (
    MCPConfig,
    MCPServerTypes,
)
from fastmcp.server.server import FastMCP

# def composite_server_from_mcp_config(
#     config: MCPConfig, name_as_prefix: bool = True
# ) -> tuple[FastMCP[None], list[ClientTransport]]:
#     """A utility function to create a composite server from an MCPConfig, returns the underlying
#     transports for each server.
#     """
#     composite_server = FastMCP[None]()

#     transports = mount_mcp_config_into_server(config, composite_server, name_as_prefix)

#     return composite_server, transports


# def mount_mcp_config_into_server(
#     config: MCPConfig,
#     server: FastMCP[Any],
#     name_as_prefix: bool = True,
# ) -> None:
#     """A utility function to mount the servers from an MCPConfig into a FastMCP server, returns the underlying
#     transports for each server.
#     """
#     for name, server_to_mount, transport in mcp_config_to_servers_and_transports(config):
#         server.mount(server=server_to_mount, prefix=name if name_as_prefix else None)

def mcp_config_to_servers_and_transports(
    config: MCPConfig,
) -> list[tuple[str, FastMCP[Any], ClientTransport]]:
    """A utility function to convert each entry of an MCP Config into a transport and server."""
    return [
        mcp_server_type_to_servers_and_transports(name, mcp_server)
        for name, mcp_server in config.mcpServers.items()
    ]

def mcp_server_type_to_servers_and_transports(
    name: str,
    mcp_server: MCPServerTypes,
) -> tuple[str, FastMCP[Any], ClientTransport]:
    """A utility function to convert each entry of an MCP Config into a transport and server."""
    from fastmcp.mcp_config import (
        TransformingRemoteMCPServer,
        TransformingStdioMCPServer,
)
    server: FastMCP[Any]
    transport: ClientTransport

    if isinstance(
        mcp_server, TransformingRemoteMCPServer | TransformingStdioMCPServer
    ):
        server, transport = mcp_server._to_server_and_transport()
    else:
        transport = mcp_server.to_transport()
        server = FastMCP.as_proxy(backend=transport)

    return name, server, transport
