from fastmcp import FastMCP
from fastmcp.testing import TestClient

server = FastMCP("test-server")


@server.tool()
def get_the_value_of_schleeb() -> int:
    return 42


async def main():
    async with TestClient(server) as client:
        await client.say("What is the value of schleeb?")
        await client.say("sorry can you repeat that?")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
