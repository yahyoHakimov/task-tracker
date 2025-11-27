from aiogram.fsm.state import State, StatesGroup


class TaskStates(StatesGroup):
    """States for task creation flow"""
    waiting_for_title = State()
    waiting_for_description = State()