from fastapi import APIRouter, status

from finlen_be.api.deps import AuthServiceDep, CurrentUserDep, DbSessionDep
from finlen_be.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest
from finlen_be.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with unique username and email. Returns safe user representation.",
)
async def register(
    req: UserRegisterRequest,
    db: DbSessionDep,
    service: AuthServiceDep,
) -> UserResponse:
    return await service.register(db, req)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate with email and password to receive a JWT access token.",
)
async def login(
    req: UserLoginRequest,
    db: DbSessionDep,
    service: AuthServiceDep,
) -> TokenResponse:
    return await service.login(db, req)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Retrieve the authenticated user's profile and progress stats.",
)
async def get_me(
    current_user: CurrentUserDep,
) -> UserResponse:
    return UserResponse.model_validate(current_user)
