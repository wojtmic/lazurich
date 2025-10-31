import msal
import msal.exceptions
import os
import httpx

BASE_DIR = os.path.expanduser('~/.local/share/lazurich')

CLIENT_ID = 'd1801a6c-317e-45b7-adef-08fe47e474f6'
AUTHORITY = 'https://login.microsoftonline.com/consumers'
SCOPES = ['XboxLive.signin']

XBL_URL = 'https://user.auth.xboxlive.com/user/authenticate'
XSTS_URL= 'https://xsts.auth.xboxlive.com/xsts/authorize'
MC_URL  = 'https://api.minecraftservices.com/authentication/login_with_xbox'
PROF_URL= 'https://api.minecraftservices.com/minecraft/profile'

cache = msal.SerializableTokenCache()
cache_path = os.path.join(BASE_DIR, 'msal_token_cache.bin')
if os.path.exists(cache_path):
    with open(cache_path, "r") as f:
        cache.deserialize(f.read())

app = msal.PublicClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    token_cache=cache
)

def login():
    result = None
    accounts = app.get_accounts()

    if accounts:
        try:
            result = app.acquire_token_silent_with_error(SCOPES, account=accounts[0])
        except:
            result = None

    if not result:
        print('Interactive login starting')
        try:
            result = app.acquire_token_interactive(scopes=SCOPES)
        except msal.exceptions.MsalError:
            print('Failed interactive login (canceled?)')

    if 'access_token' in result:
        token = result['access_token']

        account = app.get_accounts()[0]

        if cache.has_state_changed:
            with open(cache_path, "w") as f:
                f.write(cache.serialize())

        return token, account

    else:
        return None, None

def get_credentials(token: str):
    with httpx.Client() as session:
        print('Authenticating with Xbox Live')
        xbl_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        xbl_payload = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={token}"
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT"
        }

        response = session.post(XBL_URL, headers=xbl_headers, json=xbl_payload)
        response.raise_for_status()

        xbl_data = response.json()
        xbl_token = xbl_data['Token']

        print('Authenticating with XSTS')
        xsts_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        xsts_payload = {
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [
                    xbl_token
                ]
            },
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT"
        }

        response = session.post(XSTS_URL, headers=xsts_headers, json=xsts_payload)
        response.raise_for_status()

        xsts_data = response.json()

        if "XErr" in xsts_data:
            xerr = xsts_data["XErr"]
            message = xsts_data.get("Message", "")
            if xerr == 2148916233:
                print(f"   [ERROR] XSTS Error: The user does not have an Xbox account. ({message})")
            elif xerr == 2148916238:
                print(f"   [ERROR] XSTS Error: The user is a child and cannot be logged in. ({message})")
            else:
                print(f"   [ERROR] XSTS Error {xerr}: {message}")
            return None

        xsts_token = xsts_data["Token"]
        user_hash = xsts_data["DisplayClaims"]["xui"][0]["uhs"]

        print('Authenticating with Minecraft Services')
        mc_headers = {
            "Content-Type": "application/json",
            "Accept": 'application/json'
        }
        identity_token = f"XBL3.0 x={user_hash};{xsts_token}"
        mc_payload = {
            "identityToken": identity_token
        }

        print(f"User hash: {user_hash}")
        print(f"Identity token length: {len(identity_token)}")
        print(f"XSTS token (first 50 chars): {xsts_token[:50]}")

        response = session.post(MC_URL, json=mc_payload, headers=mc_headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        response.raise_for_status()

        mc_data = response.json()
        mc_access_token = mc_data["access_token"]

        print('Fetching Minecraft Profile')
        profile_headers = {
            "Authorization": f"Bearer {mc_access_token}"
        }

        response = session.get(PROF_URL, headers=profile_headers)
        response.raise_for_status()
        profile_data = response.json()

        return {
            "username": profile_data["name"],
            "uuid": profile_data["id"],
            "token": mc_access_token
        }
