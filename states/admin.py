from aiogram.dispatcher.filters.state import StatesGroup, State

class AddCategory(StatesGroup):
    title = State()
    desc = State()
    image = State()