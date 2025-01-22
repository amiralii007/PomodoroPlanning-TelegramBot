# PomodoroPlanning-TelegramBot

This project is a Telegram bot designed to help you manage your productivity with Pomodoro timers, task management, and reminders. It's built using Python, asyncio, and the `python-telegram-bot` library.

The bot allows users to:
- Start Pomodoro timers with multiple presets (Classic, Long, Short) or custom timers.
- Add, list, and mark tasks as completed.
- Set and receive reminders at specified times.

**Note:** The connection between the database (MongoDB) and the code has not been fully completed yet.

## Features

- **Pomodoro Timer:**
  - Supports classic, long, and short Pomodoro presets.
  - Users can set custom Pomodoro timers.
  - Timer status updates every minute with the option to cancel.

- **Task Management:**
  - Add tasks with descriptions.
  - List all tasks and mark them as completed.

- **Reminder System:**
  - Set reminders at specified times in the format `HH:MM`.

## Requirements

- Python 3.8 or higher
- MongoDB running locally or on a server
- `python-telegram-bot` library

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/productivity-bot.git
   cd productivity-bot
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up MongoDB:
   - Make sure MongoDB is running locally or set the `MONGO_URI` to your remote MongoDB URI in the code.

4. Replace the Telegram bot token:
   - Create a new Telegram bot through [BotFather](https://core.telegram.org/bots#botfather) and replace the token in the `main()` function:
     ```python
     application = Application.builder().token("YOUR_BOT_TOKEN").build()
     ```

5. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

Once the bot is running, you can interact with it by sending `/start` to the bot.

- **Pomodoro Timer**: 
  - You can choose from presets (Classic, Long, Short) or set a custom Pomodoro timer.
  - Start a Pomodoro session by selecting a preset or entering your custom focus and rest time.
  - The timer will send periodic updates and allow you to cancel it at any time.

- **Task Management**:
  - Add tasks by sending a task description.
  - List all tasks and mark them as completed.
  
- **Reminder System**:
  - Set reminders in the format `reminder HH:MM` to receive notifications at the specified time.

## Database Setup

The bot uses MongoDB to store the following data:
- **Pomodoros**: User Pomodoro timer history.
- **Tasks**: User-created tasks.
- **Reminders**: User reminders.

Make sure you have MongoDB set up and the connection URI (`MONGO_URI`) configured properly in the code.

## Notes

- The connection between the MongoDB database and the bot functionality is still in progress.
- Currently, data is stored in MongoDB, but some features (like persistent task completion status) are not fully implemented yet.

## Contributing

Feel free to fork the repository and submit pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
