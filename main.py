import os
import azure.functions as func
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from models import FeedbackCreate, FeedbackUpdate
from typing import List
from utils import generate_custom_id

app = FastAPI()

# API Key
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_DETAILS = os.getenv("MONGO_DETAILS")
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client["bootcamp_db"]
feedback_collection = database.get_collection("feedbacks")

@app.middleware("http")
async def api_key_validator(request: Request, call_next):
    if API_KEY_NAME in request.headers:
        provided_api_key = request.headers[API_KEY_NAME]
        if provided_api_key == API_KEY:
            response = await call_next(request)
            return response
    raise HTTPException(status_code=401, detail="Invalid or missing API Key")

# Utility functions
def feedback_helper(feedback) -> dict:
    return {
        "feedback_id": feedback["feedback_id"],
        "target_id": feedback["target_id"],
        "given_by": feedback["given_by"],
        "feedback": feedback["feedback"],
    }

# Routes

@app.post("/createFeedback", response_model=dict)
async def create_feedback(feedback: FeedbackCreate):
    # Check if given_by user exists and is a professor
    # (Assuming you have access to user-service or have cached user roles)
    # Skipping for now as per instructions

    # Ensure a teacher can only give one feedback to a single student
    existing_feedback = await feedback_collection.find_one({
        "target_id": feedback.target_id,
        "given_by": feedback.given_by
    })
    if existing_feedback:
        raise HTTPException(status_code=400, detail="Feedback already exists for this user by the teacher")
    
    # Generate feedback_id
    feedback_id = generate_custom_id("feed")
    
    feedback_dict = feedback.dict()
    feedback_dict["feedback_id"] = feedback_id
    
    await feedback_collection.insert_one(feedback_dict)
    
    return feedback_helper(feedback_dict)

@app.get("/getFeedbacksByUserID/{user_id}", response_model=List[dict])
async def get_feedbacks_by_user_id(user_id: str):
    feedbacks = []
    async for feedback in feedback_collection.find({"target_id": user_id}):
        feedbacks.append(feedback_helper(feedback))
    return feedbacks

@app.get("/getGivenFeedbacksByUserID/{user_id}", response_model=List[dict])
async def get_given_feedbacks_by_user_id(user_id: str):
    feedbacks = []
    async for feedback in feedback_collection.find({"given_by": user_id}):
        feedbacks.append(feedback_helper(feedback))
    return feedbacks

@app.get("/getFeedbacks", response_model=List[dict])
async def get_feedbacks():
    feedbacks = []
    async for feedback in feedback_collection.find():
        feedbacks.append(feedback_helper(feedback))
    return feedbacks

@app.put("/updateFeedback/{feedback_id}", response_model=dict)
async def update_feedback(feedback_id: str, feedback_data: FeedbackUpdate):
    feedback = await feedback_collection.find_one({"feedback_id": feedback_id})
    if feedback:
        await feedback_collection.update_one(
            {"feedback_id": feedback_id}, {"$set": feedback_data.dict(exclude_unset=True)}
        )
        updated_feedback = await feedback_collection.find_one({"feedback_id": feedback_id})
        return feedback_helper(updated_feedback)
    raise HTTPException(status_code=404, detail="Feedback not found")

@app.delete("/deleteFeedback/{feedback_id}", response_model=dict)
async def delete_feedback(feedback_id: str):
    result = await feedback_collection.delete_one({"feedback_id": feedback_id})
    if result.deleted_count:
        return {"status": "Feedback deleted"}
    raise HTTPException(status_code=404, detail="Feedback not found")
