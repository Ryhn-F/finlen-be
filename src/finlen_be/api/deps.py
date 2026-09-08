from typing import Annotated
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from finlen_be.core.database import get_db
from finlen_be.core.security import decode_access_token
from finlen_be.models.user import User
from finlen_be.services.auth_service import AuthService, auth_service
from finlen_be.services.roleplay_service import RoleplayService, roleplay_service
from finlen_be.services.scenario_service import ScenarioService, scenario_service

# Reusable database dependency annotation
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]

# HTTP Bearer security scheme for Swagger documentation
security = HTTPBearer(auto_error=False)


async def get_current_user(
    db: DbSessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User:
    """Validate JWT bearer token and extract authenticated user from PostgreSQL."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
AuthServiceDep = Annotated[AuthService, Depends(lambda: auth_service)]
ScenarioServiceDep = Annotated[ScenarioService, Depends(lambda: scenario_service)]
RoleplayServiceDep = Annotated[RoleplayService, Depends(lambda: roleplay_service)]
