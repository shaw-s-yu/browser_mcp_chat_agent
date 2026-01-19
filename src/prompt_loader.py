from haystack.components.converters import MarkdownToDocument
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack.dataclasses import ChatMessage
import os

from dotenv import load_dotenv
load_dotenv()

path = os.path.expanduser('~/app/prompts/')

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
        3. if the similarity is greater than 90%, reply with the exact the same content of the Instruction section of that document.
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
        return reply.text

if __name__ == "__main__":
    prompt_loader = PromptLoader()
    user_input = input("Enter your question or command: ")
    response = prompt_loader.get_response(user_input)
    print("Response:", response)