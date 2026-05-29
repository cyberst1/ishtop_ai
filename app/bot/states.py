"""All FSM groups."""
from aiogram.fsm.state import State, StatesGroup


class SearchSG(StatesGroup):
    role = State()       # jobseeker | employer
    query = State()
    browsing = State()


class AdminLoginSG(StatesGroup):
    password = State()


class AdminBalanceSG(StatesGroup):
    user_id = State()
    amount = State()


class AdminBroadcastSG(StatesGroup):
    text = State()
    confirm = State()


class AdvisorSG(StatesGroup):
    asking = State()


class BonusChannelAddSG(StatesGroup):
    chat_id = State()
    title = State()
    invite_link = State()
