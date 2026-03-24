from datetime import date, timedelta
from typing import List
from sqlmodel import select
from .models import FoodItem
from .db import get_session


def create_item(item_data) -> FoodItem:
    with get_session() as session:
        item = FoodItem(**item_data.dict())
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


def list_items(include_used: bool = False) -> List[FoodItem]:
    with get_session() as session:
        statement = select(FoodItem)
        if not include_used:
            statement = statement.where(FoodItem.used == False)
        return session.exec(statement).all()


def get_expiring_items(days: int = 3) -> List[FoodItem]:
    with get_session() as session:
        today = date.today()
        end_date = today + timedelta(days=days)
        statement = (
            select(FoodItem)
            .where(FoodItem.used == False)
            .where(FoodItem.expiry_date >= today)
            .where(FoodItem.expiry_date <= end_date)
            .order_by(FoodItem.expiry_date)
        )
        return session.exec(statement).all()


def mark_item_used(item_id: int) -> FoodItem:
    with get_session() as session:
        item = session.get(FoodItem, item_id)
        if not item:
            return None
        item.used = True
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
