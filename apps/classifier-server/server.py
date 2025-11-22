import os
import json
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import pipeline
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Spare Parts Inquiry Classifier")

# Load the spare parts model at startup
classifier = pipeline(
    "text-classification",
    model="./spare_parts_model",
    tokenizer="./spare_parts_model"
)

# Featherless.ai configuration
FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY")
if FEATHERLESS_API_KEY:
    FEATHERLESS_API_KEY = FEATHERLESS_API_KEY.strip()  # Remove any whitespace

CONFIDENCE_THRESHOLD = 0.61

# Initialize OpenAI client for Featherless.ai
client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key=FEATHERLESS_API_KEY or "dummy"  # Provide dummy if not set, will error later
)
# Pydantic models for request/response
class InquiryRequest(BaseModel):
    message: str = Field(..., description="The message to classify")

class InquiryResponse(BaseModel):
    is_parts_inquiry: bool = Field(..., description="Whether the message is a spare parts inquiry")
    confidence: float = Field(..., description="Confidence score of the prediction")
    method: Literal["model", "llm"] = Field(..., description="Which method was used for classification")

class LLMAnalysisResponse(BaseModel):
    is_parts_inquiry: bool = Field(..., description="Whether the message is about spare parts")

async def classify_with_model(message: str) -> tuple[bool, float]:
    """
    Classify message using the trained spare parts model.
    Returns (is_parts_inquiry, confidence)
    """
    result = classifier(message)[0]
    label = result['label']
    score = result['score']

    # LABEL_1 indicates spare parts inquiry
    is_parts_inquiry = (label == 'LABEL_1')

    return is_parts_inquiry, score

def classify_with_llm(message: str) -> bool:
    """
    Use Featherless.ai reasoning LLM to determine if message is a spare parts inquiry.
    Returns a type-safe boolean.
    """
    if not FEATHERLESS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="FEATHERLESS_API_KEY environment variable is not set"
        )

    system_prompt = """You are a classifier that determines if a message is asking about spare parts, replacement parts, or components.

Your task is to analyze the message and determine if it's related to:
- Requesting spare parts or replacement parts
- Asking about part availability
- Inquiring about part numbers, models, or specifications
- Questions about ordering or purchasing parts
- Parts-related documentation or manuals

Respond with a JSON object containing only a boolean field 'is_parts_inquiry'.

Examples:
- "Need a replacement gasket for model TX900" -> {"is_parts_inquiry": true}
- "Do you have spare filters?" -> {"is_parts_inquiry": true}
- "What time is the meeting?" -> {"is_parts_inquiry": false}
- "Lunch at 14:00?" -> {"is_parts_inquiry": false}

Be strict: only return true if the message is clearly about spare parts."""

    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this message: {message}"}
            ],
            temperature=0.1,
            max_tokens=100,
            response_format={"type": "json_object"}
        )

        # Get the content from the response
        content = response.model_dump()['choices'][0]['message']['content']

        # Parse the JSON response
        parsed_response = json.loads(content)

        # Validate and extract the boolean with type safety
        if 'is_parts_inquiry' not in parsed_response:
            raise ValueError("LLM response missing 'is_parts_inquiry' field")

        is_parts_inquiry = parsed_response['is_parts_inquiry']

        # Ensure it's a boolean
        if not isinstance(is_parts_inquiry, bool):
            raise ValueError(f"Expected boolean, got {type(is_parts_inquiry)}")

        return is_parts_inquiry

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error calling Featherless.ai API: {str(e)}"
        )

@app.post("/classify", response_model=InquiryResponse)
async def classify_inquiry(request: InquiryRequest) -> InquiryResponse:
    """
    Classify a message as a spare parts inquiry or not.

    If the model's confidence is >= 0.61, use the model's prediction.
    If confidence is < 0.61, use a reasoning LLM for evaluation.
    """
    # First, try with the trained model
    is_parts_inquiry, confidence = await classify_with_model(request.message)

    # If confidence is high enough, return the model's prediction
    if confidence >= CONFIDENCE_THRESHOLD:
        return InquiryResponse(
            is_parts_inquiry=is_parts_inquiry,
            confidence=confidence,
            method="model"
        )

    # Otherwise, use the LLM for a more careful evaluation
    is_parts_inquiry = classify_with_llm(request.message)

    return InquiryResponse(
        is_parts_inquiry=is_parts_inquiry,
        confidence=confidence,  # Still report the original model confidence
        method="llm"
    )

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    if FEATHERLESS_API_KEY:
        print(f"✓ Featherless API key loaded (length: {len(FEATHERLESS_API_KEY)})")
        print(f"  First 10 chars: {FEATHERLESS_API_KEY[:10]}...")
        print(f"  Last 5 chars: ...{FEATHERLESS_API_KEY[-5:]}")
    else:
        print("⚠ WARNING: FEATHERLESS_API_KEY not found in environment")
    print(f"✓ Spare parts model loaded")
    print(f"✓ Confidence threshold: {CONFIDENCE_THRESHOLD}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": classifier is not None,
        "api_key_configured": FEATHERLESS_API_KEY is not None,
        "api_key_length": len(FEATHERLESS_API_KEY) if FEATHERLESS_API_KEY else 0
    }

@app.get("/debug-env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    return {
        "env_var_exists": "FEATHERLESS_API_KEY" in os.environ,
        "api_key_loaded": FEATHERLESS_API_KEY is not None,
        "api_key_length": len(FEATHERLESS_API_KEY) if FEATHERLESS_API_KEY else 0,
        "first_chars": FEATHERLESS_API_KEY[:10] if FEATHERLESS_API_KEY else None,
        "cwd": os.getcwd(),
        "env_file_exists": os.path.exists(".env")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
