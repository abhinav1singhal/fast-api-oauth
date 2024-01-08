from fastapi import HTTPException, status
import httpx
import os

class OktaAuthenticator:
    def __init__(self):
        self.okta_domain = os.getenv("OKTA_DOMAIN")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")

    async def authenticate(self, token: str):
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        async with httpx.AsyncClient() as client:
            try:
                print("token -->"+ token + "\n" + self.client_id + "\n" + self.client_secret + "\n")
                print(f"{self.okta_domain}/v1/introspect")
                response = await client.post(
                    f"{self.okta_domain}/v1/introspect",
                    data={
                        "token": token, 
                        "client_id": self.client_id, 
                        "client_secret": self.client_secret,
                        "token_type_hint": "access_token"
                    }
                )
                response.raise_for_status()
                token_data = response.json()
                if not token_data["active"]:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token",
                    )
            except httpx.HTTPError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
        return token_data
