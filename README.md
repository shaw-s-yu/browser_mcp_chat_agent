# Browser Automation and VNC Project

This project provides a web-based interface for browser automation, featuring a split-screen layout with a terminal on the left and a VNC session on the right. The system is containerized using Docker, making it easy to set up and run.

## Prerequisites

- Docker
- Docker Compose
- A Google Gemini API Key

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a `.env` file:**
    Create a file named `.env` in the `src` directory of the project and add your Google Gemini API key:
    ```
    GEMINI_API_KEY=your_gemini_api_key
    ```

## Running the Application

1.  **Build and run the Docker container:**

    ```bash
    docker-compose up -d --build
    ```

2.  **Access the web interface:**
    Open your web browser and navigate to `http://localhost:5000`.

## Functionality

- **Web Terminal:** The left pane of the interface is a fully functional web terminal.
- **VNC Screen:** The right pane displays a live VNC session of the browser running within the Docker container.
- **Automated Agent:** The system automatically starts a browser automation agent that can perform tasks based on user input.

## Adding New Actions

To add new automated actions, you need to create SQL queries, prompt templates, and register them in the action mapper.

### Step 1: Create a New SQL Query

1. Navigate to `src/db/query/`
2. Create a new SQL file, e.g., `my_new_query.sql`
3. Write your SQL query that will be executed to fetch data needed for your action

### Step 2: Create a New Prompt Template

1. Navigate to `src/prompts/`
2. Create a new Markdown file, e.g., `my_new_action.md`
3. The file should follow this structure:
   ```markdown
   ## Description
   [Brief description of what this action does]

   ## Instruction
   RUN_MY_NEW_ACTION or `the actual steps`

   ## Template
   [Step-by-step instructions for the AI agent]
   [Include variables from CSV data like <column_name>]
   [These will be replaced with actual data from the SQL query results]
   ```

**Important:** If your action requires using both SQL data and a template:
- Put the action name (e.g., `RUN_MY_NEW_ACTION`) in the **Instruction** section
- Add a **Template** section with step-by-step instructions that reference CSV columns as `<column_name>`
- When the action is triggered, the system will:
  1. Execute the SQL query to get data (saved as CSV)
  2. Use the Template section to generate instructions with actual data substituted

**Example:** See [src/prompts/submit_task.md](src/prompts/submit_task.md) for a complete example showing how to use actions with templates and SQL data together.

### Step 3: Register in action_mapper.json

1. Open `src/action_mapper.json`
2. Add a new entry with the action name:
   ```json
   {
       "RUN_MY_NEW_ACTION": {
           "prompt_file": "my_new_action.md",
           "sql": "my_new_query.sql"
       }
   }
   ```
3. The action name must follow the format: `RUN_<action_name>_ACTION`

### Step 4: How It Works

When the AI responds with `RUN_MY_NEW_ACTION`:
1. The system looks up the action in `action_mapper.json`
2. Executes the SQL query from `src/db/query/my_new_query.sql`
3. Generates a prompt using the template in `src/prompts/my_new_action.md`
4. Returns the generated prompt to be used by the browser agent

## Project Structure

```
.
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── README.md
└── src
    ├── .env
    ├── app.py
    ├── browser_agent.py
    ├── chat_agent.py
    ├── prompt_loader.py
    ├── prompts
    │   ├── go_to_task_page.md
    │   ├── login.md
    │   └── open_home_page.md
    ├── requirements.txt
    ├── run_agent.sh
    └── templates
        └── terminal.html
```
