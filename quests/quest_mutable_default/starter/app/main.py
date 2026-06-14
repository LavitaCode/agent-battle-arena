from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class CartRequest(BaseModel):
    items: list[str]


# BUG: lista mutável como valor padrão acumula entre chamadas
def build_cart(items: list[str], cart: list[str] = []) -> list[str]:
    cart.extend(items)
    return cart


@app.post("/cart/add")
def add_to_cart(request: CartRequest) -> dict:
    return {"cart": build_cart(request.items)}
