
from browser_agent import BrowserAgent
from prompt_loader import PromptLoader

def get_is_login_page(browser_agent: BrowserAgent) -> bool:
    ans = browser_agent.run_single_prompt_no_v("""
    Is this page requesting user to sign in?
        your answer should only be "YES" or "NO"

        do not reply anything else
    """)
    if ans.strip().upper() == "YES":
        return True
    else:
        return False

if __name__ == '__main__':
    # This block demonstrates how to use the refactored BrowserAgent class.
    # It requires a .env file with your GEMINI_API_KEY.
    try:
        
        # Inject dependencies into the agent
        browser_agent = BrowserAgent()
        prompt_agent = PromptLoader()

        
        # Run the interactive session
        browser_agent.run_single_prompt("go to google")
        while True:
            if get_is_login_page(browser_agent):
                print("The current page is a login page. Please log in manually before continuing.")
            prompt = input("Enter your prompt (or 'exit' to quit): ")
            if prompt.lower() == 'exit':
                break

            preprossed_prompt = prompt_agent.get_response(prompt)
            browser_agent.run_single_prompt(preprossed_prompt)

        
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
