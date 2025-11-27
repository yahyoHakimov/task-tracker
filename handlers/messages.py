from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.models import Task, TaskStatus
from database.connection import async_session_maker
from states import TaskStates
from keyboard import get_skip_description_keyboard
from utils import validate_task_title, validate_task_description
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(TaskStates.waiting_for_title)
async def process_task_title(message: Message, state: FSMContext):
    """Handle task title input"""
    title = message.text
    
    # Validate title
    is_valid, error_message = validate_task_title(title)
    
    if not is_valid:
        await message.answer(error_message)
        return
    
    # Store title in FSM context
    await state.update_data(title=title.strip())
    
    # Move to next state
    await state.set_state(TaskStates.waiting_for_description)
    
    await message.answer(
        "📋 Great! Now enter a description for your task (max 1000 characters).\n\n"
        "Or click Skip if you don't want to add a description:",
        reply_markup=get_skip_description_keyboard()
    )
    logger.info(f"User {message.from_user.id} entered task title: {title[:50]}")


@router.message(TaskStates.waiting_for_description)
async def process_task_description(message: Message, state: FSMContext):
    """Handle task description input"""
    description = message.text
    
    # Validate description
    is_valid, error_message = validate_task_description(description)
    
    if not is_valid:
        await message.answer(error_message)
        return
    
    # Get title from FSM context
    data = await state.get_data()
    title = data.get('title')
    
    # Save task to database
    async with async_session_maker() as session:
        try:
            new_task = Task(
                user_id=message.from_user.id,
                title=title,
                description=description.strip() if description else None,
                status=TaskStatus.PENDING
            )
            session.add(new_task)
            await session.commit()
            
            await message.answer(
                f"✅ Task created successfully!\n\n"
                f"📝 <b>{title}</b>\n"
                f"📋 {description[:100]}{'...' if len(description) > 100 else ''}\n\n"
                f"Use /list to view all your tasks."
            )
            logger.info(f"User {message.from_user.id} created task: {title[:50]}")
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            await message.answer(
                "❌ An error occurred while creating the task. Please try again."
            )
    
    # Clear FSM state
    await state.clear()