from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from typing import Optional
import ssl
import certifi

# Fix for macOS Python lacking root certificates for urllib
# This is a workaround to ensure that the SSL context uses the certifi bundle for HTTPS requests, which is necessary for fetching JWKS from Clerk's endpoints.
try:
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
except Exception:
    pass

from app.config import settings

security = HTTPBearer()

def get_jwks_url() -> str:
    # If CLERK_ISSUER_URL is provided, use it
    if settings.CLERK_ISSUER_URL:
        return f"{settings.CLERK_ISSUER_URL.rstrip('/')}/.well-known/jwks.json"
    # Otherwise, fallback to a dummy URL for testing if not set
    return "https://example.com/.well-known/jwks.json"

_jwks_client: Optional[PyJWKClient] = None

def get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(get_jwks_url())
    return _jwks_client


def verify_token(token: str) -> dict:
    if not settings.CLERK_ISSUER_URL:
        # In test environments without real Clerk, we might want to mock this
        # or just fail. For now, let's just attempt validation and it will fail.
        pass

    try:
        client = get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        
        # Clerk JWTs are signed with RS256
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            # Clerk issues tokens with azp (Authorized Party) and iss (Issuer)
            # You can verify audience if configured, but often it's sufficient to verify signature and exp
            options={"verify_aud": False},
        )
        return data
    except jwt.PyJWKClientError as e:
        print("JWK Client Error:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unable to fetch JWKS: {e}",
        ) from e
    except jwt.InvalidTokenError as e:
        print("Invalid Token Error:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {e}",
        ) from e

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    payload = verify_token(token)
    
    # The 'sub' claim in Clerk JWT is the user ID
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing 'sub' claim",
        )
    return user_id
