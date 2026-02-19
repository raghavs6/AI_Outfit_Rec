from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Set
from datetime import datetime, timezone
import itertools
import json
import os
import random
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
USERS: Dict[str, dict] = {}
ITEMS: Dict[str, List[dict]] = {}
EXTERNAL_IMAGES: Dict[str, dict] = {}
SWIPES: List[dict] = []
FEED_CACHE: Dict[str, List[str]] = {}

VALID_CATEGORIES = {"top", "bottom", "shoes", "outerwear", "accessory"}

#Folder for images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name ="static")

@app.get("/health")
def health() :
    return {"ok" : True}

class SwipeFeedRequest(BaseModel):
    user_id: str
    pinterest_token: Optional[str] = None
    seed_terms: Optional[List[str]] = None

class SwipeRequest(BaseModel):
    user_id: str
    external_image_id: str
    direction: str

class OutfitRequest(BaseModel):
    user_id: str
    constraints: Optional[dict] = None

class GuestUserResponse(BaseModel):
    user_id: str
    created_at: str

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _validate_user(user_id: str) -> None:
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

def _validate_category(category: str) -> None:
    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Use one of: {sorted(list(VALID_CATEGORIES))}",
        )

def _parse_attributes(attributes_json: Optional[str]) -> dict:
    if not attributes_json:
        return {}
    try:
        parsed = json.loads(attributes_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="attributes_json must be valid JSON")
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=400, detail="attributes_json must be a JSON object")
    return parsed

def _create_external_image(seed_terms: Optional[List[str]]) -> dict:
    external_id = str(uuid.uuid4())
    tags = seed_terms or []
    image = {
        "id": external_id,
        "source": "pinterest",
        "external_id": external_id,
        "image_url": f"https://example.com/pin/{external_id}.jpg",
        "metadata": {"tags": tags},
    }
    EXTERNAL_IMAGES[external_id] = image
    return image

def _build_taste_tags(user_id: str) -> Set[str]:
    tags: Set[str] = set()
    for swipe in SWIPES:
        if swipe["user_id"] == user_id and swipe["direction"] == "like":
            image = EXTERNAL_IMAGES.get(swipe["external_image_id"])
            if image:
                tags.update(image.get("metadata", {}).get("tags", []))
    return tags

def _score_outfit(items: List[dict], taste_tags: Set[str]) -> float:
    if not items:
        return 0.0
    score = 0.0
    for item in items:
        tags = set(item.get("attributes", {}).get("tags", []))
        score += len(tags & taste_tags)
    score += random.random() * 0.25
    return score

@app.post("/users/guest")
def create_guest_user():
    user_id = str(uuid.uuid4())
    USERS[user_id] = {"id": user_id, "created_at": _now_iso()}
    ITEMS[user_id] = []
    return {"user_id": user_id}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    _validate_user(user_id)
    return {"user_id": user_id}

@app.post("/v1/users/guest", response_model=GuestUserResponse)
def create_guest_user_v1():
    user_id = str(uuid.uuid4())
    USERS[user_id] = {"id": user_id, "created_at": _now_iso()}
    ITEMS[user_id] = []
    return {"user_id": user_id, "created_at": USERS[user_id]["created_at"]}


@app.post("/items")
def create_item(user_id: str, category: str):
    _validate_user(user_id)
    _validate_category(category)
    item_id = str(uuid.uuid4())
    item = {"id": item_id, "category": category}
    ITEMS[user_id].append(item)
    return item


@app.get("/items")
def list_items(user_id: str):
    _validate_user(user_id)
    return ITEMS[user_id]

@app.post("/items/upload")
async def upload_item(
    user_id: str = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),
):
    _validate_user(user_id)
    _validate_category(category)
    item_id = str(uuid.uuid4())
    filename = f"{item_id}.jpg"
    path = os.path.join(UPLOAD_DIR, filename)
    contents = await file.read()
    with open(path, "wb") as f:
        f.write(contents)
    item = {
        "id": item_id,
        "category": category,
        "image_url": f"/static/{filename}",
    }
    ITEMS[user_id].append(item)
    return item

@app.post("/v1/closet/items")
async def create_closet_item_v1(
    user_id: str = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),
    attributes_json: Optional[str] = Form(None),
):
    _validate_user(user_id)
    _validate_category(category)
    attributes = _parse_attributes(attributes_json)
    item_id = str(uuid.uuid4())
    filename = f"{item_id}.jpg"
    path = os.path.join(UPLOAD_DIR, filename)
    contents = await file.read()
    with open(path, "wb") as f:
        f.write(contents)
    item = {
        "id": item_id,
        "category": category,
        "image_url": f"/static/{filename}",
        "attributes": attributes,
    }
    ITEMS[user_id].append(item)
    return item

@app.get("/v1/closet/items")
def list_closet_items_v1(user_id: str):
    _validate_user(user_id)
    return ITEMS[user_id]

@app.post("/v1/swipe/feed")
def swipe_feed_v1(req: SwipeFeedRequest):
    _validate_user(req.user_id)
    feed = []
    for _ in range(10):
        image = _create_external_image(req.seed_terms)
        feed.append(image)
    FEED_CACHE[req.user_id] = [img["id"] for img in feed]
    return feed

@app.post("/v1/swipe")
def record_swipe_v1(req: SwipeRequest):
    _validate_user(req.user_id)
    if req.direction not in {"like", "dislike"}:
        raise HTTPException(status_code=400, detail="direction must be like or dislike")
    if req.external_image_id not in EXTERNAL_IMAGES:
        raise HTTPException(status_code=404, detail="External image not found")
    swipe = {
        "id": str(uuid.uuid4()),
        "user_id": req.user_id,
        "external_image_id": req.external_image_id,
        "direction": req.direction,
        "created_at": _now_iso(),
    }
    SWIPES.append(swipe)
    return swipe

@app.post("/v1/outfits/generate")
def generate_outfits_v1(req: OutfitRequest):
    _validate_user(req.user_id)
    closet = ITEMS.get(req.user_id, [])
    if not closet:
        return {"outfits": []}

    taste_tags = _build_taste_tags(req.user_id)
    tops = [i for i in closet if i.get("category") == "top"]
    bottoms = [i for i in closet if i.get("category") == "bottom"]
    shoes = [i for i in closet if i.get("category") == "shoes"]
    outerwear = [i for i in closet if i.get("category") == "outerwear"]
    accessories = [i for i in closet if i.get("category") == "accessory"]

    base_combos = list(itertools.product(tops or [None], bottoms or [None], shoes or [None]))
    outfits = []
    for top, bottom, shoe in base_combos:
        items = [i for i in [top, bottom, shoe] if i is not None]
        if outerwear:
            items = items + [random.choice(outerwear)]
        if accessories:
            items = items + [random.choice(accessories)]
        score = _score_outfit(items, taste_tags)
        outfits.append(
            {
                "id": str(uuid.uuid4()),
                "items": [i["id"] for i in items],
                "score": score,
                "explanations": {
                    "matched_tags": sorted(list(taste_tags)),
                    "note": "Stub ML scoring based on tag overlap and randomness.",
                },
            }
        )

    outfits.sort(key=lambda o: o["score"], reverse=True)
    return {"outfits": outfits[:10]}
