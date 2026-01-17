from httpx import AsyncClient

client: AsyncClient | None = None

def get_client():
    global client
    if client is None or client.is_closed:
        client = AsyncClient(
            timeout=None,
            headers={"User-Agent": "wojtmic/lazurich/0.0.1-alpha (lazurich.wojtmic.dev)"}
        )

    return client

async def close_client():
    global client
    if client:
        await client.aclose()
        client = None
