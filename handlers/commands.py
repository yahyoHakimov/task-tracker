from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.models import User
from database.connection import async_session_maker
from states.task_states import TaskStates
import logging
from datetime import datetime
from database.models import Task, TaskStatus
from keyboard import get_task_actions_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """Handle /start command - welcome and register user"""
    # Clear any active state
    await state.clear()
    
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name or "User"
    
    async with async_session_maker() as session:
        try:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                # User exists - welcome back
                await message.answer(
                    f"👋 Welcome back, {first_name}!\n\n"
                    f"Available commands:\n"
                    f"/add - Add a new task\n"
                    f"/list - View your pending tasks\n"
                    f"/completed - View completed tasks\n"
                    f"/cancel - Cancel current operation"
                )
                logger.info(f"Existing user {user_id} used /start")
            else:
                # New user - register
                new_user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name
                )
                session.add(new_user)
                await session.commit()
                
                await message.answer(
                    f"👋 Hello, {first_name}! Welcome to Task Tracker Bot!\n\n"
                    f"I'll help you manage your tasks efficiently.\n\n"
                    f"Available commands:\n"
                    f"/add - Add a new task\n"
                    f"/list - View your pending tasks\n"
                    f"/completed - View completed tasks\n"
                    f"/cancel - Cancel current operation\n\n"
                    f"Let's get started! Use /add to create your first task."
                )
                logger.info(f"New user registered: {user_id} - {first_name}")
                
        except Exception as e:
            logger.error(f"Error in start_command: {e}")
            await message.answer(
                "❌ An error occurred. Please try again later."
            )


@router.message(Command("add"))
async def add_task_command(message: Message, state: FSMContext):
    """Handle /add command - start task creation flow"""
    await state.set_state(TaskStates.waiting_for_title)
    await message.answer(
        "📝 Let's create a new task!\n\n"
        "Please enter the task title (max 200 characters):\n\n"
        "Use /cancel to abort."
    )
    logger.info(f"User {message.from_user.id} started adding a task")


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    """Handle /cancel command - cancel any active operation"""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "✅ No active operation to cancel.\n\n"
            "Use /add to create a task or /list to view your tasks."
        )
    else:
        await state.clear()
        await message.answer(
            "❌ Operation cancelled.\n\n"
            "Use /add to create a task or /list to view your tasks."
        )
        logger.info(f"User {message.from_user.id} cancelled operation from state: {current_state}")


@router.message(Command("list"))
async def list_tasks_command(message: Message, state: FSMContext):
    """Handle /list command - show all pending tasks"""
    await state.clear()  # Clear any active state
    
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        try:
            # Get all pending tasks for user
            result = await session.execute(
                select(Task)
                .where(Task.user_id == user_id)
                .where(Task.status == TaskStatus.PENDING)
                .order_by(Task.created_at.desc())
            )
            tasks = result.scalars().all()
            
            if not tasks:
                await message.answer(
                    "📝 You have no pending tasks!\n\n"
                    "Use /add to create your first task."
                )
                logger.info(f"User {user_id} has no pending tasks")
                return
            
            await message.answer(
                f"📋 <b>Your Pending Tasks ({len(tasks)}):</b>\n"
            )
            
            # Send each task as a separate message with action buttons
            for task in tasks:
                task_text = f"📝 <b>{task.title}</b>\n"
                
                if task.description:
                    # Truncate long descriptions
                    desc = task.description[:150]
                    if len(task.description) > 150:
                        desc += "..."
                    task_text += f"📋 {desc}\n"
                
                task_text += f"🕐 Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}"
                
                await message.answer(
                    task_text,
                    reply_markup=get_task_actions_keyboard(task.id)
                )
            
            logger.info(f"User {user_id} listed {len(tasks)} pending tasks")
            
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            await message.answer(
                "❌ An error occurred while fetching tasks. Please try again."
            )


