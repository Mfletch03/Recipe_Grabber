from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scraper import get_recipe

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Recipe API running"}


@app.get("/recipe")
def fetch_recipe(url: str):

    recipe = get_recipe(url)

    if not recipe:
        return {"error": "Recipe not found"}

    return recipe