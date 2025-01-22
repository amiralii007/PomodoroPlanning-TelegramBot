import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram import error

# Pomodoro timer variables
POMODORO_PRESETS = {
    "classic": {"focus": 25 * 60, "rest": 5 * 60, "name": "Classic (25/5)"},
    "long": {"focus": 50 * 60, "rest": 10 * 60, "name": "Long (50/10)"},
    "short": {"focus": 15 * 60, "rest": 3 * 60, "name": "Short (15/3)"}
}

timer_tasks = {}  # Store timer tasks per user

# Task management
class Task:
    def __init__(self, description, due_date=None):
        self.description = description
        self.due_date = due_date
        self.completed = False
        self.created_at = datetime.now()

tasks = {}  # Dictionary to store tasks per user


# Start command - Main menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks.setdefault(user_id, [])

    if update.callback_query:
        message = update.callback_query.message
        await update.callback_query.answer()  # Acknowledge the callback
    else:
        message = update.message

    if message and message.from_user.id == context.bot.id:
        try:
            keyboard = [
                [InlineKeyboardButton("🍅 Pomodoro", callback_data="pomodoro")],
                [InlineKeyboardButton("📝 Tasks", callback_data="tasks")],
                [InlineKeyboardButton("⏰ Reminders", callback_data="reminders")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.edit_text(
                "Welcome to the Enhanced Productivity Bot!\n\n"
                "Choose an option to get started:",
                reply_markup=reply_markup
            )
        except error.BadRequest as e:
            print(f"Failed to edit message: {e}")
    else:
        keyboard = [
            [InlineKeyboardButton("🍅 Pomodoro", callback_data="pomodoro")],
            [InlineKeyboardButton("📝 Tasks", callback_data="tasks")],
            [InlineKeyboardButton("⏰ Reminders", callback_data="reminders")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Welcome to the Enhanced Productivity Bot!\n\n"
                 "Choose an option to get started:",
            reply_markup=reply_markup
        )


# Pomodoro Menu
async def pomodoro_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(preset_info["name"], callback_data=f"start_pomodoro_{preset}")]
        for preset, preset_info in POMODORO_PRESETS.items()
    ]
    keyboard.append([InlineKeyboardButton("➕ Custom Pomodoro", callback_data="custom_pomodoro")])
    keyboard.append([InlineKeyboardButton("⏹ Stop Pomodoro", callback_data="stop_pomodoro")])
    keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "Choose your Pomodoro preset or set your own:\n\n"
        "• Classic: 25min focus, 5min rest\n"
        "• Long: 50min focus, 10min rest\n"
        "• Short: 15min focus, 3min rest",
        reply_markup=reply_markup
    )


# Custom Pomodoro timer setup
async def custom_pomodoro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔙 Back to Pomodoro Menu", callback_data="pomodoro")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "Set your own Pomodoro timer:\n\n"
        "Send your focus and rest times separated by a space (e.g., '30 7' for 30 minutes focus, 7 minutes rest).",
        reply_markup=reply_markup
    )
    context.user_data["custom_pomodoro"] = True


