from flask import Flask, jsonify, request
from flask_cors import CORS
import os

from init_db import init_db, get_db_connection

app = Flask(__name__)
CORS(app)

DEFAULT_RESPONSE_BODY = {
    "errorCode": None,
    "errorMessage": None,
}

def make_response(body=None, error_code=None, error_message=None):
    response = DEFAULT_RESPONSE_BODY.copy()
    if body:
        response.update(body)
    response["errorCode"] = error_code
    response["errorMessage"] = error_message
    return jsonify(response)

"""
GET /tree — returns the prompt tree

- This includes project info and their associated prompt IDs
- The prompts IDs are unique identifiers persisted in the database and will be returned in chain order
"""
@app.route("/tree", methods=["GET"])
def get_tree():
    try:
        database_connection = get_db_connection()
        database_cursor = database_connection.cursor()
        error_code = 200
        error_message = "Success"

        # Get project info
        # As per the shared JSON file, there is only one project at the top level
        # For multiple projects, this logic would need to be adjusted as the spec changes
        project_row = database_cursor.execute("SELECT * FROM projects LIMIT 1").fetchone()
        project = dict(project_row) if project_row else None

        if project:
            # Get all prompts IDs for the project in chain order
            prompt_rows = database_cursor.execute(
                "SELECT prompt_id FROM PROMPTS WHERE project_id = ? ORDER BY prompt_id",
                (project["project_id"],)
            ).fetchall()
            prompt_ids = [row["prompt_id"] for row in prompt_rows]
            result = {
                "project": project["name"],
                "mainRequest": project["main_request"],
                "finalIntegration": project.get("final_integration"),
                "prompts": prompt_ids
            }
        else:
            result = {
                "project": None,
                "mainRequest": None,
                "finalIntegration": None,
                "prompts": []
            }
            error_code = 404
            error_message = "No project found in the database"
        database_connection.close()
        return make_response(body=result, error_code=error_code, error_message=error_message)
    except Exception as e:
        print(f"Error fetching tree data: {e}")
        return make_response(body=None, error_code=500, error_message="Internal Server Error")

"""
GET /prompts/:id — returns a single prompt with details

- This includes the prompt's title, description and parent_prompt_id
- The prompt is identified by its unique ID persisted in the database, which can be referenced from the /tree endpoint
"""
@app.route("/prompts/<int:prompt_id>", methods=["GET"])
def get_prompt(prompt_id):
    try:
        database_connection = get_db_connection()
        database_cursor = database_connection.cursor()
        error_code = 200
        error_message = "Success"

        prompt_row = database_cursor.execute(
            "SELECT * FROM PROMPTS WHERE prompt_id = ?",
            (prompt_id,)
        ).fetchone()

        if prompt_row:
            prompt = dict(prompt_row)
            result = {
                "title": prompt["title"],
                "description": prompt["description"],
                "parentPromptId": prompt["parent_prompt_id"],
                "projectId": prompt["project_id"]
            }
        else:
            result = None
            error_code = 404
            error_message = "Prompt not found"
        database_connection.close()
        return make_response(body=result, error_code=error_code, error_message=error_message)
    except Exception as e:
        print(f"Error fetching prompt data: {e}")
        return make_response(body=None, error_code=500, error_message="Internal Server Error")

"""
GET /prompts/:id/nodes - returns the nodes for a prompt

- This includes a list of nodes associated with a particular prompt identified by its unique ID
- The nodes contain details such as name and action
"""
@app.route("/prompts/<int:prompt_id>/nodes", methods=["GET"])
def get_prompt_nodes(prompt_id):
    try:
        database_connection = get_db_connection()
        database_cursor = database_connection.cursor()
        error_code = 200
        error_message = "Success"

        prompt_row = database_cursor.execute(
            "SELECT * FROM PROMPTS WHERE prompt_id = ?",
            (prompt_id,)
        ).fetchone()

        if prompt_row:
            node_rows = database_cursor.execute(
                "SELECT * FROM NODES WHERE prompt_id = ? ORDER BY node_id",
                (prompt_id,)
            ).fetchall()
            nodes = []
            for row in node_rows:
                node = {
                    "nodeId": row["node_id"],
                    "name": row["name"],
                    "action": row["action"],
                }
                nodes.append(node)
            result = {
                "nodes": nodes
            }
        else:
            result = None
            error_code = 404
            error_message = "Prompt not found"
        
        database_connection.close()
        return make_response(body=result, error_code=error_code, error_message=error_message)
    except Exception as e:
        print(f"Error fetching prompt nodes: {e}")
        return make_response(body=None, error_code=500, error_message="Internal Server Error")

