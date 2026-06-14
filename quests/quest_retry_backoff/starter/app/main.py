from typing import Callable

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Substituível nos testes para simular falhas sem I/O real
_upstream_caller: Callable[[], dict] | None = None


def _call_upstream() -> dict:
    if _upstream_caller is not None:
        return _upstream_caller()
    return {"data": "ok"}


@app.get("/fetch")
def fetch() -> JSONResponse:
    # BUG: sem retry — falha imediatamente na primeira exceção
    try:
        result = _call_upstream()
        return JSONResponse(content=result)
    except Exception:
        return JSONResponse(status_code=503, content={"error": "upstream failed"})
