from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Set
from datetime import datetime, timezone
import itertools
import json
import os
import random
import uuid

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the environment or .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_CATEGORIES = {"top", "bottom", "shoes", "outerwear", "accessory"}

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        user_response = supabase.auth.get_user(token)
        if user_response and user_response.user:
            return user_response.user.id
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

@app.get("/health")
def health() :
    return {"ok" : True}

class SwipeFeedRequest(BaseModel):
    pinterest_token: Optional[str] = None
    seed_terms: Optional[List[str]] = None

class SwipeRequest(BaseModel):
    external_image_id: str
    direction: str

class OutfitRequest(BaseModel):
    constraints: Optional[dict] = None

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

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

@app.get("/users/me")
def get_user_me(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}

@app.post("/items")
def create_item(category: str, user_id: str = Depends(get_current_user)):
    _validate_category(category)
    
    item_id = str(uuid.uuid4())
    data = {
        "id": item_id,
        "user_id": user_id,
        "category": category,
        "image_url": "", 
        "attributes": {}
    }
    
    res = supabase.table("items").insert(data).execute()
    if len(res.data) > 0:
        return res.data[0]
    raise HTTPException(status_code=500, detail="Failed to create item")

@app.get("/items")
def list_items(user_id: str = Depends(get_current_user)):
    res = supabase.table("items").select("*").eq("user_id", user_id).execute()
    return res.data

@app.post("/items/upload")
async def upload_item(
    category: str = Form(...),
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    _validate_category(category)
    
    item_id = str(uuid.uuid4())
    filename = f"{user_id}/{item_id}.jpg"
    
    contents = await file.read()
    
    # Upload to Supabase Storage
    try:
        supabase.storage.from_("clothes").upload(
            file=contents,
            path=filename,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
        
    # Get public URL
    public_url_res = supabase.storage.from_("clothes").get_public_url(filename)
    
    data = {
        "id": item_id,
        "user_id": user_id,
        "category": category,
        "image_url": public_url_res,
        "attributes": {}
    }
    
    res = supabase.table("items").insert(data).execute()
    if len(res.data) > 0:
        return res.data[0]
    raise HTTPException(status_code=500, detail="Failed to create item record")

@app.post("/v1/closet/items")
async def create_closet_item_v1(
    category: str = Form(...),
    file: UploadFile = File(...),
    attributes_json: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user)
):
    _validate_category(category)
    attributes = _parse_attributes(attributes_json)
    
    item_id = str(uuid.uuid4())
    filename = f"{user_id}/{item_id}.jpg"
    
    contents = await file.read()
    
    try:
        supabase.storage.from_("clothes").upload(
            file=contents,
            path=filename,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
        
    public_url_res = supabase.storage.from_("clothes").get_public_url(filename)
    
    data = {
        "id": item_id,
        "user_id": user_id,
        "category": category,
        "image_url": public_url_res,
        "attributes": attributes
    }
    
    res = supabase.table("items").insert(data).execute()
    if len(res.data) > 0:
        return res.data[0]
    raise HTTPException(status_code=500, detail="Failed to create closet item")

@app.get("/v1/closet/items")
def list_closet_items_v1(user_id: str = Depends(get_current_user)):
    res = supabase.table("items").select("*").eq("user_id", user_id).execute()
    return res.data

# Note: These v1 endpoints for swipes and outfits will need slight adjustments
# For now, swipes will be logged to Supabase DB.
@app.post("/v1/swipe/feed")
def swipe_feed_v1(req: SwipeFeedRequest, user_id: str = Depends(get_current_user)):
    # Mocking a feed. In a real app we'd fetch from Pinterest or a DB table
    feed = []
    for _ in range(10):
        external_id = str(uuid.uuid4())
        image = {
            "id": external_id,
            "source": "pinterest",
            "external_id": external_id,
            "image_url": f"https://example.com/pin/{external_id}.jpg",
            "metadata": {"tags": req.seed_terms or []},
        }
        feed.append(image)
    return feed

@app.post("/v1/swipe")
def record_swipe_v1(req: SwipeRequest, user_id: str = Depends(get_current_user)):
    if req.direction not in {"like", "dislike"}:
        raise HTTPException(status_code=400, detail="direction must be like or dislike")
    
    data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "external_image_id": req.external_image_id,
        "direction": req.direction
    }
    
    res = supabase.table("swipes").insert(data).execute()
    if len(res.data) > 0:
        return res.data[0]
    raise HTTPException(status_code=500, detail="Failed to record swipe")

def _build_taste_tags(swipes: List[dict]) -> Set[str]:
    tags: Set[str] = set()
    # Mock extracting tags from swipes... 
    for swipe in swipes:
        if swipe.get("direction") == "like":
            # Just mimicking getting some tags
            tags.update(["casual", "summer", "dark"]) 
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

@app.post("/v1/outfits/generate")
def generate_outfits_v1(req: OutfitRequest, user_id: str = Depends(get_current_user)):
    # Get user wardrobe
    res_items = supabase.table("items").select("*").eq("user_id", user_id).execute()
    closet = res_items.data
    
    if not closet:
        return {"outfits": []}

    # Get user swipes
    res_swipes = supabase.table("swipes").select("*").eq("user_id", user_id).execute()
    taste_tags = _build_taste_tags(res_swipes.data)
    
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
