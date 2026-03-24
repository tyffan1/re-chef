# Re-Chef

Проект: ШІ-сканер холодильника для боротьби з марнотратством їжі.

## 🚀 Старт

1. Створити віртуальне оточення (на Windows PowerShell):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Запустити сервер:

   ```powershell
   uvicorn backend.app:app --reload --port 8000
   ```

3. Перейти у браузері: `http://localhost:8000/docs`


## 🧩 API MVP

- `POST /items` — додати продукт
- `GET /items` — перелік продуктів
- `GET /items/expiring?days=3` — товари, що скоро зіпсуються
- `POST /items/{item_id}/use` — позначити як використаний
- `POST /scan/receipt` — простий парсер чеку (текст)
- `POST /scan/shelf` — ручний скан полиці (список продуктів)
- `GET /notifications` — генерація push-повідомлень
- `GET /recipes/expiring` — рецепт з критичних інгредієнтів


## 🧪 Тестові приклади

### 1. Додати товар

`POST /items`

```json
{
  "name": "Молоко",
  "quantity": 1,
  "unit": "л",
  "added_date": "2026-03-24",
  "expiry_date": "2026-03-26"
}
```

### 2. Парсинг чеку

`POST /scan/receipt` з тілом (plain text):

```
Молоко,1,2026-03-26
Йогурт,3,2026-03-25
Помідор,5,2026-03-28
```


## �️ Фронтенд

Один з варіантів презентації: `frontend/index.html` + `frontend/app.js` + `frontend/style.css`.

Запуск:

1. запустити backend: `uvicorn backend.app:app --reload --port 8000`
2. відкрити http://localhost:8000/

## �🔧 Далі

1. Підключити реальну OCR/Computer Vision (Cloud Vision/YOLOv8)
2. Персоналізація UX: налаштування дієти, шаблони рецепту
3. Push-повідомлення через FCM/APNS і планувальник cron
4. Монетизація: преміум тарифи (+персональні плани)
