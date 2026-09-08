import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from finlen_be.api.deps import AuthServiceDep, CurrentUserDep, DbSessionDep
from finlen_be.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest
from finlen_be.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with unique username and email. Returns safe user representation.",
    responses={
        409: {"description": "Email or username already taken"},
        500: {"description": "Internal server error"},
    },
)
async def register(
    req: UserRegisterRequest,
    db: DbSessionDep,
    service: AuthServiceDep,
) -> UserResponse:
    try:
        return await service.register(db, req)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error during registration: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to a database error. Please try again.",
        )
    except Exception as e:
        logger.error("Unexpected error during registration: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration.",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate with email and password to receive a JWT access token.",
    responses={
        401: {"description": "Invalid email or password"},
        500: {"description": "Internal server error"},
    },
)
async def login(
    req: UserLoginRequest,
    db: DbSessionDep,
    service: AuthServiceDep,
) -> TokenResponse:
    try:
        return await service.login(db, req)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error during login: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to a database error. Please try again.",
        )
    except Exception as e:
        logger.error("Unexpected error during login: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login.",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Retrieve the authenticated user's profile and progress stats.",
    responses={
        401: {"description": "Authentication required or invalid token"},
        500: {"description": "Internal server error"},
    },
)
async def get_me(
    current_user: CurrentUserDep,
) -> UserResponse:
    try:
        return UserResponse.model_validate(current_user)
    except ValidationError as e:
        logger.error("Validation error serializing user profile: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to serialize user profile.",
        )
    except Exception as e:
        logger.error("Unexpected error fetching user profile: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching the user profile.",
        )
