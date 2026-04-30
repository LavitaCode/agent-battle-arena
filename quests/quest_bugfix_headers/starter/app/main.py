from fastapi import FastAPI
from fastapi.responses import JSONResponse


app = FastAPI()


@app.get("/status")
def status() -> JSONResponse:
    return JSONResponse(status_code=200, content={"ok": "true"})
