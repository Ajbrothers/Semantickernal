import asyncio
import os
import logging
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from plugin import ExercisePlugin  # Import from local plugin.py
from food_plugin import FoodPlugin  # Import the new FoodPlugin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def initialize_kernel() -> Kernel:
    """Initialize and configure the Semantic Kernel with both plugins."""
    kernel = Kernel()
    logger.info("Initializing Semantic Kernel")

    try:
        # Configure Azure OpenAI
        azure_chat = AzureChatCompletion(
            service_id="azure_chat_completion",
            deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        )
        kernel.add_service(azure_chat)
        logger.info("Azure OpenAI service configured successfully")
        
        # Add the plugins
        kernel.add_plugin(ExercisePlugin(), plugin_name="Exercises")
        logger.info("Exercise plugin added successfully")
        
        kernel.add_plugin(FoodPlugin(), plugin_name="Food")
        logger.info("Food plugin added successfully")
        
    except Exception as e:
        logger.error("Failed to configure Azure OpenAI: %s", str(e))
        raise

    return kernel

async def main():
    """Main application entry point."""
    try:
        kernel = await initialize_kernel()
        
        # Chat settings
        execution_settings = AzureChatPromptExecutionSettings(
            temperature=0.3,
            max_tokens=200,
        )

        # Initialize chat history
        chat_history = ChatHistory()
        chat_history.add_system_message(
            "You are a helpful health assistant that can manage both exercises and meals. "
            "You can help users track their workouts, suggest new exercises, "
            "manage meal plans, and provide nutrition advice. Be positive and encouraging!"
        )

        print("\nWelcome to your Health Assistant!")
        print("Type 'help' for commands or 'exit' to quit.\n")
        print("Available categories:")
        print("- Exercise: Manage workouts and exercises")
        print("- Food: Manage meals and nutrition\n")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == 'exit':
                break
                
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("\nExercise commands:")
                print("- show exercises: List all exercises")
                print("- next exercise: Get the next recommended exercise")
                print("- complete [id]: Mark an exercise as completed")
                print("- add exercise: Add a new exercise")
                print("- remove exercise [id]: Remove an exercise")
                print("- details exercise [id]: Show exercise details")
                
                print("\nFood commands:")
                print("- show meals: List all meals")
                print("- suggest meal: Get a meal suggestion")
                print("- log meal [id]: Mark a meal as consumed")
                print("- add meal: Add a new meal")
                print("- remove meal [id]: Remove a meal")
                print("- details meal [id]: Show meal details")
                print("\n- exit: Quit the program\n")
                continue

            chat_history.add_user_message(user_input)
            
            try:
                # Retrieve the chat service using the correct service_id
                chat_service = kernel.get_service("azure_chat_completion")
                result = await chat_service.get_chat_message_content(
                    chat_history=chat_history,
                    settings=execution_settings,
                    kernel=kernel
                )
                print(f"\nAssistant: {result}")
                chat_history.add_assistant_message(str(result))
            except Exception as e:
                print(f"\nError occurred: {str(e)}")

    except Exception as e:
        logger.error("Application error: %s", str(e))
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())