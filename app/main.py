from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="kubernetes-lab-api", version="1.0.0")

_items: dict[int, str] = {}
_next_id: int = 1


class ItemCreate(BaseModel):
    name: str


class ItemResponse(BaseModel):
    id: int
    name: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "kubernetes-lab-api", "docs": "/docs", "health": "/health"}


@app.get("/hello")
def hello(name: str = "world") -> dict[str, str]:
    return {"message": f"Hello, {name}!"}


@app.get("/items", response_model=list[ItemResponse])
def list_items() -> list[ItemResponse]:
    return [ItemResponse(id=k, name=v) for k, v in _items.items()]


@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(payload: ItemCreate) -> JSONResponse | ItemResponse:
    global _next_id
    name = payload.name.strip()
    if not name:
        return JSONResponse(status_code=400, content={"error": "name is required"})
    item_id = _next_id
    _next_id += 1
    _items[item_id] = name
    return ItemResponse(id=item_id, name=name)


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int) -> JSONResponse | ItemResponse:
    if item_id not in _items:
        return JSONResponse(status_code=404, content={"error": "not found"})
    return ItemResponse(id=item_id, name=_items[item_id])


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="not found")
    del _items[item_id]
    return None
