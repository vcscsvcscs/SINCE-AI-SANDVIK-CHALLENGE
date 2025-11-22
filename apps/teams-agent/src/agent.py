"""FastAPI agent implementation for Teams bot"""
import sys
import traceback
import asyncio
import httpx
from os import environ
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import requests
import pandas as pd
import difflib
import logging
from pathlib import Path


from .models import MessageActionsPayload
from .card_messages import CardMessages

load_dotenv()

# Pre-chosen user ID - set this in environment variable TARGET_USER_ID
TARGET_USER_ID = environ.get("TARGET_USER_ID", "")

# Webhook URL for sending adaptive cards to the frontend
WEBHOOK_URL = environ.get("WEBHOOK_URL", "http://localhost:5175/api/webhook")

LOG_FILE = environ.get("LOG_FILE", "agent.log")
LOG_LEVEL = environ.get("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.DEBUG),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename=LOG_FILE,
    filemode="a",
)
logger = logging.getLogger(__name__)


SPARE_PARTS = [
    {"id": "P-001", "name": "filter"},
    {"id": "P-002", "name": "belt"},
    {"id": "P-003", "name": "bearing"},
]

# Featherless LLM config
FEATHERLESS_API_KEY = environ.get("FEATHERLESS_API_KEY")
FEATHERLESS_MODEL = environ.get(
    "FEATHERLESS_MODEL",
    "Qwen/Qwen2.5-7B-Instruct",  # разумный дефолт
)
FEATHERLESS_API_URL = "https://api.featherless.ai/v1/chat/completions"

# === Load spare parts catalog from CSV (pandas) ===


PROJECT_ROOT = Path(__file__).parent

# SPARE_PARTS_CSV_PATH=test/sku_register_full.csv
CSV_ENV = environ.get("SPARE_PARTS_CSV_PATH", "tests/data/sku_register_full.csv")

csv_path = Path(CSV_ENV)
if not csv_path.is_absolute():
    csv_path = PROJECT_ROOT / csv_path

CATALOG_CSV_PATH = csv_path

try:
    logger.debug("Loading spare parts catalog from %r", str(CATALOG_CSV_PATH))
    CATALOG_DF = pd.read_csv(CATALOG_CSV_PATH)
    logger.info(
        "Spare parts catalog loaded: path=%r, rows=%d, columns=%s",
        str(CATALOG_CSV_PATH),
        len(CATALOG_DF),
        list(CATALOG_DF.columns),
    )
except Exception as e:
    logger.exception(
        "Failed to load spare parts catalog from %r: %s",
        str(CATALOG_CSV_PATH),
        e,
    )
    CATALOG_DF = pd.DataFrame()

# Condition settings - customize these as needed
# Only send notifications if message contains these keywords (empty list = send all messages)
NOTIFICATION_KEYWORDS = environ.get("NOTIFICATION_KEYWORDS", "").split(",") if environ.get("NOTIFICATION_KEYWORDS") else []
# Filter out empty strings
NOTIFICATION_KEYWORDS = [kw.strip().lower() for kw in NOTIFICATION_KEYWORDS if kw.strip()]

# Store conversation references for proactive messaging
# In production, you'd use persistent storage (e.g., CosmosDB, Blob Storage)
conversation_references: Dict[str, Dict[str, Any]] = {}

def _string_similarity(a: str, b: str) -> float:
    """
    Простая строковая similarity на основе difflib.SequenceMatcher.
    Возвращает число от 0 до 1.
    """
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_best_part_by_term(term: str) -> Optional[Dict[str, object]]:
    """
    Looking in CATALOG_DF for a row whose 'name' is most similar to the term.
    Returns a dict with sku, name, score or None if nothing suitable is found.
    """
    logger.debug("find_best_part_by_term: term=%r", term)

    if CATALOG_DF is None or CATALOG_DF.empty:
        logger.warning("find_best_part_by_term: CATALOG_DF is empty or not loaded")
        return None

    if "name" not in CATALOG_DF.columns:
        logger.warning(
            "find_best_part_by_term: 'name' column not found in CATALOG_DF. Columns: %s",
            list(CATALOG_DF.columns),
        )
        return None

    logger.debug(
        "find_best_part_by_term: catalog size=%d, first rows=%s",
        len(CATALOG_DF),
        CATALOG_DF.head().to_dict(orient="records"),
    )

    similarities = CATALOG_DF["name"].astype(str).apply(
        lambda x: _string_similarity(term, x)
    )

    best_idx = similarities.idxmax()
    best_score = float(similarities.loc[best_idx])
    row = CATALOG_DF.loc[best_idx]

    logger.debug(
        "find_best_part_by_term: best_idx=%s, best_name=%r, best_score=%.3f",
        best_idx,
        row.get("name"),
        best_score,
    )

    if best_score < 0.5:
        logger.info(
            "find_best_part_by_term: best_score %.3f below threshold for term=%r",
            best_score,
            term,
        )
        return None

    sku = row.get("sku") if "sku" in CATALOG_DF.columns else None
    name = row.get("name") if "name" in CATALOG_DF.columns else None

    result = {
        "sku": sku,
        "name": name,
        "score": best_score,
    }
    logger.debug("find_best_part_by_term: result=%s", result)
    return result



def call_featherless_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Low-level helper: call Featherless chat completions API and
    return raw assistant message content as string.
    """
    if not FEATHERLESS_API_KEY:
        # Without the key, there's no point in trying
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

    # Take the text of the first response
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
    else:
        spare_part_info = "LLM: message does NOT look spare-part-related."
        
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

    # Notification card sending status
    if TARGET_USER_ID:
        status_text = (
            f"✓ Notification card sent to the configured user about: {message_text}\n"
            f"Deep link: {channel_deep_link}"
        )
    else:
        status_text = "⚠ TARGET_USER_ID not configured. Please set it in environment variables."
    
    response_activity["text"] = status_text + "\n\n" + spare_part_info
    
    return response_activity

    
async def analyze_spare_parts(message_text: str) -> Optional[Dict[str, object]]:
    """
    Step 1: LLM решает, связано ли сообщение с запчастями, и вытаскивает ключевой term.
    Step 2: по этому term ищем лучшую запчасть в CSV каталоге (pandas + similarity).
    """
    logger.debug("analyze_spare_parts: message_text=%r", message_text)

    if not message_text:
        logger.info("analyze_spare_parts: empty message_text, returning None")
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
