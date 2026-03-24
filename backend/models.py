from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field


class FoodItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    quantity: float = Field(default=1.0, ge=0)
    unit: str = Field(default="pcs")
    added_date: date
    expiry_date: date
    source: str = Field(default="manual")
    used: bool = Field(default=False)
