import uuid
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from finlen_be.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from finlen_be.models.user import User
from finlen_be.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest
from finlen_be.schemas.user import UserResponse


class AuthService:
    async def register(
        self,
        db: AsyncSession,
        req: UserRegisterRequest,
    ) -> UserResponse:
        """Register a new user, ensuring unique email and username."""
        # Check if email or username already exists
        stmt = select(User).where(
            or_(User.email == req.email, User.username == req.username)
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            if existing.email == req.email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        # Hash password and create record
        hashed = hash_password(req.password)
        new_user = User(
            id=uuid.uuid4(),
            username=req.username,
            email=req.email,
            password_hash=hashed,
            level=1,
            xp=0,
            financial_instinct=0.0,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return UserResponse.model_validate(new_user)

    async def login(
        self,
        db: AsyncSession,
        req: UserLoginRequest,
    ) -> TokenResponse:
        """Authenticate user credentials and issue a JWT access token."""
        stmt = select(User).where(User.email == req.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        return TokenResponse(access_token=access_token, token_type="bearer")

    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> User | None:
        """Retrieve user by UUID."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


auth_service = AuthService()
