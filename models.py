from pydantic import BaseModel
from typing import Optional

class Feedback(BaseModel):
    feedback_id: str
    target_id: str
    given_by: str
    feedback: str

class FeedbackCreate(BaseModel):
    target_id: str
    given_by: str
    feedback: str

class FeedbackUpdate(BaseModel):
    feedback: Optional[str] = None