"""
POST /prompts/:id — add a prompt

- This allows adding a new prompt under a specified parent prompt identified by its unique ID
- The request body should contain the title and description for the new prompt
- If successful, the response will include the unique ID of the newly created prompt
- If the parent prompt ID already has a child prompt, the request will be rejected to maintain the chain structure
"""
@app.route("/prompts/<int:prompt_id>", methods=["POST"])
def add_prompt(prompt_id):
    try:
        data = request.json
        if not data or "title" not in data or not data["title"].strip() or "description" not in data or not data["description"].strip():
            return make_response(body=None, error_code=400, error_message="Title and description are required")
        
        database_connection = get_db_connection()
        database_cursor = database_connection.cursor()
        error_code = 200
        error_message = "Prompt added successfully"

        parent_id = prompt_id if prompt_id > 0 else None
        project_id = None
        if parent_id is not None:
            parent_row = database_cursor.execute(
                "SELECT prompt_id, project_id FROM PROMPTS WHERE prompt_id = ?",
                (parent_id,)
            ).fetchone()
            if not parent_row:
                database_connection.close()
                return make_response(body=None, error_code=404, error_message="Parent prompt not found")
            project_id = parent_row["project_id"]
        else:
            return make_response(body=None, error_code=400, error_message="Parent prompt ID must be greater than 0")
        
        # Check if parent prompt already has a child prompt
        child_row = database_cursor.execute(
            "SELECT prompt_id FROM PROMPTS WHERE parent_prompt_id = ?",
            (parent_id,)
        ).fetchone()
        if child_row:
            result = None
            error_message = "Parent prompt already has a child prompt"
            error_code = 400
        else:
            # Insert new prompt
            database_cursor.execute(
                "INSERT INTO PROMPTS (title, description, parent_prompt_id, project_id) VALUES (?, ?, ?, ?)",
                (data["title"], data["description"], parent_id, project_id)
            )
            new_prompt_row_id = database_cursor.lastrowid
            new_prompt_id = database_cursor.execute(
                "SELECT prompt_id FROM PROMPTS WHERE rowid = ?",
                (new_prompt_row_id,)
            ).fetchone()["prompt_id"]
            result = {
                "id": new_prompt_id
            }
        database_connection.commit()
        database_connection.close()
        return make_response(body=result, error_code=error_code, error_message=error_message)
    except Exception as e:
        print(f"Error adding prompt: {e}")
        return make_response(body=None, error_code=500, error_message="Internal Server Error")

"""
POST /prompts/:id/nodes — add a node for a prompt

- This allows adding a new node associated with a particular prompt identified by its unique ID
- The request body should contain the name and action for the new node
- If successful, the response will include the unique ID of the newly created node
- If the prompt ID does not exist, the request will be rejected
- The new node will be linked to the last available node in the prompt's node list, as the ID of the newly created node is auto-incremented
"""
@app.route("/prompts/<int:prompt_id>/nodes", methods=["POST"])
def add_prompt_node(prompt_id):
    try:
        data = request.json
        if not data or "name" not in data or not data["name"].strip() or "action" not in data or not data["action"].strip():
            return make_response(body=None, error_code=400, error_message="Name and action are required")
        database_connection = get_db_connection()
        database_cursor = database_connection.cursor()
        error_code = 200
        error_message = "Node added successfully"
        prompt_row = database_cursor.execute(
            "SELECT * FROM PROMPTS WHERE prompt_id = ?",
            (prompt_id,)
        ).fetchone()
        if not prompt_row:
            error_code = 404
            error_message = "Prompt not found"
            result = None
        else:
            # Insert new node
            database_cursor.execute(
                "INSERT INTO NODES (prompt_id, name, action) VALUES (?, ?, ?)",
                (prompt_id, data["name"], data["action"])
            )
            new_node = database_cursor.execute(
                "SELECT node_id FROM NODES WHERE prompt_id = ? AND name = ? ORDER BY rowid DESC LIMIT 1",
                (prompt_id, data["name"])
            ).fetchone()
            new_node_id = new_node["node_id"]
            result = {
                "id": new_node_id
            }
        database_connection.commit()
        database_connection.close()
        return make_response(body=result, error_code=error_code, error_message=error_message)
    except Exception as e:
        print(f"Error adding prompt node: {e}")
        return make_response(body=None, error_code=500, error_message="Internal Server Error")

