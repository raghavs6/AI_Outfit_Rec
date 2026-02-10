from fastapi import FastAPI, HTTPException, UploadFile, File, Form
import uuid
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
USERS = set()

#I add this to map each user with their items
ITEMS = {}

VALID_CATEGORIES = {"top", "bottom", "shoes"}

#Folder for images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name ="static")

@app.get("/health")
def health() :
    return {"ok" : True}

@app.post("/users/guest")
def create_guest_user():
    user_id = str(uuid.uuid4())
    USERS.add(user_id)
    ITEMS[user_id] = []
    return {"user_id": user_id}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id}


@app.post("/items")
def create_item(user_id: str, category: str):
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

    # 2) validate category
    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Use one of: {sorted(list(VALID_CATEGORIES))}",
        )

    # 3) create item
    item_id = str(uuid.uuid4())
    item = {"id": item_id, "category": category}

    # 4) save item in the user's closet
    ITEMS[user_id].append(item)

    return item


@app.get("/items")
def list_items(user_id: str):
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    return ITEMS[user_id]

@app.post("/items/upload")
async def upload_item(
    user_id: str = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),
):
    # 1) validate user
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

    # 2) validate category
    if category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")

    # 3) create an item id and filename
    item_id = str(uuid.uuid4())
    filename = f"{item_id}.jpg"
    path = os.path.join(UPLOAD_DIR, filename)

    # 4) read uploaded file bytes and save to disk
    contents = await file.read()
    with open(path, "wb") as f:
        f.write(contents)

    # 5) store item in memory with a URL to the saved image
    item = {
        "id": item_id,
        "category": category,
        "image_url": f"/static/{filename}",
    }
    ITEMS[user_id].append(item)

    return item