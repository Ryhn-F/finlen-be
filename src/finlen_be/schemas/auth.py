from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(description="User valid email address")
    password: str = Field(min_length=8, max_length=128, description="Password (at least 8 characters)")


class UserLoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(description="User registered email")
    password: str = Field(description="User password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
