from fastapi import FastAPI, status
from pydantic import BaseModel


class ProfileSettingsPayload(BaseModel):
    theme: str
    notifications: bool


app = FastAPI()


@app.post("/profile/settings", status_code=status.HTTP_201_CREATED)
def save_profile_settings(payload: ProfileSettingsPayload) -> dict[str, str]:
    return {"status": "saved"}
