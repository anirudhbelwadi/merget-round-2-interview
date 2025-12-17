## The task:

- Build a web app with a backend API that lets users explore and annotate a prompt tree.

### Backend API:

- `GET /tree` — returns the prompt tree
- `GET /prompts/:id` — returns a single prompt with details
- `GET /prompts/:id/nodes` - returns the nodes for a prompt 
- `POST /prompts/:id` — add a prompt
- `POST /prompts/:id/nodes` — add a node for a prompt

### Frontend:
- Visualize the tree (expand/collapse)
- Click a node to see details in a side panel
- Add and view notes on any prompt

### Data persistence:
- In-memory or SQLite — your choice

### Notes
You will be provided a [JSON](./prompt_list.json) with a list of prompt and subprompts, and you are also provided an image of what the UI could look like (incredibly coarse/rough, it's there to simply provide inspiration). You may also create more or less API calls, it's your choice. The language, libraries etc. you use is also your choice.

<img src="./ui_expectation.png">