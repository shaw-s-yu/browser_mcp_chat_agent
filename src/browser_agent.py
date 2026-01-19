import os
import time
from dotenv import load_dotenv
from haystack.components.agents import Agent
from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack_integrations.tools.mcp import MCPToolset, StdioServerInfo

# Load environment variables from .env file at the very start of the script
load_dotenv()

class BrowserAgent:
    """
    An agent that can interact with a web browser.
    It requires PromptLoader and VideoRecorder instances to be injected.
    """
    def __init__(self):
        """
        Initializes the BrowserAgent.

        Args:
            prompt_loader (PromptLoader): An instance of the prompt loader.
            video_recorder (VideoRecorder): An instance of the video recorder.
        """
        # The API key is now expected to be in the environment, loaded from .env
        if "GEMINI_API_KEY" not in os.environ or not os.environ["GEMINI_API_KEY"]:
            raise ValueError("GEMINI_API_KEY not found. Please create a .env file and add your key.")

        # We use /usr/bin/env to set the DISPLAY variable and run npx directly.
        # This is more stable than using 'bash -c' and avoids shell-related process issues.
        
        command = 'DISPLAY=:1 npx @playwright/mcp@latest --no-sandbox --viewport-size="1280,800"'
        # 1. Initialize the MCP server and toolset for browser control
        server_info = StdioServerInfo(command="bash", args=["-c", command])
        toolset = MCPToolset(
            server_info=server_info,
            tool_names=["browser_navigate", "browser_snapshot", "browser_click", "browser_type", "browser_navigate_back", "browser_wait_for"]
        )

        # 2. Initialize the Chat Generator (LLM)
        chat_generator = GoogleGenAIChatGenerator(model="gemini-2.5-pro")

        # 3. Define the system prompt for the agent
        system_message = """
        You are an intelligent assistant equipped with tools for navigating the web.
        You can use tools when appropriate, but not every task requires them.
        If a request seems challenging, think creatively and attempt a solution.
        You are more capable than you might assume. Trust your abilities.
        """

        # 4. Create the Haystack Agent
        self.agent = Agent(
            chat_generator=chat_generator,
            tools=toolset,
            system_prompt=system_message,
            exit_conditions=["text"],
        )

    def run_single_prompt(self, prompt: str) -> str:
        """
        Processes a single prompt and returns the agent's final text response.
        """
        print(f"Running prompt: {prompt}")
        result = self.agent.run(messages=[ChatMessage.from_user(prompt)])
        response_text = result['last_message'].text
        print(response_text)
        return response_text

    def run_single_prompt_no_v(self, prompt: str) -> str:
        """
        Processes a single prompt and returns the agent's final text response.
        """
        result = self.agent.run(messages=[ChatMessage.from_user(prompt)])
        response_text = result['last_message'].text
        return response_text

if __name__ == '__main__':
    # This block demonstrates how to use the refactored BrowserAgent class.
    # It requires a .env file with your GEMINI_API_KEY.
    try:
        
        # Inject dependencies into the agent
        browser_agent = BrowserAgent()
        
        # Run the interactive session
        browser_agent.run_single_prompt("go to google")
        while True:
            prompt = input("Enter your prompt (or 'exit' to quit): ")
            if prompt.lower() == 'exit':
                break

            browser_agent.run_single_prompt(prompt)

        
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
