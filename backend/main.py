from fastapi import FastAPI, HTTPException
import uuid

app = FastAPI()
USERS = set()

#I add this to map each user with their items
ITEMS = {}

VALID_CATEGORIES = {"top", "bottom", "shoes"}

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

