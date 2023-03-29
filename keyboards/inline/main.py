from loader import db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def make_cats_markup():
    cats_markup = InlineKeyboardMarkup(row_width=1)
    all_cats = await db.select_all_cats()
    for cat in all_cats:
        cats_markup.insert(InlineKeyboardButton(text=cat["title"], callback_data=cat["title"]))
    return cats_markup