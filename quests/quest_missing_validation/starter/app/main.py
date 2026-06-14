from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


# BUG: todos os campos são Optional — payload vazio é aceito silenciosamente
@app.post("/orders", status_code=201)
def create_order(payload: dict = {}) -> dict:
    return {
        "order_id": "ord-001",
        "product": payload.get("product"),
        "price": payload.get("price"),
        "status": "created",
    }
