import json
import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FoodPlugin:
    def __init__(self, storage_file: str = "meals.json"):
        self.storage_file = storage_file
        self.meals = self._load_meals()
        logger.info("FoodPlugin initialized with %d meals", len(self.meals))

    def _load_meals(self) -> List[Dict]:
        """Load meals from storage file."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Error loading meals: %s", str(e))
        
        # Default meals if loading fails
        return [
            {
                "id": 1,
                "name": "Chicken Salad",
                "consumed": False,
                "description": "Healthy protein-rich meal",
                "category": "lunch",
                "ingredients": ["chicken", "lettuce", "tomato", "cucumber"],
                "calories": 350,
                "protein": 30,
                "carbs": 10,
                "fats": 15
            },
            {
                "id": 2,
                "name": "Oatmeal",
                "consumed": True,
                "description": "Breakfast with fruits",
                "category": "breakfast",
                "ingredients": ["oats", "milk", "banana", "honey"],
                "calories": 300,
                "protein": 10,
                "carbs": 50,
                "fats": 5
            }
        ]

    def _save_meals(self):
        """Save meals to storage file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.meals, f, indent=2)
        except IOError as e:
            logger.error("Error saving meals: %s", str(e))

    @kernel_function(name="get_meals", description="Get the current list of meals and their status")
    async def get_meals(self) -> List[Dict]:
        """Get all meals with their status."""
        logger.debug("Retrieving meal list")
        return self.meals

    @kernel_function(name="get_meal_suggestion", description="Get a meal suggestion based on preferences")
    async def get_meal_suggestion(self, preference: str = "") -> Dict:
        """Get a meal suggestion based on preferences."""
        if preference:
            for meal in self.meals:
                if not meal["consumed"] and preference.lower() in meal["name"].lower():
                    return meal
        for meal in self.meals:
            if not meal["consumed"]:
                return meal
        return {"message": "All meals consumed! Add new ones."}

    @kernel_function(name="get_meal_details", description="Get details for a specific meal")
    async def get_meal_details(self, meal_id: int) -> Dict:
        """Get details of a specific meal."""
        try:
            meal_id = int(meal_id)
            for meal in self.meals:
                if meal["id"] == meal_id:
                    return meal
            return {"error": "Meal not found"}
        except ValueError:
            return {"error": "Invalid meal ID"}

    @kernel_function(name="log_meal", description="Mark a meal as consumed or not consumed")
    async def log_meal(self, meal_id: int) -> str:
        """Toggle the consumption status of a meal."""
        try:
            meal_id = int(meal_id)
            for meal in self.meals:
                if meal["id"] == meal_id:
                    meal["consumed"] = not meal["consumed"]
                    status = "CONSUMED" if meal["consumed"] else "NOT CONSUMED"
                    self._save_meals()
                    logger.info("Meal '%s' status changed to %s", meal["name"], status)
                    return f"Meal '{meal['name']}' is now {status}"
            logger.warning("Meal with ID %d not found", meal_id)
            return f"Meal with ID {meal_id} not found"
        except ValueError:
            logger.error("Invalid meal ID format: %s", meal_id)
            return "Invalid meal ID format. Please provide a valid number."

    @kernel_function(name="add_meal", description="Add a new meal to the list")
    async def add_meal(
        self,
        name: str,
        category: str = "lunch",
        ingredients: List[str] = None,
        calories: Optional[int] = None,
        protein: Optional[int] = None,
        carbs: Optional[int] = None,
        fats: Optional[int] = None,
        description: Optional[str] = None
    ) -> str:
        """Add a new meal to the list."""
        try:
            if not name or not name.strip():
                return "Meal name cannot be empty"
            
            if len(name) > 50:
                return "Meal name is too long (max 50 characters)"
            
            if description and len(description) > 200:
                return "Description is too long (max 200 characters)"
            
            new_id = max(meal["id"] for meal in self.meals) + 1
            new_meal = {
                "id": new_id,
                "name": name,
                "consumed": False,
                "category": category,
                "ingredients": ingredients or [],
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fats": fats,
                "description": description or f"{category} with {', '.join(ingredients)}" if ingredients else f"{category} meal"
            }
            self.meals.append(new_meal)
            self._save_meals()
            logger.info("New meal added: %s", name)
            return f"Meal '{name}' added successfully with ID {new_id}"
        except Exception as e:
            logger.error("Error adding meal: %s", str(e))
            return f"Error adding meal: {str(e)}"

    @kernel_function(name="remove_meal", description="Remove a meal from the list")
    async def remove_meal(self, meal_id: int) -> str:
        """Remove a meal from the list."""
        try:
            meal_id = int(meal_id)
            for i, meal in enumerate(self.meals):
                if meal["id"] == meal_id:
                    removed_name = meal["name"]
                    del self.meals[i]
                    self._save_meals()
                    return f"Meal '{removed_name}' removed successfully"
            return "Meal not found"
        except ValueError:
            return "Invalid meal ID"

    @kernel_function(name="get_meals_by_category", description="Get meals by category")
    async def get_meals_by_category(self, category: str) -> List[Dict]:
        """Get meals filtered by category."""
        return [meal for meal in self.meals if meal["category"].lower() == category.lower()]

    @kernel_function(name="get_meals_by_ingredient", description="Get meals by ingredient")
    async def get_meals_by_ingredient(self, ingredient: str) -> List[Dict]:
        """Get meals filtered by ingredient."""
        return [meal for meal in self.meals if ingredient.lower() in [ing.lower() for ing in meal["ingredients"]]]