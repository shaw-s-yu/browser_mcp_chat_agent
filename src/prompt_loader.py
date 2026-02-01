from click import prompt
from haystack.components.converters import MarkdownToDocument
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack.dataclasses import ChatMessage
import os
import json

from dotenv import load_dotenv

from db.oracle_sql import OracleSQL
from prompt_converter import PromptConverter
load_dotenv()

path = os.path.expanduser('prompts/')

class PromptLoader:
    def __init__(self):

        # Convert markdown to documents
        markdown_converter = MarkdownToDocument()
        documents = markdown_converter.run(sources=[path+f for f in os.listdir(path) if f.endswith(".md")])["documents"]

        # Extract content from documents
        self.content = "\n".join([doc.content for doc in documents])

        self.system_message = f"""
        You are a helpful assistant that helps to read documents concisely.
        When user gives you a question or command, you should:
        1. look into each document carefully.
        2. calculate the similarity rate of the question or command to the Description section of each of the documents.
        3. if the similarity is greater than 90%, reply with the exact the same content of the Instruction section of that document, and DO NOT inlcude the Template section
        4. otherwise, reply the original question.

        The documents are as follows:
        {self.content}
        """

        # Create generator and run
        self.chat_generator = GoogleGenAIChatGenerator(model="gemini-2.5-pro")

    def get_response(self, user_input: str) -> str:
        # Create chat messages
        messages = [
            ChatMessage.from_user(user_input),
            ChatMessage.from_system(self.system_message),
        ]

        # Create generator and run
        response = self.chat_generator.run(messages=messages)

        # Print the response in a readable format
        reply = response["replies"][0]
        reply= reply.text
        if reply:
            reply_stripped = reply.strip()
            # Check if reply matches RUN_xxx_ACTION format
            if reply_stripped.startswith("RUN_") and reply_stripped.endswith("_ACTION"):
                return self.process_sql_to_prompt(reply_stripped)
            return reply_stripped

        return reply

    def process_sql_to_prompt(self, action: str) -> str:
        # Load action mapper
        action_mapper_path = os.path.join(os.path.dirname(__file__), 'action_mapper.json')
        with open(action_mapper_path, 'r') as f:
            action_mapper = json.load(f)
        
        # Get action config
        if action not in action_mapper:
            raise ValueError(f"Action '{action}' not found in action_mapper.json")
        
        action_config = action_mapper[action]
        prompt_file = action_config['prompt_file']
        sql_file = action_config['sql']
        
        # Run SQL query to generate CSV
        oracle = OracleSQL()
        success, message = oracle.run_query_file(sql_file)
        if not success:
            raise ValueError(f"Error executing SQL query: {message}")
        
        # Use PromptConverter to generate prompts
        converter = PromptConverter()
        
        # Build paths
        prompt_file_path = os.path.join(os.path.dirname(__file__), 'prompts', prompt_file)
        csv_file_path = os.path.join(os.path.dirname(__file__), 'db', 'data', 'temp_sql_result.csv')
        
        # Generate prompts
        final_prompt = converter.generate_prompts(prompt_file_path, csv_file_path)
        
        return final_prompt

if __name__ == "__main__":
    prompt_loader = PromptLoader()
    user_input = input("Enter your question or command: ")
    response = prompt_loader.get_response(user_input)
    print("Response:", response)