# Browser Automation and VNC Project

This project provides a web-based interface for browser automation, featuring a split-screen layout with a terminal on the left and a VNC session on the right. The system is containerized using Docker, making it easy to set up and run.

## Prerequisites

- Docker
- Docker Compose
- A Google Gemini API Key
- Access to a remote Oracle database server (IP, port, credentials)

## Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### Step 2: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and update with your actual credentials:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   
   # Oracle Database Configuration
   ORACLE_HOST=your_oracle_server_ip      # e.g., 192.168.1.100
   ORACLE_PORT=1521                       # Oracle port (usually 1521)
   ORACLE_SERVICE=your_service_name       # e.g., ORCL
   ORACLE_USER=your_username              # e.g., system
   ORACLE_PASSWORD=your_password          # Your password
   ```

   **Important:** Make sure you can reach the Oracle server from your Docker environment.

### Step 3: Build and Run the Docker Container

1.  **Build and start the Docker container:**

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

## Oracle Database Configuration

### Docker Environment

The Docker container is configured with Oracle Instant Client to connect to remote Oracle servers. This eliminates the need to install the full Oracle client locally.

#### Architecture
- **Host Machine:** No Oracle client needed
- **Docker Container (Ubuntu):** 
  - Oracle Instant Client 21.4 pre-installed
  - Python cx_Oracle library configured
  - Environment variables properly set

#### How It Works

1. **Dockerfile** installs:
   - `libaio1` - Oracle Instant Client dependency
   - Oracle Instant Client 21.4 libraries
   - Sets `LD_LIBRARY_PATH` and `ORACLE_HOME` environment variables

2. **entrypoint.sh** ensures:
   - Oracle environment variables are exported
   - Connection can be established to remote Oracle server

3. **docker-compose.yml** passes:
   - Oracle connection credentials via environment variables
   - Oracle home and library paths to the container

#### Testing Oracle Connection

To verify Oracle connectivity from inside the container:

```bash
# Enter the container
docker exec -it ubuntu-novnc bash

# Test Oracle connection
cd /home/user/app
python -c "from db.oracle_sql import OracleSQL; oracle = OracleSQL(); oracle.connect(); print('✓ Connection successful'); oracle.disconnect()"
```

#### Troubleshooting

**Error: "Cannot locate a 32-bit Oracle Client library"**
- The Docker image uses 64-bit Instant Client (correct)
- Ensure ORACLE_HOST is reachable from Docker container
- Test: `docker exec -it ubuntu-novnc ping your_oracle_server_ip`

**Error: "Cannot create connection"**
1. Verify Oracle credentials in `.env` file
2. Ensure Oracle server is listening on the configured port
3. Check firewall rules allow Docker container to reach Oracle server
4. Verify the service name (ORACLE_SERVICE) is correct

**Connection timeout**
- Ensure ORACLE_HOST is reachable: `docker exec -it ubuntu-novnc telnet your_oracle_server_ip 1521`
- Check Oracle server is running
- Verify network configuration and firewall rules

### Local Development (without Docker)

To run locally on Windows/Linux:

1. Install Oracle Instant Client from [Oracle website](https://www.oracle.com/database/technologies/instant-client.html)
2. Add the client to your PATH
3. Create a Python virtual environment: `python -m venv venv`
4. Activate it and install requirements: `pip install -r src/requirements.txt`
5. Configure `.env` with your Oracle credentials
6. Run: `python src/app.py`

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
