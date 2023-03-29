from aiogram import types
from loader import dp
from utils.misc.check_user import check_subs_user
from keyboards.default.main import main_menu_markup
from keyboards.inline.subscription import check_button


@dp.callback_query_handler(text="check_subs")
async def check_sub_user(call: types.CallbackQuery):
    
    user_id = call.from_user.id
    name = call.from_user.full_name
    final_status, result = await check_subs_user(user_id=user_id)
    if final_status:
        await call.answer("Obunalar tekshirilmoqda ...")
        await call.message.delete()
        await call.message.answer(f"Xush kelibsiz! @{name}", reply_markup=main_menu_markup(str(user_id)))
    else:
        try:
            await call.message.edit_text(result, reply_markup=check_button, disable_web_page_preview=True)
        except Exception as error:
            await call.answer("Barcha kanalga obuna bo'lshingiz kerak", show_alert=True)
