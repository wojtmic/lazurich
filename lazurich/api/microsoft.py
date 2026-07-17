import keyring
import msal
import requests
import time

from lazurich import get_client
client = get_client()

session = requests.Session()
session.headers.update({"User-Agent": "wojtmic/lazurich/0.0.1-alpha (lazurich.wojtmic.dev)"})

app = msal.PublicClientApplication(
    client_id="d1801a6c-317e-45b7-adef-08fe47e474f6",
    authority="https://login.microsoftonline.com/consumers",
    http_client=session,
)

def get_msa_token() -> str:
    cached_token = keyring.get_password("lazurich", "msa_access_token")
    cached_expiry = keyring.get_password("lazurich", "msa_expires_at")

    if cached_token and cached_expiry and time.time() < float(cached_expiry):
        return cached_token

    refresh_token = keyring.get_password("lazurich", "msa_refresh_token")

    if refresh_token:
        result = app.acquire_token_by_refresh_token(refresh_token, scopes=["XboxLive.signin"])
        if result and "access_token" in result:
            keyring.set_password("lazurich", "msa_access_token", result["access_token"])
            keyring.set_password("lazurich", "msa_expires_at", str(time.time() + result["expires_in"]))
            if "refresh_token" in result:
                keyring.set_password("lazurich", "msa_refresh_token", result["refresh_token"])
            return result["access_token"]

    flow = app.initiate_device_flow(scopes=["XboxLive.signin"])
    if "user_code" not in flow:
        raise RuntimeError(f"failed to create device flow: {flow.get('error_description')}")

    print(flow["message"])
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise RuntimeError(f"auth failed: {result.get('error_description')}")

    keyring.set_password("lazurich", "msa_access_token", result["access_token"])
    keyring.set_password("lazurich", "msa_expires_at", str(time.time() + result["expires_in"]))
    keyring.set_password("lazurich", "msa_refresh_token", result["refresh_token"])

    return result["access_token"]

async def get_xbox_live_token(msa_token: str) -> tuple[str, str]:
    resp = await client.post(
        "https://user.auth.xboxlive.com/user/authenticate",
        json={
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={msa_token}",
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    return data["Token"], data["DisplayClaims"]["xui"][0]["uhs"]

async def get_xsts_token(xbl_token: str) -> str:
    resp = await client.post(
        "https://xsts.auth.xboxlive.com/xsts/authorize",
        json={
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [xbl_token],
            },
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT",
        },
    )
    if resp.status_code == 401:
        raise RuntimeError(f"XSTS auth failed, XErr={resp.json().get('XErr')}")
    resp.raise_for_status()
    return resp.json()["Token"]

async def get_minecraft_token(uhs: str, xsts_token: str) -> str:
    resp = await client.post(
        "https://api.minecraftservices.com/authentication/login_with_xbox",
        json={"identityToken": f"XBL3.0 x={uhs};{xsts_token}"},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

async def get_minecraft_profile(mc_token: str) -> dict:
    resp = await client.get(
        "https://api.minecraftservices.com/minecraft/profile",
        headers={"Authorization": f"Bearer {mc_token}"},
    )
    resp.raise_for_status()
    return resp.json()

async def do_full_auth(msa_token: str) -> tuple[dict, str]:
    xbl_token, uhs = await get_xbox_live_token(msa_token)
    xsts_token = await get_xsts_token(xbl_token)
    mc_token = await get_minecraft_token(uhs, xsts_token)
    profile = await get_minecraft_profile(mc_token)
    return profile, mc_token

if __name__ == "__main__":
    tok = get_msa_token()
    import asyncio
    print(asyncio.run(do_full_auth(tok))[0])
