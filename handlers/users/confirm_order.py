from aiogram import types
from loader import dp, db, bot
from aiogram.dispatcher import FSMContext
from utils.misc.product import Product
from aiogram.types import LabeledPrice
from utils.misc.shippings import REGULAR_SHIPPING, FAST_SHIPPING, PICKUP_SHIPPING
from data.config import ADMINS


@dp.message_handler(text="🛒 Rasmiylashtirish", state="*")
async def confirm_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    call_message = data.get("message")
    total_price = data.get("total_price", 0)
    msg = ""
    prices = []
    if call_message:
        await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=call_message["message_id"], reply_markup=None)
    user = await db.select_user(telegram_id=message.from_user.id)
    cart = await db.select_user_cart(user_id=user["id"])
    cart_items = await db.select_user_cart_items(cart_id=cart["id"])
    order = await db.add_order(user_id=user["id"], total_price=total_price)
    for cart_item in cart_items:
        await db.add_order_item(order_id=order["id"], product_id=cart_item["product_id"], quantity=cart_item["quantity"])
        products = await db.select_product(id=cart_item["product_id"])
        product = products[0]
        total_price += cart_item["quantity"] * product['price']
        msg += f"{product['title']} ({product['price']} $) x {cart_item['quantity']} = {product['price'] * cart_item['quantity']} $\n"
        prices.append(
            LabeledPrice(label=product['title'], amount=int(product['price'] * cart_item['quantity'] * 100))
        )
    await db.update_order_price(order_id=order["id"], price=total_price)
    # prices.append(LabeledPrice(label="Yektazib berish", amount=5000000))
    # Send Invoice to user
    invoice = Product(
        title="To'lov qilish uchun chek",
        description=msg,
        currency="UZS",
        prices=prices,
        start_parameter="create_invoice",
        need_email=True,
        need_name=True,
        need_phone_number=True,
        need_shipping_address=True, # foydalanuvchi manzilini kiritishi shart
        is_flexible=True
    )
    await message.answer("<b>Buyurtmangiz saqlandi!</b>")
    await bot.send_invoice(chat_id=message.from_user.id, **invoice.generate_invoice(), payload="payload:invoice")
    await db.clear_cart(cart_id=cart["id"])
    await state.update_data({"order_id": order["id"]})


@dp.shipping_query_handler(state="*")
async def choose_shipping(query: types.ShippingQuery):
    if query.shipping_address.country_code != "UZ":
        await bot.answer_shipping_query(shipping_query_id=query.id,
                                        ok=False,
                                        error_message="Chet elga yetkazib bera olmaymiz")
    elif query.shipping_address.city.lower() == "urganch":
        await bot.answer_shipping_query(shipping_query_id=query.id,
                                        shipping_options=[FAST_SHIPPING, REGULAR_SHIPPING, PICKUP_SHIPPING],
                                        ok=True)
    else:
        await bot.answer_shipping_query(shipping_query_id=query.id,
                                        shipping_options=[REGULAR_SHIPPING],
                                        ok=True)

@dp.pre_checkout_query_handler(state="*")
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("order_id")
    await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,
                                        ok=True)
    await bot.send_message(chat_id=pre_checkout_query.from_user.id,
                           text="Xaridingiz uchun rahmat!")
    await bot.send_message(chat_id=ADMINS[0],
                           text=f"Quyidagi mahsulot sotildi: {pre_checkout_query.invoice_payload}\n"
                                f"ID: {pre_checkout_query.id}\n"
                                f"Telegram user: {pre_checkout_query.from_user.first_name}\n"
                                f"Xaridor: {pre_checkout_query.order_info.name}, tel: {pre_checkout_query.order_info.phone_number}")
    await db.update_order_paid(order_id=order_id, paid=True)    

