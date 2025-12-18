from flask import Flask, jsonify
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
                'project': project['name'],
                'mainRequest': project['main_request'],
                'finalIntegration': project.get('final_integration'),
                'prompts': prompt_ids
            }
        else:
            result = {
                'project': None,
                'mainRequest': None,
                'finalIntegration': None,
                'prompts': []
            }
            error_code = 601
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
    print(f"Fetching prompt with ID: {prompt_id}")
    pass

"""
GET /prompts/:id/nodes - returns the nodes for a prompt

- This includes a list of nodes associated with a particular prompt identified by its unique ID
- The nodes contain details such as name and action
"""
@app.route("/prompts/<int:prompt_id>/nodes", methods=["GET"])
def get_prompt_nodes(prompt_id):
    print(f"Fetching nodes for prompt ID: {prompt_id}")
    pass

"""
POST /prompts/:id — add a prompt

- This allows adding a new prompt under a specified parent prompt identified by its unique ID
- The request body should contain the title and description for the new prompt
- If successful, the response will include the unique ID of the newly created prompt
- If the parent prompt ID already has a child prompt, the request will be rejected to maintain the chain structure
"""
@app.route("/prompts/<int:prompt_id>", methods=["POST"])
def add_prompt(prompt_id):
    print(f"Adding prompt under parent prompt ID: {prompt_id}")
    pass

"""
POST /prompts/:id/nodes — add a node for a prompt

- This allows adding a new node associated with a particular prompt identified by its unique ID
- The request body should contain the name and action for the new node
- If successful, the response will include the unique ID of the newly created node
- If the prompt ID does not exist, the request will be rejected
- The new node will be linked to the last available node in the prompt's node list
"""
@app.route("/prompts/<int:prompt_id>/nodes", methods=["POST"])
def add_prompt_node(prompt_id):
    print(f"Adding node for parent prompt ID: {prompt_id}")
    pass

"""
GET /prompts/:id/notes — get notes for a prompt

- This retrieves all notes associated with a particular prompt identified by its unique ID
- The notes are returned in reverse chronological order based on their creation timestamp
"""
@app.route("/prompts/<int:prompt_id>/notes", methods=["GET"])
def get_prompt_notes(prompt_id):
    print(f"Fetching notes for prompt ID: {prompt_id}")
    pass

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
    print(f"Adding note for prompt ID: {prompt_id}")
    pass


if __name__ == "__main__":
    # This will create the database file and tables if they don't exist
    # It will also seed the database from the provided JSON file
    init_db()
    port = int(os.environ.get("PORT", "5001"))
    app.run(debug=True, host="127.0.0.1", port=port)