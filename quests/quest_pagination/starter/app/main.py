from fastapi import FastAPI

app = FastAPI()

# Dataset fixo representando o catálogo
_PRODUCTS = [{"id": i, "name": f"product-{i}", "price": i * 1.5} for i in range(1, 51)]


# BUG: sem paginação — retorna tudo sem page/page_size e sem metadata
@app.get("/products")
def list_products() -> dict:
    return {"items": _PRODUCTS}
