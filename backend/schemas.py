from datetime import date
from pydantic import BaseModel, condecimal
from typing import Optional, List


class FoodItemCreate(BaseModel):
    name: str
    quantity: Optional[condecimal(gt=0)] = 1
    unit: Optional[str] = "pcs"
    added_date: date
    expiry_date: date
    source: Optional[str] = "manual"


class FoodItemRead(FoodItemCreate):
    id: int
    used: bool


class Recipe(BaseModel):
    title: str
    ingredients: List[str]
    steps: List[str]
    expiry_reason: str


class Notification(BaseModel):
    message: str
    item_id: int
    days_until_expiry: int


class ChatRequest(BaseModel):
    message: str
    previous_response_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    response_id: str
