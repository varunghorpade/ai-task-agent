import json
import os
import subprocess
from datetime import datetime
from typing import List, Dict
import openai
from dotenv import load_dotenv

load_dotenv()

class TaskAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.tasks_file = 'tasks.json'
        self.load_tasks()

    def load_tasks(self):
        try:
            with open(self.tasks_file, 'r') as f:
                self.tasks = json.load(f)
        except FileNotFoundError:
            self.tasks = []

    def save_tasks(self):
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, description: str):
        task = {
            'id': len(self.tasks) + 1,
            'description': description,
            'completed': False,
            'created': datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.save_tasks()
        return f"Task added: {description}"

    def list_tasks(self):
        if not self.tasks:
            return "No tasks found."

        result = "Your tasks:\n"
        for task in self.tasks:
            status = "✓" if task['completed'] else "○"
            result += f"{status} {task['id']}: {task['description']}\n"
        return result

    def complete_task(self, task_id: int):
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                self.save_tasks()
                return f"Task {task_id} completed!"
        return f"Task {task_id} not found."

    def chat_with_ai(self, message: str):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI Error: {e}"

    def process_command(self, user_input: str):
        user_input = user_input.strip().lower()

        if user_input.startswith('add task'):
            task_desc = user_input[8:].strip()
            return self.add_task(task_desc)

        elif user_input == 'list tasks':
            return self.list_tasks()

        elif user_input.startswith('complete'):
            try:
                task_id = int(user_input.split()[1])
                return self.complete_task(task_id)
            except (IndexError, ValueError):
                return "Usage: complete <task_id>"

        elif user_input.startswith('ask'):
            question = user_input[3:].strip()
            return self.chat_with_ai(question)

        elif user_input in ['help', 'commands']:
            return """Available commands:
- add task <description>: Add a new task
- list tasks: Show all tasks
- complete <id>: Mark task as completed
- ask <question>: Chat with AI
- help: Show this help
- quit: Exit"""

        else:
            return "Unknown command. Type 'help' for available commands."
