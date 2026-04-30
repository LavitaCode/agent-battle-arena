"""Pydantic models for closed alpha authentication."""
from typing import Optional

from pydantic import BaseModel, Field

from .user import User


class AuthStartRequest(BaseModel):
    github_login: Optional[str] = Field(
        None,
        description="GitHub login used only by local mock auth; real OAuth resolves it from GitHub",
    )
    invite_code: str = Field(..., description="Invite code for closed alpha access")


class AuthStartResponse(BaseModel):
    state: str = Field(..., description="Temporary state token")
    authorization_url: str = Field(..., description="Callback URL used to complete auth")


class InviteValidationResponse(BaseModel):
    valid: bool = Field(..., description="Whether the invite is valid")
    status: str = Field(..., description="Invite validation status")


class SessionUserResponse(BaseModel):
    authenticated: bool = Field(..., description="Whether a user is currently authenticated")
    user: Optional[User] = Field(None, description="Authenticated user payload")
