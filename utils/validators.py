from typing import Tuple


def validate_task_title(title: str) -> Tuple[bool, str]:
    if not title or not title.strip():
        return False, "❌ Title cannot be empty. Please enter a task title."
    
    if len(title) > 200:
        return False, f"❌ Title is too long ({len(title)} characters). Maximum is 200 characters."
    
    return True, ""


def validate_task_description(description: str) -> Tuple[bool, str]:
    if len(description) > 1000:
        return False, f"❌ Description is too long ({len(description)} characters). Maximum is 1000 characters."
    
    return True, ""