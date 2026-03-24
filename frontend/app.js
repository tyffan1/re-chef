const apiBase = window.location.protocol.startsWith("http")
  ? `${window.location.protocol}//${window.location.host}`
  : "http://127.0.0.1:8000";

const $ = (selector) => document.querySelector(selector);
let previousResponseId = null;

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString("ru-RU");
}

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(apiBase + path, { ...options, headers });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || `Ошибка ${res.status}`);
  }

  return res.json();
}

async function refreshItems(includeUsed = false, expiring = false) {
  const list = $("#items-list");
  const path = expiring ? "/items/expiring?days=7" : `/items?include_used=${includeUsed}`;

  try {
    const items = await request(path);
    list.innerHTML = "";

    if (!items.length) {
      const empty = document.createElement("li");
      empty.textContent = expiring ? "Нет продуктов с близким сроком годности." : "Список продуктов пуст.";
      list.appendChild(empty);
      return;
    }

    items.forEach((item) => {
      const el = document.createElement("li");
      el.textContent = `${item.name} (${item.quantity} ${item.unit}) - срок: ${formatDate(item.expiry_date)}${item.used ? " (использован)" : ""}`;

      if (!item.used) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = "Отметить как использованный";
        btn.style.marginLeft = "8px";
        btn.onclick = async () => {
          try {
            await request(`/items/${item.id}/use`, { method: "POST" });
            await refreshItems(includeUsed, expiring);
          } catch (err) {
            $("#add-item-result").textContent = `Ошибка: ${err.message}`;
          }
        };
        el.appendChild(btn);
      }

      list.appendChild(el);
    });
  } catch (err) {
    list.innerHTML = "";
    const error = document.createElement("li");
    error.textContent = `Не удалось загрузить продукты: ${err.message}`;
    list.appendChild(error);
  }
}

async function loadRecipe() {
  try {
    const recipe = await request("/recipes/expiring");
    const container = $("#recipe");
    container.innerHTML = `<strong>${recipe.title}</strong><p>Причина: ${recipe.expiry_reason}</p><p>Ингредиенты: ${recipe.ingredients.join(", ")}</p><p>Шаги:</p><ol>${recipe.steps.map((step) => `<li>${step}</li>`).join("")}</ol>`;
  } catch (err) {
    $("#recipe").textContent = "Нет доступных продуктов для рецепта.";
  }
}

async function loadNotifications() {
  const list = $("#notifications");

  try {
    const data = await request("/notifications?days=7");
    list.innerHTML = "";

    if (!data.length) {
      const empty = document.createElement("li");
      empty.textContent = "Уведомлений пока нет.";
      list.appendChild(empty);
      return;
    }

    data.forEach((notification) => {
      const li = document.createElement("li");
      li.textContent = `${notification.message} (${notification.days_until_expiry} дн.)`;
      list.appendChild(li);
    });
  } catch (err) {
    list.innerHTML = "";
    const error = document.createElement("li");
    error.textContent = `Не удалось загрузить уведомления: ${err.message}`;
    list.appendChild(error);
  }
}

function appendChatMessage(role, text) {
  const container = $("#chat-messages");
  const message = document.createElement("div");
  message.className = `chat-message ${role}`;
  message.textContent = text;
  container.appendChild(message);
}

$("#chat-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();

  const input = $("#chat-input");
  const status = $("#chat-status");
  const message = input.value.trim();
  if (!message) {
    return;
  }

  appendChatMessage("user", message);
  status.textContent = "ChatGPT думает...";
  input.value = "";

  try {
    const result = await request("/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        previous_response_id: previousResponseId,
      }),
    });

    previousResponseId = result.response_id;
    appendChatMessage("assistant", result.reply);
    status.textContent = "Ответ получен.";
  } catch (err) {
    appendChatMessage("assistant", `Ошибка: ${err.message}`);
    status.textContent = "Не удалось получить ответ.";
  }
});

$("#add-item-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();

  const payload = {
    name: $("#name").value.trim(),
    quantity: Number($("#quantity").value),
    unit: $("#unit").value.trim() || "шт",
    added_date: $("#added_date").value,
    expiry_date: $("#expiry_date").value,
  };

  try {
    await request("/items", { method: "POST", body: JSON.stringify(payload) });
    $("#add-item-result").textContent = "Продукт добавлен.";
    $("#add-item-form").reset();

    const today = new Date().toISOString().split("T")[0];
    $("#added_date").value = today;
    $("#expiry_date").value = today;

    await refreshItems();
  } catch (err) {
    $("#add-item-result").textContent = `Ошибка: ${err.message}`;
  }
});

$("#load-items").addEventListener("click", () => {
  refreshItems(false, false);
});

$("#load-expiring").addEventListener("click", () => {
  refreshItems(false, true);
});

$("#load-recipe").addEventListener("click", loadRecipe);
$("#load-notifications").addEventListener("click", loadNotifications);

window.addEventListener("load", async () => {
  const today = new Date().toISOString().split("T")[0];
  $("#added_date").value = today;
  $("#expiry_date").value = today;
  await refreshItems();
});