@router.message(Command("completed"))
async def completed_tasks_command(message: Message, state: FSMContext):
    """Handle /completed command - show all completed tasks"""
    await state.clear()  # Clear any active state
    
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        try:
            # Get all completed tasks for user
            result = await session.execute(
                select(Task)
                .where(Task.user_id == user_id)
                .where(Task.status == TaskStatus.COMPLETED)
                .order_by(Task.completed_at.desc())
            )
            tasks = result.scalars().all()
            
            if not tasks:
                await message.answer(
                    "✅ You haven't completed any tasks yet!\n\n"
                    "Use /list to view your pending tasks."
                )
                logger.info(f"User {user_id} has no completed tasks")
                return
            
            # Build message with all completed tasks
            text = f"✅ <b>Completed Tasks ({len(tasks)}):</b>\n\n"
            
            for i, task in enumerate(tasks, 1):
                text += f"{i}. <b>{task.title}</b>\n"
                
                if task.description:
                    desc = task.description[:100]
                    if len(task.description) > 100:
                        desc += "..."
                    text += f"   📋 {desc}\n"
                
                if task.completed_at:
                    text += f"   ✅ Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}\n"
                
                text += "\n"
            
            await message.answer(text)
            logger.info(f"User {user_id} viewed {len(tasks)} completed tasks")
            
        except Exception as e:
            logger.error(f"Error fetching completed tasks: {e}")
            await message.answer(
                "❌ An error occurred while fetching completed tasks. Please try again."
            )

@router.message(Command("stats"))
async def stats_command(message: Message, state: FSMContext):
    """Handle /stats command - show user statistics"""
    await state.clear()
    
    user_id = message.from_user.id
    
    async with async_session_maker() as session:
        try:
            # Get all tasks
            result = await session.execute(
                select(Task).where(Task.user_id == user_id)
            )
            all_tasks = result.scalars().all()
            
            # Count by status
            pending_count = sum(1 for t in all_tasks if t.status == TaskStatus.PENDING)
            completed_count = sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED)
            total_count = len(all_tasks)
            
            # Calculate completion rate
            completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
            
            # Get user info
            user_result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                await message.answer("❌ User not found. Please use /start first.")
                return
            
            # Build stats message
            stats_text = f"📊 <b>Your Statistics</b>\n\n"
            stats_text += f"👤 User: {user.first_name}\n"
            stats_text += f"📅 Member since: {user.created_at.strftime('%Y-%m-%d')}\n\n"
            stats_text += f"📝 <b>Tasks Overview:</b>\n"
            stats_text += f"   • Total tasks: {total_count}\n"
            stats_text += f"   • Pending: {pending_count} ⏳\n"
            stats_text += f"   • Completed: {completed_count} ✅\n"
            stats_text += f"   • Completion rate: {completion_rate:.1f}%\n\n"
            
            if completed_count > 0:
                # Get most recent completed task
                completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
                most_recent = max(completed_tasks, key=lambda t: t.completed_at)
                stats_text += f"🎯 Last completed: <b>{most_recent.title}</b>\n"
                stats_text += f"   ({most_recent.completed_at.strftime('%Y-%m-%d %H:%M')})\n"
            
            await message.answer(stats_text)
            logger.info(f"User {user_id} viewed statistics")
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            await message.answer(
                "❌ An error occurred while fetching statistics. Please try again."
            )


@router.message(Command("help"))
async def help_command(message: Message, state: FSMContext):
    """Handle /help command - show help information"""
    await state.clear()
    
    help_text = (
        "📚 <b>Task Tracker Bot - Help</b>\n\n"
        "<b>Available Commands:</b>\n\n"
        "🆕 <b>Creating Tasks:</b>\n"
        "/add - Create a new task\n"
        "   • You'll be asked for a title (required)\n"
        "   • Then for a description (optional)\n"
        "   • Use /cancel anytime to abort\n\n"
        "📋 <b>Viewing Tasks:</b>\n"
        "/list - View all pending tasks\n"
        "/completed - View completed tasks\n"
        "/stats - View your statistics\n\n"
        "⚙️ <b>Task Actions:</b>\n"
        "   • ✅ Complete - Mark task as done\n"
        "   • 🗑 Delete - Remove task permanently\n\n"
        "🛠 <b>Other Commands:</b>\n"
        "/cancel - Cancel current operation\n"
        "/help - Show this help message\n"
        "/start - Restart the bot\n\n"
        "💡 <b>Tips:</b>\n"
        "   • Tasks are saved automatically\n"
        "   • Completed tasks are kept for your records\n"
        "   • Each task can have a title up to 200 characters\n"
        "   • Descriptions can be up to 1000 characters\n\n"
        "Need more help? Contact @YourUsername"
    )
    
    await message.answer(help_text)
    logger.info(f"User {message.from_user.id} viewed help")