# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
import traceback
from os import environ
from dotenv import load_dotenv

from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.hosting.core import (
    Authorization,
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.activity import load_configuration_from_env
from microsoft_agents.activity import ConversationReference, Activity

from .card_messages import CardMessages

load_dotenv()
agents_sdk_config = load_configuration_from_env(environ)

STORAGE = MemoryStorage()
# Connection manager is optional - CloudAdapter can work without it
# If you need MSAL authentication, you'll need to install/configure it separately
ADAPTER = CloudAdapter(connection_manager=None)
AUTHORIZATION = Authorization(STORAGE, None, **agents_sdk_config)

AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE, adapter=ADAPTER, authorization=AUTHORIZATION, **agents_sdk_config
)

# Pre-chosen user ID - set this in environment variable TARGET_USER_ID
TARGET_USER_ID = environ.get("TARGET_USER_ID", "")

# Condition settings - customize these as needed
# Only send notifications if message contains these keywords (empty list = send all messages)
NOTIFICATION_KEYWORDS = environ.get("NOTIFICATION_KEYWORDS", "").split(",") if environ.get("NOTIFICATION_KEYWORDS") else []
# Filter out empty strings
NOTIFICATION_KEYWORDS = [kw.strip().lower() for kw in NOTIFICATION_KEYWORDS if kw.strip()]

# Store conversation references for proactive messaging
# In production, you'd use persistent storage (e.g., CosmosDB, Blob Storage)
conversation_references = {}


def get_conversation_reference(activity):
    """Extract conversation reference from activity"""
    return ConversationReference(
        activity_id=activity.id,
        user=activity.from_property,
        bot=activity.recipient,
        conversation=activity.conversation,
        channel_id=activity.channel_id,
        service_url=activity.service_url,
    )


def should_send_notification(activity) -> bool:
    """Check if notification should be sent based on conditions"""
    # Condition 1: Message must not be empty
    if not activity.text or not activity.text.strip():
        return False
    
    # Condition 2: Message must not be from the bot itself
    if activity.from_property and activity.recipient:
        if activity.from_property.id == activity.recipient.id:
            return False
    
    # Condition 3: If keywords are configured, message must contain at least one keyword
    if NOTIFICATION_KEYWORDS:
        message_lower = activity.text.lower()
        if not any(keyword in message_lower for keyword in NOTIFICATION_KEYWORDS):
            return False
    
    return True


async def send_card_to_user(
    adapter: CloudAdapter, 
    user_id: str, 
    message_text: str = None,
    channel_deep_link: str = None,
    sender_name: str = None
):
    """Send a card to a specific user using stored conversation reference"""
    try:
        # Get stored conversation reference for the user
        conversation_ref = conversation_references.get(user_id)
        
        if not conversation_ref:
            print(f"Warning: No conversation reference found for user {user_id}. "
                  f"The user needs to send a message to the bot first.", file=sys.stderr)
            return False
        
        # Use the adapter to continue the conversation and send the card
        async def send_card_callback(turn_context: TurnContext):
            await CardMessages.send_notification_card(
                turn_context, 
                message_text, 
                channel_deep_link,
                sender_name
            )
        
        await adapter.continue_conversation(
            conversation_ref,
            send_card_callback,
        )
        return True
    except Exception as e:
        print(f"Error sending card to user: {e}", file=sys.stderr)
        traceback.print_exc()
        return False


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    """Handle messages received in a channel"""
    # Store conversation reference for the user who sent the message
    # This allows us to send proactive messages later
    user_id = context.activity.from_property.id if context.activity.from_property else None
    if user_id:
        conversation_ref = get_conversation_reference(context.activity)
        conversation_references[user_id] = conversation_ref
    
    # Check if message is from a channel (not a direct message)
    # In Teams, channel messages have channelData with channel info
    is_channel_message = (
        context.activity.channel_data 
        and isinstance(context.activity.channel_data, dict)
        and context.activity.channel_data.get("channel", {}).get("id")
    ) or (
        context.activity.conversation 
        and context.activity.conversation.conversation_type == "channel"
    )
    
    if is_channel_message:
        # Check condition before sending notification
        if not should_send_notification(context.activity):
            # Conditions not met, skip sending notification
            return
        
        # This is a channel message
        message_text = context.activity.text or "A message was received in the channel"
        sender_name = context.activity.from_property.name if context.activity.from_property else "Someone"
        
        # Create Teams deep link to the channel message
        channel_deep_link = CardMessages.create_teams_deep_link(context.activity)
        
        # Send card to pre-chosen user
        if TARGET_USER_ID:
            success = await send_card_to_user(
                ADAPTER,
                TARGET_USER_ID,
                message_text,
                channel_deep_link,
                sender_name
            )
            # Acknowledge in the channel
            if success:
                await context.send_activity(
                    f"✓ Notification card sent to the configured user about: {message_text}"
                )
            else:
                await context.send_activity(
                    f"⚠ Could not send notification. User {TARGET_USER_ID} needs to send a message to the bot first."
                )
        else:
            await context.send_activity(
                "⚠ TARGET_USER_ID not configured. Please set it in environment variables."
            )
    else:
        # Direct message - store reference and provide info
        if user_id == TARGET_USER_ID:
            await context.send_activity(
                "Hello! I've registered you as the notification recipient. "
                "I'll send you cards when messages are received in channels."
            )
        else:
            await context.send_activity(
                f"You said: {context.activity.text}\n\n"
                f"Note: This bot sends notification cards to user {TARGET_USER_ID} "
                f"when messages are received in channels."
            )


@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, _state: TurnState):
    """Welcome message when bot is added to a conversation"""
    await context.send_activity(
        "Hello! I'm a bot that sends notification cards to a pre-chosen user "
        "when messages are received in channels."
    )
    return True


@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    """Handle errors"""
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The bot encountered an error or bug.")

