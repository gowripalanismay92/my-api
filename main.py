import os
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import jwt
from jwt import PyJWKClient

# Configured from Entra ID App Registration (my-api)
TENANT_ID = os.getenv("TENANT_ID", "YOUR_TENANT_ID")
API_CLIENT_ID = os.getenv("API_CLIENT_ID", "YOUR_API_CLIENT_ID")

JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"

jwk_client = PyJWKClient(JWKS_URL)
security = HTTPBearer()

app = FastAPI(title="My Protected API (my-api)")

# Allow requests from the separate SPA app at http://localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=API_CLIENT_ID,
            issuer=ISSUER,
        )
        
        # Validate that token contains access_as_user scope
        scopes = payload.get("scp", "").split(" ")
        if "access_as_user" not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token missing required 'access_as_user' scope."
            )
        return payload
    except jwt.PyJWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authorization token: {str(err)}"
        )

# Mock DB rows isolated by user Object ID (oid)
MOCK_ORDERS = [
    {"id": 101, "item": "Cloud Compute Node", "owner_oid": "USER_OID_1"},
    {"id": 102, "item": "Database Instance", "owner_oid": "USER_OID_2"},
]

@app.get("/api/me")
def get_me(user: dict = Depends(verify_jwt_token)):
    return {
        "name": user.get("name", "Unknown User"),
        "username": user.get("preferred_username", user.get("upn", "Unknown")),
        "oid": user.get("oid"),
        "scopes": user.get("scp")
    }

@app.get("/api/orders")
def get_orders(user: dict = Depends(verify_jwt_token)):
    user_oid = user.get("oid")
    user_orders = [o for o in MOCK_ORDERS if o["owner_oid"] == user_oid]
    if not user_orders:
        user_orders = [{"id": 1001, "item": "Personalized User Record", "owner_oid": user_oid}]
    return {"user_oid": user_oid, "orders": user_orders}
