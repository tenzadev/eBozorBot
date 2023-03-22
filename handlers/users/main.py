from aiogram import types
from loader import dp, db, bot
from keyboards.default.main import make_cats_markup, make_products_markup, numbers, main_menu_markup
from states.main import ShopState
from aiogram.dispatcher import FSMContext


@dp.message_handler(text="🛍 Buyurtma berish")
async def get_cats_list(message: types.Message):
    user = await db.select_user(telegram_id=message.from_user.id)
    if user:
        cart = await db.select_user_cart(user_id=user["id"])
        if not cart:
            await db.create_cart(user_id=user["id"])
    markup = await make_cats_markup()
    await message.answer("Nimadan boshlaymiz? Kategoriyani tanlang!", reply_markup=markup)
    await ShopState.category.set()


@dp.message_handler(state=ShopState.category)
async def get_cat(message: types.Message, state: FSMContext):
    cat_title = message.text
    cat = await db.select_category(title=cat_title)
    await state.update_data({"cat_id": cat["id"]})
    markup = await make_products_markup(cat_id=cat["id"])
    await message.answer_photo(photo=cat["image_url"], caption=cat["description"], reply_markup=markup)
    await ShopState.next()


@dp.message_handler(state=ShopState.product)
async def get_product(message: types.Message, state: FSMContext):
    product_title = message.text
    data = await state.get_data()
    cat_id = data.get("cat_id")
    products = await db.select_product(title=product_title, cat_id=cat_id)
    product = products[0]
    msg = f"<b>{product['title']}\n\nNarx: {product['price']} $</b>\n\n<i>{product['description']}</i>"
    await state.update_data({"prod_id": product["id"], "prod_title": product['title'], "prod_price": product['price']})
    await message.answer_photo(photo=product["image_url"], caption=msg, reply_markup=numbers)
    await ShopState.next()


@dp.message_handler(lambda message: int(message.text) > 0, state=ShopState.quantity) 
async def get_quantity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = await db.select_user(telegram_id=message.from_user.id)
    cart = await db.select_user_cart(user_id=user["id"])
    product_id = data.get("prod_id")
    title = data.get("prod_title")
    price = data.get("prod_price")
    msg = f"{title} ({price} $) x {message.text} = {int(message.text) * price} $"
    check_product = await db.select_cart_item(cart_id=cart["id"], product_id=product_id)
    if check_product:
        old_quantity = check_product["quantity"]
        new_quantity = int(message.text)
        await db.update_cart_item(cart_id=cart["id"], product_id=product_id, quantity=old_quantity + new_quantity)
    else:
        await db.add_cart_item(cart_id=cart["id"], product_id=product_id, quantity=int(message.text))
    await message.answer(msg, reply_markup=main_menu_markup(str(message.from_user.id)))
    await state.finish()