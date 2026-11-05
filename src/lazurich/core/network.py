import httpx

from lazurich.core.consts import CODENAME, VERSION

_client: httpx.AsyncClient | None = None


def client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            http2=True,
            follow_redirects=True,
            headers={'User-Agent': f'wojtmic/lazurich/{VERSION}-{CODENAME} (https://lazurich.app)'},
            timeout=httpx.Timeout(30, connect=10),
        )
    return _client


async def close():
    global _client
    if _client:
        await _client.aclose()
        _client = None