"""
GET /prompts/:id/notes — get notes for a prompt

- This retrieves all notes associated with a particular prompt identified by its unique ID
- The notes are returned in reverse chronological order based on their creation timestamp
"""
@app.route("/prompts/<int:prompt_id>/notes", methods=["GET"])
def get_prompt_notes(prompt_id):
    try:
        database_connection = get_db_connection()
        database_cursor = database_connection.cursor()
        error_code = 200
        error_message = "Success"

        prompt_row = database_cursor.execute(
            "SELECT * FROM PROMPTS WHERE prompt_id = ?",
            (prompt_id,)
        ).fetchone()

        if prompt_row:
            note_rows = database_cursor.execute(
                "SELECT * FROM NOTES WHERE prompt_id = ? ORDER BY created_at DESC",
                (prompt_id,)
            ).fetchall()
            notes = []
            for row in note_rows:
                note = {
                    "noteId": row["note_id"],
                    "content": row["content"],
                    "createdAt": row["created_at"],
                }
                notes.append(note)
            result = {
                "notes": notes
            }
        else:
            result = None
            error_code = 404
            error_message = "Prompt not found"
        
        database_connection.close()
        return make_response(body=result, error_code=error_code, error_message=error_message)
    except Exception as e:
        print(f"Error fetching prompt notes: {e}")
        return make_response(body=None, error_code=500, error_message="Internal Server Error")

"""
POST /prompts/:id/notes — add a note for a prompt

- This allows adding a new note associated with a particular prompt identified by its unique ID
- The request body should contain the content of the note
- If successful, the response will include the unique ID of the newly created note
- The note will be timestamped with the current date and time upon creation
- If the prompt ID does not exist, the request will be rejected
"""
@app.route("/prompts/<int:prompt_id>/notes", methods=["POST"])
def add_prompt_note(prompt_id):
    try:
        data = request.json
        if not data or "content" not in data or not data["content"].strip():
            return make_response(body=None, error_code=400, error_message="Content is required")

        database_connection = get_db_connection()
        database_cursor = database_connection.cursor()
        error_code = 200
        error_message = "Note added successfully"

        prompt_row = database_cursor.execute(
            "SELECT * FROM PROMPTS WHERE prompt_id = ?",
            (prompt_id,)
        ).fetchone()

        if not prompt_row:
            error_code = 404
            error_message = "Prompt not found"
            result = None
        else:
            # Insert new note
            database_cursor.execute(
                "INSERT INTO NOTES (prompt_id, content) VALUES (?, ?)",
                (prompt_id, data["content"])
            )
            new_note = database_cursor.execute(
                "SELECT note_id FROM NOTES WHERE prompt_id = ? AND content = ? ORDER BY rowid DESC LIMIT 1",
                (prompt_id, data["content"])
            ).fetchone()
            new_note_id = new_note["note_id"]
            result = {
                "id": new_note_id
            }
        database_connection.commit()
        database_connection.close()
        return make_response(body=result, error_code=error_code, error_message=error_message)
    except Exception as e:
        print(f"Error adding prompt note: {e}")
        return make_response(body=None, error_code=500, error_message="Internal Server Error")

if __name__ == "__main__":
    # This will create the database file and tables if they don't exist
    # It will also seed the database from the provided JSON file
    init_db()
    port = int(os.environ.get("PORT", "5001"))
    app.run(debug=True, host="127.0.0.1", port=port)