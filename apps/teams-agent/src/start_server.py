"""FastAPI server setup"""
from os import environ
import traceback
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .agent import process_message
from .models import MessageActionsPayload

app = FastAPI(title="Teams Agent", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    error_msg = str(exc)
    error_trace = traceback.format_exc()
    print(f"\n[ERROR] Unhandled exception in request handler:", file=sys.stderr)
    print(error_trace, file=sys.stderr)
    
    # Return error response with details (only in development/test mode)
    if environ.get("DISABLE_AUTH", "").lower() in ["true", "1", "yes"]:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": error_msg,
                "traceback": error_trace
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error"}
        )


@app.post("/api/messages")
async def messages_endpoint(request: Request):
    """Handle incoming messages from Teams"""
    try:
        # Parse the request body
        body = await request.json()
        
        # Handle different payload formats
        # Teams might send the payload directly or wrapped
        if "value" in body:
            # Payload might be wrapped in a "value" field (common in webhooks)
            payload_data = body["value"]
        elif "message" in body:
            # Payload might be in a "message" field
            payload_data = body["message"]
        elif "type" in body and body.get("type") == "message":
            # Full Activity object - extract message data
            payload_data = {
                "id": body.get("id"),
                "reply_to_id": body.get("replyToId"),
                "message_type": body.get("type"),
                "created_date_time": body.get("timestamp"),
                "last_modified_date_time": body.get("lastModified"),
                "deleted": body.get("deleted", False),
                "subject": body.get("subject"),
                "summary": body.get("summary"),
                "importance": body.get("importance"),
                "locale": body.get("locale"),
                "link_to_message": body.get("linkToMessage"),
                "from": body.get("from"),
                "body": {
                    "content_type": body.get("textFormat", "text"),
                    "content": body.get("text", "")
                },
                "attachment_layout": body.get("attachmentLayout"),
                "attachments": body.get("attachments"),
                "mentions": body.get("mentions"),
                "reactions": body.get("reactions"),
            }
        else:
            # Payload is at root level (MessageActionsPayload format)
            payload_data = body
        
        # Parse as MessageActionsPayload (with extra fields allowed)
        payload = MessageActionsPayload(**payload_data)
        
        # Process the message
        response = await process_message(payload)
        
        # Return response in Teams-compatible format (Activity object)
        return JSONResponse(content=response)
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"\n[ERROR] Exception in messages_endpoint:", file=sys.stderr)
        print(error_trace, file=sys.stderr)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/messages")
async def messages_get():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"status": "ok", "service": "Teams Agent"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
