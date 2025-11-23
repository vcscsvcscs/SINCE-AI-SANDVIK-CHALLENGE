"""FastAPI agent implementation for Teams bot"""
import asyncio
import httpx
from os import environ
from dotenv import load_dotenv
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
import json
import requests

import logging
from pathlib import Path
from .utils.similarity_check import find_best_part_by_term
from .utils.second_llm_check import call_featherless_llm

from .models import MessageActionsPayload
from .card_messages import CardMessages

load_dotenv()

# Pre-chosen user ID - set this in environment variable TARGET_USER_ID
TARGET_USER_ID = environ.get("TARGET_USER_ID", "")

# Webhook URL for sending adaptive cards to the frontend
WEBHOOK_URL = environ.get("WEBHOOK_URL", "http://localhost:5175/api/webhook")

# Classifier server endpoint URL
CLASSIFIER_ENDPOINT = environ.get("CLASSIFIER_ENDPOINT", "http://classifier-server:8069/classify")

LOG_FILE = environ.get("LOG_FILE", "agent.log")
LOG_LEVEL = environ.get("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.DEBUG),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename=LOG_FILE,
    filemode="a",
)
logger = logging.getLogger(__name__)


# === Load spare parts catalog from CSV (pandas) ===

# Condition settings - customize these as needed
# Only send notifications if message contains these keywords (empty list = send all messages)
NOTIFICATION_KEYWORDS = environ.get("NOTIFICATION_KEYWORDS", "").split(",") if environ.get("NOTIFICATION_KEYWORDS") else []
# Filter out empty strings
NOTIFICATION_KEYWORDS = [kw.strip().lower() for kw in NOTIFICATION_KEYWORDS if kw.strip()]

# Store conversation references for proactive messaging
# In production, you'd use persistent storage (e.g., CosmosDB, Blob Storage)
conversation_references: Dict[str, Dict[str, Any]] = {}

    
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
    logger.debug("process_message: payload.id=%s", getattr(payload, "id", None))

    # Store conversation reference
    store_conversation_reference(payload)
    
    # Build base activity response
    response_activity = {
        "type": "message",
        "text": "",
    }
    # Check condition before sending notification (твоя логика фильтра)
    if not should_send_notification(payload):
        response_activity["text"] = "Message received but notification conditions not met."
        return response_activity
    
    message_text = get_message_text(payload)
    sender_name = get_sender_name(payload)
    logger.debug("process_message: sender_name=%r, message_text=%r", sender_name, message_text)

    classifier_response = call_custom_classifier(message_text)
    logger.debug("process_message: classifier_response=%s", classifier_response)

    if classifier_response.confidence > 0.5 and not classifier_response.is_parts_inquiry:
        response_activity["text"] = "Custom classifier: message is not a spare parts inquiry."
        return response_activity
        
    # === NEW: use term + matched_part ===
    spare_part_match = await analyze_spare_parts(message_text)
    logger.debug("process_message: spare_part_match=%s", spare_part_match)

    if spare_part_match:
        term = spare_part_match.get("term") or "<no term>"
        reason = spare_part_match.get("reason") or ""
        matched = spare_part_match.get("matched_part")

        if matched:
            match_text = (
                f"Matched part from catalog: {matched.get('name')} "
                f"(SKU: {matched.get('sku')}), similarity: {matched.get('score'):.2f}"
            )
        else:
            match_text = "No good match found in catalog for this term."

        spare_part_info = f"LLM: message looks spare-part-related. Term: {term}. {match_text}"
        if reason:
            spare_part_info += f" Reason: {reason}"
        # Create Teams deep link to the channel message
        channel_deep_link = CardMessages.create_teams_deep_link(payload)
        # Extract channel name from payload
        channel_name = "Unknown Channel"
        if payload.from_property and payload.from_property.conversation:
            channel_name = payload.from_property.conversation.display_name or channel_name
        
        # Send adaptive card to webhook endpoint (which will be picked up by frontend)
        webhook_payload = {
            "message": message_text,
            "message_id": payload.id or f"msg_{payload.created_date_time}",
            "timestamp": payload.created_date_time or "",
            "channel": channel_name,
            "user": {
                "name": sender_name,
                "id": payload.from_property.user.id if payload.from_property and payload.from_property.user else None
            }
        }
        
        # Call webhook endpoint asynchronously in background (don't wait for response)
        async def send_to_webhook():
            try:
                async with httpx.AsyncClient() as client:
                    webhook_response = await client.post(
                        WEBHOOK_URL,
                        json=webhook_payload,
                        timeout=5.0
                    )
                    if webhook_response.status_code == 200:
                        print(f"[TEAMS-AGENT] ✅ Successfully sent adaptive card to webhook")
                    else:
                        print(f"[TEAMS-AGENT] ⚠️ Webhook returned status {webhook_response.status_code}")
            except Exception as e:
                print(f"[TEAMS-AGENT] ❌ Error calling webhook: {e}")
            
        # Run webhook call in background
        asyncio.create_task(send_to_webhook())
        status_text = (
            f"✓ Notification card sent to the configured user about: {message_text}\n"
            f"Deep link: {channel_deep_link}"
        )
        response_activity["text"] = status_text + "\n\n" + spare_part_info
    else:
        response_activity["text"] = "LLM: message does NOT look spare-part-related."
    
    return response_activity

    
async def analyze_spare_parts(message_text: str) -> Optional[Dict[str, object]]:
    """
    Step 1: LLM decides if the message is related to spare parts and extracts the key term.
    Step 2: Using this term, find the best matching spare part in the CSV catalog (pandas + similarity).
    """
    logger.debug("analyze_spare_parts: message_text=%r", message_text)

    if not message_text:
        logger.info("analyze_spare_parts: empty message_text, returning None")
        return None

    user_prompt = f"Customer message:\n{message_text}"

    try:
        raw = call_featherless_llm(user_prompt)
        logger.debug("analyze_spare_parts: raw LLM output=%s", raw)
    except Exception as e:
        logger.exception("analyze_spare_parts: Featherless call failed: %s", e)
        return None

    try:
        data = json.loads(raw)
        logger.debug("analyze_spare_parts: parsed JSON=%s", data)
    except json.JSONDecodeError:
        logger.warning("analyze_spare_parts: failed to parse LLM JSON output: %r", raw)
        return None

    is_related = data.get("is_spare_part_related")
    term = data.get("spare_part_term") or None
    reason = data.get("reason") or None

    logger.debug(
        "analyze_spare_parts: is_related=%r, term=%r, reason=%r",
        is_related,
        term,
        reason,
    )

    if not is_related:
        logger.info("analyze_spare_parts: LLM says not spare-part-related")
        return None

    matched_part = None
    if term:
        matched_part = find_best_part_by_term(term)
        logger.debug("analyze_spare_parts: matched_part=%s", matched_part)

    result = {
        "is_spare_related": True,
        "term": term,
        "reason": reason,
        "raw_model_output": raw,
        "matched_part": matched_part,
    }
    logger.debug("analyze_spare_parts: result=%s", result)
    return result
