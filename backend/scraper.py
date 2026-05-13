import requests
from bs4 import BeautifulSoup
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RECIPES_FILE = os.path.join(BASE_DIR, "recipes.json")

def get_recipe(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return None

    except Exception as e:
        print("Request failed:", e)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    recipe_data = None

    # Find all JSON-LD script tags
    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:

        if not script.string:
            continue

        try:
            data = json.loads(script.string)

            # CASE 1: JSON is a list
            if isinstance(data, list):

                for item in data:

                    if (
                        isinstance(item, dict)
                        and item.get("@type") == "Recipe"
                    ):
                        recipe_data = item
                        break

            # CASE 2: JSON is a dictionary
            elif isinstance(data, dict):

                # Direct Recipe object
                if data.get("@type") == "Recipe":
                    recipe_data = data

                # Wrapped inside @graph
                elif "@graph" in data:

                    for item in data["@graph"]:

                        if (
                            isinstance(item, dict)
                            and item.get("@type") == "Recipe"
                        ):
                            recipe_data = item
                            break

        except Exception:
            continue

        if recipe_data:
            break

    if not recipe_data:
        print("Recipe not found.")
        return None

    # Build clean recipe object
    recipe = {
        "title": recipe_data.get("name", "No title"),
        "ingredients": recipe_data.get("recipeIngredient", []),
        "instructions": [],
        "url": url
    }

    instructions = recipe_data.get("recipeInstructions", [])

    for step in instructions:

        if isinstance(step, dict):
            text = step.get("text", "")

        else:
            text = step

        recipe["instructions"].append(text)

    # SAVE RECIPE
    save_recipe(recipe)

    return recipe



def save_recipe(recipe):

    recipes = []

    # Load existing recipes
    if os.path.exists(RECIPES_FILE):

        try:
            with open(RECIPES_FILE, "r") as file:
                recipes = json.load(file)

        except Exception as e:
            print("Error loading recipes:", e)


    for existing_recipe in recipes:
        if existing_recipe.get("url") == recipe.get("url"):
            print("Recipe already exists. Skipping the save")
            return

    # Add new recipe
    recipes.append(recipe)

    # Save updated recipes
    try:
        with open(RECIPES_FILE, "w") as file:
            json.dump(recipes, file, indent=4)

        print("Recipe saved successfully")

    except Exception as e:
        print("Error saving recipe:", e)