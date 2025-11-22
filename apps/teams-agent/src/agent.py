"""FastAPI agent implementation for Teams bot"""
import sys
import traceback
from os import environ
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from .models import MessageActionsPayload
from .card_messages import CardMessages

load_dotenv()

# Pre-chosen user ID - set this in environment variable TARGET_USER_ID
TARGET_USER_ID = environ.get("TARGET_USER_ID", "")

# Condition settings - customize these as needed
# Only send notifications if message contains these keywords (empty list = send all messages)
NOTIFICATION_KEYWORDS = environ.get("NOTIFICATION_KEYWORDS", "").split(",") if environ.get("NOTIFICATION_KEYWORDS") else []
# Filter out empty strings
NOTIFICATION_KEYWORDS = [kw.strip().lower() for kw in NOTIFICATION_KEYWORDS if kw.strip()]

# Store conversation references for proactive messaging
# In production, you'd use persistent storage (e.g., CosmosDB, Blob Storage)
conversation_references: Dict[str, Dict[str, Any]] = {}


def should_send_notification(payload: MessageActionsPayload) -> bool:
    """Check if notification should be sent based on conditions"""
    # Condition 1: Message must not be empty
    if not payload.body or not payload.body.content or not payload.body.content.strip():
        return False
    
    # Condition 2: Message must not be from the bot itself
    if payload.from_property and payload.from_property.application:
        # Skip if message is from an application (bot)
        return False
    
    # Condition 3: If keywords are configured, message must contain at least one keyword
    if NOTIFICATION_KEYWORDS:
        message_lower = payload.body.content.lower()
        if not any(keyword in message_lower for keyword in NOTIFICATION_KEYWORDS):
            return False
    
    return True


def get_message_text(payload: MessageActionsPayload) -> str:
    """Extract message text from payload"""
    if payload.body and payload.body.content:
        return payload.body.content
    return "A message was received in the channel"


def get_sender_name(payload: MessageActionsPayload) -> str:
    """Extract sender name from payload"""
    if payload.from_property:
        if payload.from_property.user and payload.from_property.user.display_name:
            return payload.from_property.user.display_name
        if payload.from_property.user and payload.from_property.user.id:
            return payload.from_property.user.id
    return "Someone"


def is_channel_message(payload: MessageActionsPayload) -> bool:
    """Check if message is from a channel (not a direct message)"""
    # Check if conversation type indicates channel
    if payload.from_property and payload.from_property.conversation:
        conv_type = payload.from_property.conversation.conversation_identity_type
        if conv_type and "channel" in conv_type.lower():
            return True
    return False


def store_conversation_reference(payload: MessageActionsPayload):
    """Store conversation reference for the user who sent the message"""
    if payload.from_property and payload.from_property.user and payload.from_property.user.id:
        user_id = payload.from_property.user.id
        # Store minimal reference needed for future operations
        conversation_references[user_id] = {
            "user_id": user_id,
            "message_id": payload.id,
            "conversation_id": payload.from_property.conversation.id if payload.from_property.conversation else None,
        }


async def process_message(payload: MessageActionsPayload) -> Dict[str, Any]:
    """Process incoming message and return response in Teams Activity format"""
    # Store conversation reference
    store_conversation_reference(payload)
    
    # Build base activity response
    response_activity = {
        "type": "message",
        "text": "",
    }    

    # Check condition before sending notification
    if not should_send_notification(payload):
        # Conditions not met, return acknowledgment
        response_activity["text"] = "Message received but notification conditions not met."
        return response_activity
    
    # This is a channel message
    message_text = get_message_text(payload)
    sender_name = get_sender_name(payload)

    spare_part_match = await analyze_spare_parts(message_text)



    if spare_part_match:
        spare_part_info = (
            f"Detected spare part: {spare_part_match['name']} "
            f"(catalog id: {spare_part_match['id']}, score: {spare_part_match['score']:.2f})"
        )
    else:
        spare_part_info = "No spare parts detected in the message."

    # 2) create deep link (not used yet, but let's keep it for future)
    channel_deep_link = CardMessages.create_teams_deep_link(payload)
    
    # Send card to pre-chosen user (in a real implementation, you'd send this via Teams API)
    if TARGET_USER_ID:
        status_text = f"✓ Notification card sent to the configured user about: {message_text}"
    else:
        status_text = "⚠ TARGET_USER_ID not configured. Please set it in environment variables."
    
    # 4) form the response activity
    response_activity["text"] = status_text + "\n\n" + spare_part_info
    
    return response_activity
    
async def analyze_spare_parts(message_text: str) -> Optional[Dict[str, object]]:
    """
    Temporary stub that pretends to analyze spare parts.
    For now it always returns None.
    Later we will move it to a separate module and add LLM + catalog logic.
    """
    return None