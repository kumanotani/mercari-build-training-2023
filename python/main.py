import os
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import hashlib
from typing import Optional
import sqlite3

DATABASE="../db/mercari.sqlite3"

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO #DEBUGに変えるとImage not foundが出る
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(None),image: Optional[str] = Form("images/default.jpg")): #curlコマンドからの相対パス
    
    try:
        with open('items.json', 'r') as f:
            data = json.load(f) #data: dict
    except FileNotFoundError:
        data = {"items": []}
    
    #画像の保存
    image_folder = 'images'
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)




    with open(image, 'rb') as imagefile:
        content = imagefile.read()
    hash_value = hashlib.sha256(content).hexdigest()
    file_name = f"{hash_value}.jpg"
    with open(os.path.join(image_folder, file_name), 'wb') as f:
        f.write(content)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, category, image_name) VALUES (?, ?, ?)",
            (name, category, f"{hash_value}.jpg")
        )
        conn.commit()
        item_id = cursor.lastrowid
        return {"message": "Item added successfully", "item_id": item_id}


@app.get("/items")
def get_item_list():

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()
        return {"items": items}
    # try:
    #     with open('items.json', 'r') as f:
    #         data = json.load(f) #data: dict
    # except FileNotFoundError:
    #     data = {"items": []}
    # return data

@app.get("/items/{item_id}")
def get_item(item_id: int):
    # try:
    #     with open('items.json', 'r') as f:
    #         data = json.load(f) #data: dict
    # except FileNotFoundError:
    #     data = {"items": []}
    # return data["items"][item_id]
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id=?", (item_id,))
        item = cursor.fetchone()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"item": item}



@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
