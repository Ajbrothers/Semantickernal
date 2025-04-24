import json
import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExercisePlugin:
    def __init__(self, storage_file: str = "exercises.json"):
        self.storage_file = storage_file
        self.exercises = self._load_exercises()
        logger.info("ExercisePlugin initialized with %d exercises", len(self.exercises))

    def _load_exercises(self) -> List[Dict]:
        """Load exercises from storage file."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Error loading exercises: %s", str(e))
        
        # Default exercises if loading fails
        return [
            {
                "id": 1,
                "name": "Push Ups",
                "completed": False,
                "description": "Basic upper body exercise",
                "category": "strength",
                "muscle_groups": ["chest", "triceps", "shoulders"],
                "difficulty": "beginner",
                "sets": 3,
                "reps": 10
            },
            {
                "id": 2,
                "name": "Squats",
                "completed": False,
                "description": "Lower body strength exercise",
                "category": "strength",
                "muscle_groups": ["quadriceps", "glutes", "hamstrings"],
                "difficulty": "beginner",
                "sets": 3,
                "reps": 12
            },
            {
                "id": 3,
                "name": "Plank",
                "completed": True,
                "description": "Core stability exercise",
                "category": "core",
                "muscle_groups": ["abs", "back"],
                "difficulty": "beginner",
                "duration": "30 seconds"
            }
        ]

    def _save_exercises(self):
        """Save exercises to storage file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.exercises, f, indent=2)
        except IOError as e:
            logger.error("Error saving exercises: %s", str(e))

    @kernel_function(name="get_exercises", description="Get the current list of exercises and their status")
    async def get_exercises(self) -> List[Dict]:
        """Get all exercises with their status."""
        logger.debug("Retrieving exercise list")
        return self.exercises

    @kernel_function(name="get_next_exercise", description="Get the next recommended exercise")
    async def get_next_exercise(self) -> Dict:
        """Get the next recommended exercise based on completion status."""
        for exercise in self.exercises:
            if not exercise["completed"]:
                return exercise
        return {"message": "All exercises completed! Add new ones."}

    @kernel_function(name="get_exercise_details", description="Get details for a specific exercise")
    async def get_exercise_details(self, exercise_id: int) -> Dict:
        """Get details of a specific exercise."""
        try:
            exercise_id = int(exercise_id)
            for exercise in self.exercises:
                if exercise["id"] == exercise_id:
                    return exercise
            return {"error": "Exercise not found"}
        except ValueError:
            return {"error": "Invalid exercise ID"}

    @kernel_function(name="toggle_exercise", description="Mark an exercise as completed or not completed")
    async def toggle_exercise(self, exercise_id: int) -> str:
        """Toggle the completion status of an exercise."""
        try:
            exercise_id = int(exercise_id)
            for exercise in self.exercises:
                if exercise["id"] == exercise_id:
                    exercise["completed"] = not exercise["completed"]
                    status = "COMPLETED" if exercise["completed"] else "NOT COMPLETED"
                    self._save_exercises()
                    logger.info("Exercise '%s' status changed to %s", exercise["name"], status)
                    return f"Exercise '{exercise['name']}' is now {status}"
            logger.warning("Exercise with ID %d not found", exercise_id)
            return f"Exercise with ID {exercise_id} not found"
        except ValueError:
            logger.error("Invalid exercise ID format: %s", exercise_id)
            return "Invalid exercise ID format. Please provide a valid number."

    @kernel_function(name="add_exercise", description="Add a new exercise to the list")
    async def add_exercise(
        self,
        name: str,
        category: str = "strength",
        muscle_groups: List[str] = None,
        difficulty: str = "beginner",
        description: Optional[str] = None,
        sets: Optional[int] = None,
        reps: Optional[int] = None, 
        duration: Optional[str] = None
    ) -> str:
        """Add a new exercise to the list."""
        try:
            if not name or not name.strip():
                return "Exercise name cannot be empty"
            
            if len(name) > 50:
                return "Exercise name is too long (max 50 characters)"
            
            if description and len(description) > 200:
                return "Description is too long (max 200 characters)"
            
            new_id = max(exercise["id"] for exercise in self.exercises) + 1
            new_exercise = {
                "id": new_id,
                "name": name,
                "completed": False,
                "category": category,
                "muscle_groups": muscle_groups or [],
                "difficulty": difficulty,
                "description": description or f"{category} exercise for {', '.join(muscle_groups)}" if muscle_groups else f"{category} exercise",
                "sets": sets,
                "reps": reps,
                "duration": duration
            }
            self.exercises.append(new_exercise)
            self._save_exercises()
            logger.info("New exercise added: %s", name)
            return f"Exercise '{name}' added successfully with ID {new_id}"
        except Exception as e:
            logger.error("Error adding exercise: %s", str(e))
            return f"Error adding exercise: {str(e)}"

    @kernel_function(name="remove_exercise", description="Remove an exercise from the list")
    async def remove_exercise(self, exercise_id: int) -> str:
        """Remove an exercise from the list."""
        try:
            exercise_id = int(exercise_id)
            for i, exercise in enumerate(self.exercises):
                if exercise["id"] == exercise_id:
                    removed_name = exercise["name"]
                    del self.exercises[i]
                    self._save_exercises()
                    return f"Exercise '{removed_name}' removed successfully"
            return "Exercise not found"
        except ValueError:
            return "Invalid exercise ID"

    @kernel_function(name="get_exercises_by_category", description="Get exercises by category")
    async def get_exercises_by_category(self, category: str) -> List[Dict]:
        """Get exercises filtered by category."""
        return [ex for ex in self.exercises if ex["category"].lower() == category.lower()]

    @kernel_function(name="get_exercises_by_muscle_group", description="Get exercises by muscle group")
    async def get_exercises_by_muscle_group(self, muscle_group: str) -> List[Dict]:
        """Get exercises filtered by muscle group."""
        return [ex for ex in self.exercises if muscle_group.lower() in [mg.lower() for mg in ex["muscle_groups"]]]