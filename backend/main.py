from fastapi import FastAPI
import uuid

app = FastAPI()

@app.get("/health")
def health() :
    return {"ok" : True}

@app.post("/users/guest")
def create_guest_user():
    user_id = str(uuid.uuid4())
    return {"user_id": user_id}