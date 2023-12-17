# FastAPI Application with Okta Authentication and Rate Limiting

This repository contains a FastAPI application that integrates Okta for OAuth2 authentication and applies rate limiting to its endpoints. The application is designed to be run in a Docker container and includes unit tests.

# Prerequisites
1. Docker
2. Python 3.8 or higher
3. An Okta account with the necessary configuration
4. Poetry for Python dependency management

# Setup
1. Clone the Repository
2. git clone [your-repository-url]
3. cd [your-repository-name]

# Install Poetry
Install Poetry, a tool for Python dependency management and packaging:
`pip install poetry`

# Configure Environment Variables
Create a `.env` file in the root directory and add the following variables:

1. OKTA_DOMAIN=your-okta-domain
2. CLIENT_ID=your-client-id
3. LIENT_SECRET=your-client-secret

Replace your-okta-domain, your-client-id, and your-client-secret with your actual Okta configuration details.

# Install Dependencies
1. Install the required Python libraries using Poetry:
`poetry install`
For running tests, ensure that your `pyproject.toml` file includes testing dependencies under [tool.poetry.dev-dependencies].

# Application Code
app.py
```from fastapi import FastAPI, Depends, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://{OKTA_DOMAIN}/oauth2/default/v1/introspect",
                params={"token": token, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
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
async def process_formula(formula: str, user: dict = Depends(get_current_user)):
    return {"result": "Formula processed"}
```
# Dockerfile
```
FROM python:3.8-slim

WORKDIR /usr/src/app

# Copy poetry.lock and pyproject.toml for Poetry
COPY poetry.lock pyproject.toml ./

# Install Poetry and project dependencies
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
```
# update pyproject.toml
### `pyproject.toml`

Here is a sample `pyproject.toml` for the FastAPI application:

```toml
[tool.poetry]
name = "fast-api-oauth"
version = "0.1.0"
description = "FastAPI application with Okta authentication and rate limiting"
authors = ["Your Name <youremail@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"
fastapi = "^0.65.1"
uvicorn = "^0.13.4"
httpx = "^0.18.2"
python-dotenv = "^0.17.1"
slowapi = "^0.1.5"
# Add any other dependencies your application requires

[tool.poetry.dev-dependencies]
pytest = "^6.2.4"
pytest-asyncio = "^0.15.1"
respx = "^0.16.3"
# Add any other development dependencies, such as linters or formatters

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
````


Remember to adjust the version numbers and dependencies according to your specific application needs. This configuration assumes the versions available at the time of writing. Check for the latest versions suitable for your project.

# Running the Application
## With Docker
Build and run the Docker container:
`docker build -t fast-api-oauth .`
`docker run -p 8000:80 fast-api-oauth`

# Locally
Run the application locally using Poetry:
`poetry run uvicorn app:app --reload`

# Testing
Run unit tests using pytest through Poetry:
`poetry run pytest`

# Contributing
Contributions are welcome. Please open an issue or pull request for any improvements or bug fixes.




