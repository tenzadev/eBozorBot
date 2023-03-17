from aiogram.dispatcher.filters.state import StatesGroup, State


class ShopState(StatesGroup):
    category = State()
    product = State()
    quantity = State()
