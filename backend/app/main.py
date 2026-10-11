import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
origenes = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(title="Clínica API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/salud")
def salud():
    return {"estado": "ok"}