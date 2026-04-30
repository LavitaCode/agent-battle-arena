"""Pydantic models for public alpha users and invites."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    id: str = Field(..., description="User identifier")
    github_login: str = Field(..., description="GitHub login or handle")
    display_name: str = Field(..., description="Display name")
    role: str = Field("alpha_user", description="Role for the current user")
    alpha_status: str = Field("approved", description="Closed alpha access status")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class AccessInvite(BaseModel):
    code: str = Field(..., description="Invite code")
    email_or_login: str = Field(..., description="Target GitHub login or email")
    status: str = Field(..., description="Invite status")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    used_by_user_id: Optional[str] = Field(None, description="User that redeemed the invite")

    model_config = ConfigDict(from_attributes=True)
