from aiogram.dispatcher.filters.state import StatesGroup, State

class AddCategory(StatesGroup):
    title = State()
    desc = State()
    image = State()


class AddProduct(StatesGroup):
    cat = State()
    title = State()
    desc = State()
    image = State()
    price = State()