import logging
import os
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import mongo

load_dotenv()

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo.connect()
    logger.info("Connected to MongoDB!")
    yield
    # Close the connections when the app is shutting down
    await mongo.close()


app = FastAPI(lifespan=lifespan)
app.logger = logger

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamic router loading - get the directory of the current module
current_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.join(current_dir, "api")

for path, _, files in os.walk(api_dir):
    for name in files:
        if not name.endswith(".py") or name.startswith("__"):
            continue

        # Get relative path from api directory
        rel_path = os.path.relpath(path, api_dir)
        if rel_path == ".":
            module_name = name[:-3]  # Remove .py extension
            module_path = f"backend.api.{module_name}"
            prefix = f"/{module_name}"
        else:
            module_name = name[:-3]  # Remove .py extension
            rel_path_parts = rel_path.replace(os.sep, ".")
            module_path = f"backend.api.{rel_path_parts}.{module_name}"
            prefix = f"/{rel_path.replace(os.sep, '/')}/{module_name}"

        try:
            module = __import__(module_path, fromlist=[""])
            if "router" in dir(module):
                app.include_router(module.router, prefix=prefix)
                logger.info(f"[Router Loaded] {prefix}")
            else:
                logger.warning(f"[Router Not Found] {prefix}")
        except Exception:
            logger.error(f"[Router Error] {module_path}\n{traceback.format_exc()}")


@app.get("/")
async def root():
    return "This is the root endpoint."