from datetime import date
from typing import List

from .crud import get_expiring_items
from .schemas import Notification


def collect_notifications(days: int = 3) -> List[Notification]:
    result = []
    today = date.today()

    for item in get_expiring_items(days=days):
        days_until = (item.expiry_date - today).days
        if days_until < 0:
            message = f"{item.name} уже просрочен!"
        elif days_until == 0:
            message = f"{item.name} истекает сегодня"
        else:
            message = f"{item.name} истекает через {days_until} дн."

        result.append(
            Notification(
                message=message,
                item_id=item.id,
                days_until_expiry=days_until,
            )
        )

    return result


def draft_recipe_for_items(items):
    names = [item.name for item in items]
    if not names:
        return None

    return {
        "title": f"Быстрый ужин из {', '.join(names[:3])}",
        "ingredients": names,
        "steps": [
            f"Подготовьте продукты: {', '.join(names)}.",
            "Нарежьте ингредиенты и смешайте их в миске или на сковороде.",
            "Добавьте специи по вкусу и готовьте 15-20 минут до готовности.",
            "Подавайте сразу, пока блюдо свежее.",
        ],
        "expiry_reason": "Выбраны продукты с ближайшим сроком годности",
    }
