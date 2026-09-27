from httpx import AsyncClient, Timeout
from importlib.metadata import version

VER_CODENAME = 'indev'
VER = version('lazurich')

client: AsyncClient | None = None

def get_client() -> AsyncClient:
    global client
    current = client
    if current is None or current.is_closed:
        current = client = AsyncClient(
            timeout=Timeout(30, connect=5),
            follow_redirects=True,
            headers={"User-Agent": f"wojtmic/lazurich/{VER}-{VER_CODENAME}"},
        )

    return current

async def close_client():
    global client
    if client:
        await client.aclose()
        client = None