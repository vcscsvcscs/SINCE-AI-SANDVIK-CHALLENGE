from pydantic import BaseModel, Field
from typing import Literal
from os import environ
import requests

# Classifier server endpoint URL
CLASSIFIER_ENDPOINT = environ.get("CLASSIFIER_ENDPOINT", "http://classifier-server:8069/classify")

class InquiryResponse(BaseModel):
    is_parts_inquiry: bool = Field(..., description="Whether the message is a spare parts inquiry")
    confidence: float = Field(..., description="Confidence score of the prediction")
    method: Literal["model", "llm"] = Field(..., description="Which method was used for classification")

def call_custom_classifier(message: str) -> InquiryResponse:
    """
    Call the custom classifier server to determine if the message is a spare part inquiry.
    """
    response = requests.post(
        CLASSIFIER_ENDPOINT,
        json={"message": message}
    )
    return response.json()