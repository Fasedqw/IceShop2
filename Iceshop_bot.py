import asyncio
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    KeyboardButton, ReplyKeyboardMarkup, WebAppInfo,
    InlineKeyboardButton, InlineKeyboardMarkup
)

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = "9103844726:AAFER4K0rjPQsP4FDBHYiicJpP6Row87Ec8"
ADMIN_ID = 8915050007  # Твой числовой ID
# ВАЖНО: сюда нужно вставить URL, где будет лежать твой сайт (GitHub Pages / Vercel / etc.)
MINI_APP_URL = "https://fasedqw.github.io/IceShop2/"
# ===============================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_main_keyboard():
    web_app = WebAppInfo(url=MINI_APP_URL)
    btn = KeyboardButton(text="🛒 Открыть каталог Ice Shop", web_app=web_app)
    return ReplyKeyboardMarkup(keyboard=[[btn]], resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 <b>Добро пожаловать в Ice Shop!</b>\n\n"
        "🍦 У нас самое вкусное мороженое и холодные напитки.\n"
        "Нажми кнопку ниже, чтобы открыть каталог и оформить заказ:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@dp.message(F.text)
async def handle_text(message: types.Message):
    """Обычные текстовые сообщения — просто показываем кнопку каталога."""
    await message.answer(
        "🛍 Чтобы посмотреть товары, нажми кнопку ниже:",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    """Получаем данные из Mini App (оформленный заказ)."""
    try:
        order_data = json.loads(message.web_app_data.data)
    except json.JSONDecodeError:
        await message.answer("❌ Ошибка: не удалось прочитать данные заказа.")
        return

    if order_data.get("action") != "order":
        return

    await send_order_to_admin(order_data, message.from_user, message)


async def send_order_to_admin(order_data: dict, user: types.User, message: types.Message):
    """Формируем красивое сообщение с заказом и отправляем админу."""
    items = order_data.get("items", [])
    items_list = "\n".join([f"• {it['name']} × {it.get('qty', 1)} — {it['price']} ₽" for it in items])

    contact = order_data.get("contact", {})
    total = order_data.get("total", 0)

    text = (
        f"📦 <b>Новый заказ в Ice Shop!</b>\n\n"
        f"👤 <b>Клиент:</b> {user.full_name} "
        f"(@{user.username or 'нет юзернейма'})\n"
        f"🆔 <code>{user.id}</code>\n\n"
        f"🛍 <b>Товары:</b>\n{items_list or '—'}\n\n"
        f"💰 <b>Итого:</b> <b>{total} ₽</b>\n\n"
        f"📞 Телефон: {contact.get('phone', 'не указан')}\n"
        f"📍 Адрес: {contact.get('address', 'не указан')}\n"
        f"🚪 Подъезд: {contact.get('entrance', '—')}\n"
        f"🏠 Этаж/квартира: {contact.get('floorApt', '—')}\n"
        f"💬 Комментарий: {contact.get('comment', '—')}"
    )

    # Кнопки для админа
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data="order_accept"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data="order_reject")],
        [InlineKeyboardButton(text="💬 Написать клиенту",
                              url=f"tg://user?id={user.id}")]
    ])

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="HTML", reply_markup=kb)
        await message.answer(
            "✅ <b>Заказ принят!</b>\n"
            "Менеджер свяжется с тобой в течение 10 минут для подтверждения. 🚀",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Не удалось отправить заказ админу: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуй позже.")


@dp.callback_query(F.data.in_(["order_accept", "order_reject"]))
async def order_callbacks(callback: types.CallbackQuery):
    await callback.answer()
    if callback.data == "order_accept":
        await callback.message.edit_text(callback.message.text + "\n\n✅ <b>Статус: Принят</b>",
                                         parse_mode="HTML")
    else:
        await callback.message.edit_text(callback.message.text + "\n\n❌ <b>Статус: Отклонён</b>",
                                         parse_mode="HTML")


async def main():
    print("🤖 Бот Ice Shop запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())