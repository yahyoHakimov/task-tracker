from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.models import Task, TaskStatus
from database.connection import async_session_maker
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "skip_description")
async def skip_description_callback(callback: CallbackQuery, state: FSMContext):
    """Handle skip description button"""
    # Get title from FSM context
    data = await state.get_data()
    title = data.get('title')
    
    # Save task to database without description
    async with async_session_maker() as session:
        try:
            new_task = Task(
                user_id=callback.from_user.id,
                title=title,
                description=None,
                status=TaskStatus.PENDING
            )
            session.add(new_task)
            await session.commit()
            
            await callback.message.edit_text(
                f"✅ Task created successfully!\n\n"
                f"📝 <b>{title}</b>\n\n"
                f"Use /list to view all your tasks."
            )
            logger.info(f"User {callback.from_user.id} created task without description: {title[:50]}")
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            await callback.message.answer(
                "❌ An error occurred while creating the task. Please try again."
            )
    
    # Clear FSM state
    await state.clear()
    
    # Answer callback to remove loading state
    await callback.answer()


@router.callback_query(F.data.startswith("complete_"))
async def complete_task_callback(callback: CallbackQuery):
    """Handle complete task button"""
    # Extract task_id from callback data
    task_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        try:
            # Get the task
            result = await session.execute(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                await callback.answer("❌ Task not found!", show_alert=True)
                return
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            await session.commit()
            
            # Update message to show it's completed
            completed_text = f"✅ <b>COMPLETED</b>\n\n"
            completed_text += f"📝 <s>{task.title}</s>\n"
            
            if task.description:
                desc = task.description[:150]
                if len(task.description) > 150:
                    desc += "..."
                completed_text += f"📋 <s>{desc}</s>\n"
            
            completed_text += f"✅ Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}"
            
            await callback.message.edit_text(completed_text)
            await callback.answer("✅ Task marked as completed!")
            
            logger.info(f"User {user_id} completed task {task_id}: {task.title[:50]}")
            
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            await callback.answer("❌ Error completing task. Please try again.", show_alert=True)


@router.callback_query(F.data.startswith("delete_"))
async def delete_task_callback(callback: CallbackQuery):
    """Handle delete task button"""
    # Extract task_id from callback data
    task_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        try:
            # Get the task
            result = await session.execute(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                await callback.answer("❌ Task not found!", show_alert=True)
                return
            
            task_title = task.title
            
            # Delete the task
            await session.delete(task)
            await session.commit()
            
            # Update message to show it's deleted
            await callback.message.edit_text(
                f"🗑 <b>DELETED</b>\n\n"
                f"📝 <s>{task_title}</s>\n\n"
                f"This task has been permanently removed."
            )
            await callback.answer("🗑 Task deleted!")
            
            logger.info(f"User {user_id} deleted task {task_id}: {task_title[:50]}")
            
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            await callback.answer("❌ Error deleting task. Please try again.", show_alert=True)