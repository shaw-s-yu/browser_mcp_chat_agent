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
