from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp, db, bot
from data.config import ADMINS, CHANNELS
from keyboards.inline.subscription import check_button
from aiogram.dispatcher import FSMContext
from keyboards.default.main import main_menu_markup
from utils.misc.check_user import check_subs_user


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    name = message.from_user.username
    user = await db.select_user(telegram_id=message.from_user.id)
    if user is None:
        user = await db.add_user(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )
        # ADMINGA xabar beramiz
        count = await db.count_users()
        msg = f"@{user[2]} bazaga qo'shildi.\nBazada {count} ta foydalanuvchi bor."
        await bot.send_message(chat_id=ADMINS[0], text=msg)
    # user = await db.select_user(telegram_id=message.from_user.id)
    else:
        await bot.send_message(chat_id=ADMINS[0], text=f"@{name} bazaga oldin qo'shilgan")
    
    user_id = message.from_user.id
    final_status, result = await check_subs_user(user_id=user_id)

    if final_status:
        await message.answer(f"Xush kelibsiz! @{name}", reply_markup=main_menu_markup(str(message.from_user.id)))
    else:
        channels_format = str()
        for channel in CHANNELS:
            chat = await bot.get_chat(channel)
            invite_link = await chat.export_invite_link()
            channels_format += f"➡️ <a href='{invite_link}'><b>{chat.title}</b></a>\n"

        await message.answer(f"Quyidagi kanallarga obuna bo'ling: \n\n"
                            f"{channels_format}",
                            reply_markup=check_button,
                            disable_web_page_preview=True)
