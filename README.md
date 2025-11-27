# Task Tracker Bot

A Telegram bot for managing personal tasks with PostgreSQL database.

## Features

- ✅ Create tasks with title and optional description
- ✅ List pending tasks
- ✅ Mark tasks as completed
- ✅ Delete tasks
- ✅ View completed tasks
- ✅ View statistics
- ✅ FSM (Finite State Machine) for multi-step flows
- ✅ Input validation
- ✅ Error handling
- ✅ Middleware logging

## Architecture

### Directory Structure
```
task_bot/
├── bot.py                    # Entry point
├── config.py                 # Configuration
├── database/
│   ├── models.py            # SQLAlchemy models
│   └── connection.py        # DB connection
├── handlers/
│   ├── commands.py          # Command handlers
│   ├── messages.py          # Message handlers
│   └── callbacks.py         # Callback handlers
├── states/
│   └── task_states.py       # FSM states
├── keyboards/
│   └── task_keyboards.py    # Inline keyboards
├── middleware/
│   └── logging_middleware.py # Middleware
└── utils/
    ├── validators.py         # Input validation
    └── error_handler.py      # Error handling
```

### Tech Stack
- Python 3.11+
- aiogram 3.15.0
- PostgreSQL
- SQLAlchemy (async)

### SOLID Principles Applied

1. **Single Responsibility**: Each file/class has one clear purpose
2. **Open/Closed**: Easy to extend with new commands
3. **Liskov Substitution**: Handlers are interchangeable
4. **Interface Segregation**: Separate routers for different handler types
5. **Dependency Inversion**: Handlers depend on abstractions (FSM, database interfaces)

## Setup

1. Install PostgreSQL
2. Create database: `CREATE DATABASE task_bot_db;`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure `.env` file
5. Run: `python bot.py`

## Commands

- `/start` - Start the bot
- `/add` - Add new task
- `/list` - View pending tasks
- `/completed` - View completed tasks
- `/stats` - View statistics
- `/help` - Show help
- `/cancel` - Cancel operation

## Database Schema

### Users Table
- user_id (PK)
- username
- first_name
- created_at

### Tasks Table
- id (PK)
- user_id (FK)
- title
- description
- status (pending/completed)
- created_at
- completed_at