# Save custom Pomodoro and start the timer
async def save_custom_pomodoro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("custom_pomodoro"):
        user_id = update.effective_user.id
        try:
            times = update.message.text.strip().split()
            if len(times) != 2:
                raise ValueError("Invalid input format. Please enter both focus and rest times.")
            focus_time, rest_time = map(int, times)
            if focus_time <= 0 or rest_time <= 0:
                raise ValueError("Focus and rest times must be positive integers.")

            # Send message with cancel button and remaining time updates
            keyboard = [
                [InlineKeyboardButton("❌ Cancel Pomodoro", callback_data="cancel_pomodoro")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"Custom Pomodoro started!\nFocus time: {focus_time} minutes\nRest time: {rest_time} minutes",
                reply_markup=reply_markup
            )

            # Create Pomodoro task with the provided focus and rest times
            timer_tasks[user_id] = asyncio.create_task(
                pomodoro_timer(update, focus_time * 60, rest_time * 60)
            )

        except ValueError as e:
            await update.message.reply_text(str(e))
        
        context.user_data["custom_pomodoro"] = False

# Start Pomodoro timer with presets
async def start_pomodoro(update: Update, context: ContextTypes.DEFAULT_TYPE, preset="classic"):
    user_id = update.effective_user.id
    if user_id in timer_tasks:
        timer_tasks[user_id].cancel()

    preset_info = POMODORO_PRESETS[preset]
    timer_tasks[user_id] = asyncio.create_task(
        pomodoro_timer(update, preset_info["focus"], preset_info["rest"])
    )
    
    await update.callback_query.edit_message_text(
        f"Pomodoro started: {preset_info['name']}\n"
        f"Focus time: {preset_info['focus']//60} minutes\n"
        f"Rest time: {preset_info['rest']//60} minutes"
    )



async def pomodoro_timer(update, focus_time, rest_time):
    user_id = update.effective_user.id
    try:
        # Send the focus time message and start the Pomodoro with the cancel button
        keyboard = [
            [InlineKeyboardButton("❌ Cancel Pomodoro", callback_data="cancel_pomodoro")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Ensure you're replying to the correct message
        await update.callback_query.message.reply_text("🍅 Focus time started!", reply_markup=reply_markup)
        
        # Send the initial remaining time for focus period
        await update.callback_query.message.reply_text(f"⏳ {focus_time // 60} minutes remaining in focus time")
        
        # Focus period
        while focus_time > 0:
            await asyncio.sleep(60)  # Wait for one minute
            focus_time -= 60
            # Update remaining focus time every minute
            await update.callback_query.message.reply_text(f"⏳ {focus_time // 60} minutes remaining in focus time")

        # Focus time finished, start rest time
        await update.callback_query.message.reply_text("☕️ Rest time started!")

        # Send the initial remaining time for rest period
        await update.callback_query.message.reply_text(f"⏳ {rest_time // 60} minutes remaining in rest time")

        # Rest period
        while rest_time > 0:
            await asyncio.sleep(60)  # Wait for one minute
            rest_time -= 60
            # Update remaining rest time every minute
            await update.callback_query.message.reply_text(f"⏳ {rest_time // 60} minutes remaining in rest time")

        # After rest time ends, go back to the main menu
        await update.callback_query.message.reply_text("🔄 Pomodoro cycle completed! Going back to the main menu...")

        # Return to main menu after both focus and rest periods are done
        await start(update, context)

    except asyncio.CancelledError:
        await update.callback_query.message.reply_text("⏹ Pomodoro session stopped.")


# Handle the cancel button callback
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "pomodoro":
        await pomodoro_menu(update, context)
    elif data.startswith("start_pomodoro_"):
        preset = data.split("_")[2]
        await start_pomodoro(update, context, preset)
    elif data == "stop_pomodoro":
        user_id = update.effective_user.id
        if user_id in timer_tasks:
            timer_tasks[user_id].cancel()
            del timer_tasks[user_id]
        await query.edit_message_text("Pomodoro stopped.")
    elif data == "cancel_pomodoro":
        user_id = update.effective_user.id
        if user_id in timer_tasks:
            timer_tasks[user_id].cancel()
            del timer_tasks[user_id]
        await query.edit_message_text("Pomodoro session canceled.")
        await start(update, context)  # Return to main menu immediately after cancellation
    elif data == "custom_pomodoro":
        await custom_pomodoro(update, context)
    elif data == "main_menu":
        await start(update, context)
    elif data == "tasks":
        await query.edit_message_text("Choose an option:\n\n"
                                      "• Add Task\n"
                                      "• List Tasks\n"
                                      "• Mark Task as Completed")
    elif data == "reminders":
        await query.edit_message_text("To set a reminder, send me the time in HH:MM format.")

# Add a task
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task_description = update.message.text.strip()
    if task_description:
        task = Task(description=task_description)
        tasks[user_id].append(task)
        await update.message.reply_text(f"Task added: {task_description}")
    else:
        await update.message.reply_text("Please provide a task description.")

# List all tasks
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_tasks = tasks.get(user_id, [])
    
    if not user_tasks:
        await update.message.reply_text("You have no tasks.")
        return

    task_list = "\n".join(f"{i+1}. {task.description} {'✅' if task.completed else '❌'}"
                         for i, task in enumerate(user_tasks))
    await update.message.reply_text(f"Your tasks:\n\n{task_list}")

# Mark a task as completed
async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task_index = int(update.message.text.strip()) - 1  # Convert to zero-based index

    if 0 <= task_index < len(tasks[user_id]):
        tasks[user_id][task_index].completed = True
        await update.message.reply_text(f"Task {task_index + 1} marked as completed.")
    else:
        await update.message.reply_text("Invalid task number.")

# Set a reminder
async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        reminder_time_str = update.message.text.strip().split(" ")[1]  # Expecting "reminder <time>"
        reminder_time = datetime.strptime(reminder_time_str, "%H:%M")  # Expecting time format HH:MM
        
        reminder_time = reminder_time.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)

        # Adjust if reminder time has passed today
        if reminder_time < datetime.now():
            reminder_time = reminder_time.replace(day=datetime.now().day + 1)
        
        delay = (reminder_time - datetime.now()).total_seconds()

        await update.message.reply_text(f"Reminder set for {reminder_time.strftime('%H:%M')}")

        # Wait and send reminder
        await asyncio.sleep(delay)
        await update.message.reply_text(f"Reminder: It's {reminder_time.strftime('%H:%M')}!")
        
    except Exception as e:
        await update.message.reply_text(f"Failed to set reminder. Error: {e}")

# Main function to start the bot
def main():
    application = Application.builder().token("API_TOKEN").build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Message handlers for custom Pomodoro and tasks
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, save_custom_pomodoro))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, add_task))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, list_tasks))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, complete_task))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, set_reminder))
    application.run_polling()


if __name__ == "__main__":
    main()
