from pymongo import MongoClient
from datetime import datetime

# MongoDB connection URI (replace with your MongoDB URI)
MONGO_URI = "mongodb://localhost:27017/"  # Change to your MongoDB connection string

# Initialize MongoDB client
client = MongoClient(MONGO_URI)

# Select the database (e.g., 'productivity_bot')
db = client.productivity_bot

# Define collections for Pomodoros, Tasks, and Reminders
pomodoro_collection = db.pomodoros
task_collection = db.tasks
reminder_collection = db.reminders

# Function to save custom Pomodoro to MongoDB
def save_custom_pomodoro_to_db(user_id, focus_time, rest_time):
    pomodoro_data = {
        "user_id": user_id,
        "focus_time": focus_time,
        "rest_time": rest_time,
        "created_at": datetime.now()
    }
    # Insert the data into the 'pomodoros' collection
    pomodoro_collection.insert_one(pomodoro_data)

# Function to retrieve the most recent custom Pomodoro for a user
def get_custom_pomodoro_from_db(user_id):
    return pomodoro_collection.find_one({"user_id": user_id}, sort=[("created_at", -1)])

# Function to save task to MongoDB
def save_task_to_db(user_id, description, due_date=None):
    task_data = {
        "user_id": user_id,
        "description": description,
        "due_date": due_date,
        "completed": False,
        "created_at": datetime.now()
    }
    task_collection.insert_one(task_data)

# Function to retrieve tasks for a user
def get_tasks_from_db(user_id):
    return list(task_collection.find({"user_id": user_id}))

# Function to save reminder to MongoDB
def save_reminder_to_db(user_id, description, reminder_time):
    reminder_data = {
        "user_id": user_id,
        "description": description,
        "reminder_time": reminder_time,
        "created_at": datetime.now()
    }
    reminder_collection.insert_one(reminder_data)

# Function to retrieve reminders for a user
def get_reminders_from_db(user_id):
    return list(reminder_collection.find({"user_id": user_id}))
