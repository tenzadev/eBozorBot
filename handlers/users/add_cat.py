from aiogram import types
from data.config import ADMINS
from loader import dp, db, bot
from aiogram.dispatcher import FSMContext
from states.admin import AddCategory
from keyboards.default.main import main_menu_markup


@dp.message_handler(text="Kategoriya qo'shish", user_id=ADMINS)
@dp.message_handler(text="/add_cat", user_id=ADMINS)
async def add_cat_func(message: types.Message):
    await message.answer("Qo'shmoqchi bo'lgan kategoriya nomini kiriting")
    await AddCategory.title.set()


@dp.message_handler(user_id=ADMINS, state=AddCategory.title)
async def get_cat_title(message: types.Message, state: FSMContext):
    cat_title = message.text
    await state.update_data({"cat_title": cat_title})
    await message.answer("Kategoriyada nimalar bo'lish haqida ma'lumot kiriting")
    await AddCategory.next()


@dp.message_handler(user_id=ADMINS, state=AddCategory.desc)
async def get_cat_desc(message: types.Message, state: FSMContext):
    cat_desc = message.text
    await state.update_data({"cat_desc": cat_desc})
    await message.answer("Kategoriyaning rasmini yuboring")
    await AddCategory.next()


@dp.message_handler(content_types=["photo"], user_id=ADMINS, state=AddCategory.image)
async def get_cat_desc(message: types.Message, state: FSMContext):
    cat_image = message.photo[-1].file_id
    # await state.update_data({"cat_image_id": cat_image})
    data = await state.get_data()
    title = data.get("cat_title")
    desc = data.get("cat_desc")
    await db.add_cat(title=title, desc=desc, image_url=cat_image)
    await message.answer("Kategoriyaning saqlandi!", reply_markup=main_menu_markup(str(message.from_user.id)))
    await state.finish()

