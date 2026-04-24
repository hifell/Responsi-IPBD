from fastapi import FastAPI, HTTPException
import json
import os

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "wired_data.json")

@app.get("/articles")
def get_articles():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="File data belum ada")
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat membaca file: {str(e)}")