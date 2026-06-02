from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class RegisterRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120,
        description="User full name",
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
        description="User password",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """
        bcrypt supports a maximum password length of 72 bytes.
        Validate before hashing to avoid runtime failures.
        """
        if len(value.encode("utf-8")) > 72:
            raise ValueError(
                "Password exceeds bcrypt maximum length of 72 bytes"
            )

        return value


class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    role: str
    created_at: datetime


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse