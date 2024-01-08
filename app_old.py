from fastapi import FastAPI, Depends, HTTPException, status, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security import OAuth2PasswordBearer
import httpx
import os
from dotenv import load_dotenv


load_dotenv()

OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

app_old = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app_old.state.limiter = limiter
app_old.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    async with httpx.AsyncClient() as client:
        try:
            print("token -->"+ token + "\n" + CLIENT_ID + "\n" + CLIENT_SECRET + "\n")
            response = await client.post(
                f"{OKTA_DOMAIN}/v1/introspect",
                data={
                "token": token, 
                "client_id": CLIENT_ID, 
                "client_secret": CLIENT_SECRET,
                "token_type_hint": "access_token"  # optional, but can be helpful
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

@app.post("/process_formula/")
@limiter.limit("50/minute")
async def process_formula(request: Request, formula: str, user: dict = Depends(get_current_user)):
    return {"result": "Formula processed"}