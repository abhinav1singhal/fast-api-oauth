from fastapi import FastAPI, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from authenticator import OktaAuthenticator  # Import the authenticator class
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application setup
app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Instantiate OktaAuthenticator
authenticator = OktaAuthenticator()

class FormulaProcessor:
    def __init__(self, authenticator: OktaAuthenticator):
        self.authenticator = authenticator

    async def process(self, request: Request, formula: str):
        user = await self.authenticator.authenticate(token=await oauth2_scheme(request))
        # Add your formula processing logic here
        return {"result": "Formula processed"}

# Dependency Injection
formula_processor = FormulaProcessor(authenticator)

@app.post("/process_formula/")
@limiter.limit("50/minute")
async def process_formula_endpoint(request: Request, formula: str):
    return await formula_processor.process(request, formula)
