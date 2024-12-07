import sqlite3
from datetime import datetime, timedelta


class Task:
    def __init__(self, title, category, priority, due_date):
        self.title = title
        self.category = category
        self.priority = priority
        self.due_date = due_date


class TaskManager:
    def __init__(self, db_name="task_manager.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_task_table()

    def create_task_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT,
                category TEXT,
                priority TEXT,
                due_date TEXT,
                completed INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def add_task(self, task):
        self.cursor.execute("""
            INSERT INTO tasks (title, category, priority, due_date) 
            VALUES (?, ?, ?, ?)
        """, (task.title, task.category, task.priority, task.due_date))
        self.conn.commit()
        print("Task added successfully!")

    def view_tasks(self, filter_by=None):
        query = "SELECT id, title, category, priority, due_date, completed FROM tasks"
        if filter_by:
            query += f" WHERE category = '{filter_by}'"
        self.cursor.execute(query)
        tasks = self.cursor.fetchall()
        print("\nYour Tasks:")
        for task in tasks:
            status = "Completed" if task[5] else "Pending"
            print(f"[{task[0]}] {task[1]} | {task[2]} | {task[3]} | Due: {task[4]} | {status}")

    def mark_task_complete(self, task_id):
        self.cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        self.conn.commit()
        print("Task marked as completed!")

    def analyze_overdue_tasks(self):
        self.cursor.execute("SELECT title, due_date FROM tasks WHERE completed = 0")
        tasks = self.cursor.fetchall()
        print("\nOverdue Tasks:")
        for title, due_date in tasks:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            if due_date_obj < datetime.now():
                print(f"{title} | Due: {due_date} (OVERDUE)")

    def close(self):
        self.conn.close()


class UserManager:
    def __init__(self, db_name="users.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_user_table()

    def create_user_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)
        self.conn.commit()

    def register_user(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            print("Registration successful!")
        except sqlite3.IntegrityError:
            print("Username already exists. Try again.")

    def login_user(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = self.cursor.fetchone()
        if user:
            print("Login successful!")
            return username
        print("Invalid credentials.")
        return None

    def close(self):
        self.conn.close()


def main():
    print("Welcome to the Smart Task Manager!")
    user_manager = UserManager()
    task_manager = TaskManager()

    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            user_manager.register_user()
        elif choice == "2":
            user = user_manager.login_user()
            if user:
                while True:
                    print("\nTask Menu:")
                    print("1. Add Task")
                    print("2. View Tasks")
                    print("3. Mark Task as Complete")
                    print("4. Analyze Overdue Tasks")
                    print("5. Logout")
                    task_choice = input("Choose an option: ").strip()

                    if task_choice == "1":
                        title = input("Enter task title: ")
                        category = input("Enter task category: ")
                        priority = input("Enter priority (High, Medium, Low): ")
                        due_date = input("Enter due date (YYYY-MM-DD): ")
                        task = Task(title, category, priority, due_date)
                        task_manager.add_task(task)
                    elif task_choice == "2":
                        task_manager.view_tasks()
                    elif task_choice == "3":
                        task_id = int(input("Enter task ID to mark as complete: "))
                        task_manager.mark_task_complete(task_id)
                    elif task_choice == "4":
                        task_manager.analyze_overdue_tasks()
                    elif task_choice == "5":
                        print("Logged out successfully!")
                        break
                    else:
                        print("Invalid option. Try again.")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

    user_manager.close()
    task_manager.close()


if __name__ == "__main__":
    main()
