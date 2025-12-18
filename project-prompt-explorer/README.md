# Prompt Tree Explorer

A full-stack web application for exploring and annotating prompt trees, built with Flask (Python) backend and React frontend.

## Features

- **Tree Visualization**: Expandable/collapsible tree view of prompts and their nodes
- **Prompt Details**: Click any prompt to view detailed information in a side panel
- **Notes System**: Add and view notes for any prompt
- **RESTful API**: Complete backend API for managing prompts, nodes, and notes

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: ReactJS
- **Database**: SQLite (local storage)

## Project Structure

```
project-prompt-explorer/
├── backend/
│   ├── api_collection/     # Has API testing collections I used to test the endpoints locally
│   |    ├── bruno-collection.json  
│   |    ├── postman-collection.json
│   ├── app.py              # Flask application
│   ├── init_db.py          # Database initialization script
│   ├── requirements.txt    # Python dependencies
│   └── projects.db         # SQLite database (created on first run)
│   └── prompt_list.json    # Initially shared JSON (used for seeding the database)
└── frontend/
```

## Notes & Asssumption

- The database is initialized with data from `prompt_list.json` in the root directory
- All data persists in the SQLite database file (`prompts.db`)
- CORS is enabled for development (allows frontend to communicate with backend)
- A project can have multiple prompts and every prompt can have multiple nodes and notes
- The prompts for a particular project are always in a chain (meaning a reverse linked list as parent prompt ID is persisted)
- The nodes of a particular prompt are persisted in order (meaning a list as node ID is used to order)
- The notes are persisted as 1:n collection between prompt:note and creation time is used to order. 