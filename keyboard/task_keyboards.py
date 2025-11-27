from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_skip_description_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with Skip button for description"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏭ Skip Description", callback_data="skip_description")
            ]
        ]
    )
    return keyboard


def get_task_actions_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """Keyboard with Complete and Delete buttons for a task"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Complete", callback_data=f"complete_{task_id}"),
                InlineKeyboardButton(text="🗑 Delete", callback_data=f"delete_{task_id}")
            ]
        ]
    )
    return keyboard