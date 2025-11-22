"""FastAPI agent implementation for Teams bot"""
import sys
import traceback
from os import environ
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import requests

from .models import MessageActionsPayload
from .card_messages import CardMessages

load_dotenv()

# Pre-chosen user ID - set this in environment variable TARGET_USER_ID
TARGET_USER_ID = environ.get("TARGET_USER_ID", "")

SPARE_PARTS = [
    {"id": "P-001", "name": "filter"},
    {"id": "P-002", "name": "belt"},
    {"id": "P-003", "name": "bearing"},
]

# Featherless LLM config
FEATHERLESS_API_KEY = environ.get("FEATHERLESS_API_KEY")
FEATHERLESS_MODEL = environ.get(
    "FEATHERLESS_MODEL",
    "meta-llama/Meta-Llama-3.1-8B-Instruct",  # разумный дефолт
)
FEATHERLESS_API_URL = "https://api.featherless.ai/v1/chat/completions"

# Condition settings - customize these as needed
# Only send notifications if message contains these keywords (empty list = send all messages)
NOTIFICATION_KEYWORDS = environ.get("NOTIFICATION_KEYWORDS", "").split(",") if environ.get("NOTIFICATION_KEYWORDS") else []
# Filter out empty strings
NOTIFICATION_KEYWORDS = [kw.strip().lower() for kw in NOTIFICATION_KEYWORDS if kw.strip()]

# Store conversation references for proactive messaging
# In production, you'd use persistent storage (e.g., CosmosDB, Blob Storage)
conversation_references: Dict[str, Dict[str, Any]] = {}

def call_featherless_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Low-level helper: call Featherless chat completions API and
    return raw assistant message content as string.
    """
    if not FEATHERLESS_API_KEY:
        # Без ключа нет смысла пытаться
        raise RuntimeError("FEATHERLESS_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {FEATHERLESS_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": FEATHERLESS_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    response = requests.post(
        FEATHERLESS_API_URL,
        headers=headers,
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    # Берём текст первого ответа
    return data["choices"][0]["message"]["content"]


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
        term = spare_part_match.get("term") or "<no term>"
        reason = spare_part_match.get("reason") or ""
        spare_part_info = f"LLM: message looks spare-part-related. Term: {term}."
        if reason:
            spare_part_info += f" Reason: {reason}"
    else:
        spare_part_info = "LLM: message does NOT look spare-part-related."

    # 2) create deep link (not used yet, but let's keep it for future)
    channel_deep_link = CardMessages.create_teams_deep_link(payload)
    
    # Send card to pre-chosen user (in a real implementation, you'd send this via Teams API)
    if TARGET_USER_ID:
        status_text = f"✓ Notification card sent to the configured user about: {message_text}"
    else:
        status_text = "⚠ TARGET_USER_ID not configured. Please set it in environment variables."

    response_activity["text"] = status_text + "\n\n" + spare_part_info
        
    return response_activity
    
async def analyze_spare_parts(message_text: str) -> Optional[Dict[str, object]]:
    """
    Step 1: use LLM (Featherless) to decide whether the message
    is related to spare parts, and if so, extract the key term/phrase.

    Returns:
        None, if the query is not about spare parts
        dict with fields:
            - is_spare_related: bool (always True here)
            - term: str | None (extracted word/phrase)
            - reason: str | None (model explanation)
            - raw_model_output: str (just in case, for debugging)
    """

    if not message_text:
        return None

    system_prompt = (
        "You are a classifier for a mining equipment spare parts support chat.\n"
        "Your job:\n"
        "1) Decide if the customer message is about a SPARE PART (part, tire, hose, mirror, transmission, etc.).\n"
        "2) If yes, extract the ONE most important term or phrase that names the part.\n\n"
        "Respond ONLY in JSON with the following keys:\n"
        "{\n"
        '  \"is_spare_part_related\": true/false,\n'
        '  \"spare_part_term\": string or null,\n'
        '  \"reason\": string (very short explanation)\n'
        "}\n"
        "Do not add any extra text, only JSON."
    )

    user_prompt = f"Customer message:\n{message_text}"

    try:
        raw = call_featherless_llm(system_prompt, user_prompt)
    except Exception as e:
        # At this step, it's better not to fail, but simply say "nothing found"
        # + you can log e if you already have logging
        return None

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # model responded with invalid JSON
        return None

    is_related = data.get("is_spare_part_related")
    if not is_related:
        return None

    term = data.get("spare_part_term") or None
    reason = data.get("reason") or None

    return {
        "is_spare_related": True,
        "term": term,
        "reason": reason,
        "raw_model_output": raw,
    }
