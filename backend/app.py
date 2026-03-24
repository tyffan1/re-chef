import os
from datetime import date, datetime
from pathlib import Path
from typing import List

from fastapi import BackgroundTasks, Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .crud import create_item, get_expiring_items, list_items, mark_item_used
from .db import init_db
from .notifications import collect_notifications, draft_recipe_for_items
from .schemas import ChatRequest, ChatResponse, FoodItemCreate, FoodItemRead, Notification, Recipe

app = FastAPI(
    title="Re-Chef",
    version="0.1.0",
    description="MVP для управления продуктами в холодильнике без лишних потерь.",
)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
def serve_index():
    return FileResponse(frontend_dir / "index.html")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/items", response_model=FoodItemRead)
def add_item(item: FoodItemCreate):
    return create_item(item)


@app.get("/items", response_model=List[FoodItemRead])
def read_items(include_used: bool = False):
    return list_items(include_used=include_used)


@app.get("/items/expiring", response_model=List[FoodItemRead])
def read_expiring(days: int = 3):
    return get_expiring_items(days=days)


@app.post("/items/{item_id}/use", response_model=FoodItemRead)
def use_item(item_id: int):
    item = mark_item_used(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/scan/receipt")
def scan_receipt(receipt_text: str = Body(..., media_type="text/plain")):
    # Каждая строка: "название, количество, дата_срока".
    lines = [line.strip() for line in receipt_text.splitlines() if line.strip()]
    added = date.today()
    parsed = []

    for line in lines:
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 2:
            continue

        name = parts[0]
        qty = float(parts[1]) if parts[1].replace(".", "", 1).isdigit() else 1
        expiry = added

        if len(parts) >= 3:
            try:
                expiry = datetime.strptime(parts[2], "%Y-%m-%d").date()
            except ValueError:
                expiry = added

        item_in = FoodItemCreate(
            name=name,
            quantity=qty,
            unit="pcs",
            added_date=added,
            expiry_date=expiry,
            source="receipt",
        )
        create_item(item_in)
        parsed.append(name)

    return {"created": parsed, "count": len(parsed)}


@app.post("/scan/shelf")
def scan_shelf(items: List[FoodItemCreate]):
    created = []
    for item_in in items:
        created.append(create_item(item_in))
    return created


@app.get("/notifications", response_model=List[Notification])
def notifications(days: int = 3):
    return collect_notifications(days=days)


@app.get("/recipes/expiring", response_model=Recipe)
def recipe_for_expiring(days: int = 3):
    exp_items = get_expiring_items(days=days)
    recipe = draft_recipe_for_items(exp_items)
    if not recipe:
        raise HTTPException(status_code=404, detail="No expiring items for recipe")
    return Recipe(**recipe)


@app.post("/dummy-push")
def dummy_push(background_tasks: BackgroundTasks):
    # Заглушка для будущей асинхронной отправки push-уведомлений.
    background_tasks.add_task(lambda: print("push: проверка отправки"))
    return {"status": "scheduled"}


@app.post("/chat", response_model=ChatResponse)
def chat_with_gpt(payload: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured",
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="The openai package is not installed. Run: pip install openai",
        ) from exc

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-5.2-chat-latest")

    request_args = {
        "model": model,
        "instructions": (
            "Ты помощник приложения Re-Chef. Отвечай кратко и по делу на русском языке. "
            "Помогай с продуктами, рецептами, хранением еды и бытовыми вопросами по кухне."
        ),
        "input": payload.message,
    }
    if payload.previous_response_id:
        request_args["previous_response_id"] = payload.previous_response_id

    try:
        response = client.responses.create(**request_args)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc}") from exc

    reply = getattr(response, "output_text", "").strip()
    if not reply:
        raise HTTPException(status_code=502, detail="OpenAI returned an empty response")

    return ChatResponse(reply=reply, response_id=response.id)
