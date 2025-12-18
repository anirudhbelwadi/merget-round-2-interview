import sqlite3
import json
import os

DATABASE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'projects.db'))
PROMPT_FILE = 'prompt_list.json'

"""
Initialize database referenced in DATABASE and load data from JSON file referenced in PROMPT_FILE and seed it into the database
"""
def init_db():
    try:
        database_connection = get_db()
        database_cursor = database_connection.cursor()

        # Drop tables to update schema in a clean database
        database_cursor.execute("DROP TABLE IF EXISTS NOTES")
        database_cursor.execute("DROP TABLE IF EXISTS NODES")
        database_cursor.execute("DROP TABLE IF EXISTS PROMPTS")
        database_cursor.execute("DROP TABLE IF EXISTS PROJECTS")

        # Create tables
        database_cursor.execute('''
            CREATE TABLE IF NOT EXISTS PROJECTS (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                main_request TEXT,
                final_integration TEXT
            )
        ''')
    
        database_cursor.execute('''
            CREATE TABLE IF NOT EXISTS PROMPTS (
                prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                parent_prompt_id INTEGER,
                project_id INTEGER,
                FOREIGN KEY (parent_prompt_id) REFERENCES PROMPTS(prompt_id) ON DELETE SET NULL,
                FOREIGN KEY (project_id) REFERENCES PROJECTS(project_id) ON DELETE CASCADE
            )
        ''')
    
        database_cursor.execute('''
            CREATE TABLE IF NOT EXISTS NODES (
                node_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                action TEXT,
                FOREIGN KEY (prompt_id) REFERENCES PROMPTS(prompt_id) ON DELETE CASCADE
            )
        ''')
    
        database_cursor.execute('''
            CREATE TABLE IF NOT EXISTS NOTES (
                note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prompt_id) REFERENCES PROMPTS(prompt_id) ON DELETE CASCADE
            )
        ''')
    
        # Load JSON data
        json_path = os.path.join(os.path.dirname(__file__), PROMPT_FILE)
        json_path = os.path.abspath(json_path)

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Could not find prompt_list.json. Path provided: {json_path}")
    
        with open(json_path, "r") as f:
            json_data = json.load(f)
    
        # Insert project
        # As per the shared JSON file, there is only one project at the top level
        # For multiple projects, this logic would need to be adjusted as per the JSON structure
        database_cursor.execute(
            "INSERT INTO PROJECTS (name, main_request, final_integration) VALUES (?, ?, ?)",
            (json_data.get("project"), json_data.get("mainRequest"), json_data.get("finalIntegration"))
        )

        # Get the inserted project ID from the last inserted row
        # This is not the most efficient way, and I would use UUID for IDs in a production system
        # This pattern is used here for simplicity and also has been replicated in other parts of the codebase
        project_row_id = database_cursor.lastrowid
        project_id = database_cursor.execute(
            "SELECT project_id FROM PROJECTS WHERE rowid = ?",
            (project_row_id,)
        ).fetchone()[0]

        # Insert prompts and nodes
        last_prompt_id = None
        for prompt_data in json_data["prompts"]:
            # The id provided for each prompt in the JSON file is not used for the database, as it might not be unique always
            # I have used an auto-incrementing primary key for the prompt_id in the database.
            database_cursor.execute(
                "INSERT INTO PROMPTS (title, description, parent_prompt_id, project_id) VALUES (?, ?, ?, ?)",
                (prompt_data.get("title"), prompt_data.get("description"), last_prompt_id, project_id)
            )

            db_prompt_row_id = database_cursor.lastrowid
            db_prompt_id = database_cursor.execute(
                "SELECT prompt_id FROM PROMPTS WHERE rowid = ?",
                (db_prompt_row_id,)
            ).fetchone()[0]
        
            # Insert subprompts (nodes)
            for subprompt in prompt_data.get("subprompts", []):
                database_cursor.execute(
                    "INSERT INTO NODES (prompt_id, name, action) VALUES (?, ?, ?)",
                    (db_prompt_id, subprompt.get("name"), subprompt.get("action"))
                )

            # Next prompt becomes a child of the current prompt (simple chain as the subprompts is provided as a simple list).
            last_prompt_id = db_prompt_id

        database_connection.commit()
        database_connection.close()

        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

"""
Get a database connection for the SQLite database referenced in DATABASE
"""
def get_db_connection():
    try:
        database_connection = sqlite3.connect(DATABASE)
        # This helps to return rows as dictionaries instead of tuples
        database_connection.row_factory = sqlite3.Row
        # Enable foreign key support, which is disabled by default in SQLite
        database_connection.execute('PRAGMA foreign_keys = ON')
        return database_connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

if __name__ == "__main__":
    init_db()