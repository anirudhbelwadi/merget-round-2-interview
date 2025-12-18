## Backend Server
### Persistence Layer
- Technology chosen: SQLite
- Command to initialize and seed the Database:
```bash
python3 init_db.py # On Windows: py init_db.py
```

#### ER Diagram
<img src="./documentation_assets/erd.png">

Find the UML <a href="#uml-for-er-diagram">here</a>

#### DDL queries

Table: PROJECTS
```
 CREATE TABLE IF NOT EXISTS PROJECTS (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    main_request TEXT,
    final_integration TEXT
 )
```

Table: PROMPTS
```
CREATE TABLE IF NOT EXISTS PROMPTS (
    prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    parent_prompt_id INTEGER,
    project_id INTEGER,
    FOREIGN KEY (parent_prompt_id) REFERENCES PROMPTS(prompt_id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES PROJECTS(project_id) ON DELETE CASCADE
)
```

Table: NODES
```
CREATE TABLE IF NOT EXISTS NODES (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    action TEXT,
    FOREIGN KEY (prompt_id) REFERENCES PROMPTS(prompt_id) ON DELETE CASCADE
)
```

Table: NOTES
```
CREATE TABLE IF NOT EXISTS NOTES (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES PROMPTS(prompt_id) ON DELETE CASCADE
)
```

### Backend Server
#### Create and activate a virtual environment
```bash
python3 -m venv venv # On Windows: py -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
#### Install all the dependencies
```bash
pip install -r requirements.txt
```

#### Start the Flask Server
```bash
python app.py
```
The backend will run on `http://localhost:5001`

#### API Endpoints

##### Endpoints in given specs
- `GET /tree` - returns the prompt tree
- `GET /prompts/:id` - returns a single prompt with details
- `GET /prompts/:id/nodes` - returns the nodes for a prompt
- `POST /prompts/:id` - add a prompt
- `POST /prompts/:id/nodes` - add a node for a prompt

#### Extra Endpoints added by me
- `GET /prompts/:id/notes` - Get all notes for a prompt
- `POST /prompts/:id/notes` - Add a note to a prompt

### Appendix
#### UML for ER Diagram
```
@startuml
hide circle
skinparam linetype ortho

entity PROJECTS {
  + project_id : INTEGER <<PK>>
  --
  name : TEXT
  main_request : TEXT
  final_integration : TEXT
}

entity PROMPTS {
  + prompt_id : INTEGER <<PK>>
  --
  title : TEXT
  description : TEXT
  parent_prompt_id : INTEGER <<FK>>  
  project_id : INTEGER <<FK>>
}

entity NODES {
  + node_id : INTEGER <<PK>>
  --
  name : TEXT
  action : TEXT
  prompt_id : INTEGER <<FK>>
}

entity NOTES {
  + note_id : INTEGER <<PK>>
  --
  content : TEXT
  created_at : TIMESTAMP
  prompt_id : INTEGER <<FK>>
}

PROJECTS "(1,1)  " -- "(0,n)  " PROMPTS : " has"
PROMPTS  "  (1,1)" -- "(0,n)  " NODES   : " contains"
PROMPTS  "(1,1)  " -- "(0,n)" NOTES   : " takes"
PROMPTS  "(0,1)   " -- "  (0,1)" PROMPTS : parent_of

@enduml
```