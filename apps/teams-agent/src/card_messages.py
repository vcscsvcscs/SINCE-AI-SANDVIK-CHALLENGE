"""Card message utilities for Teams"""
from typing import Optional
from .models import MessageActionsPayload


class CardMessages:
    """Utility class for creating Teams cards and deep links"""

    @staticmethod
    def create_teams_deep_link(payload: MessageActionsPayload) -> Optional[str]:
        """Create a Teams deep link URL to the channel message"""
        try:
            # Extract channel information from payload
            channel_id = None
            team_id = None
            message_id = payload.id
            
            # Try to get channel ID from conversation
            if payload.from_property and payload.from_property.conversation:
                conversation = payload.from_property.conversation
                channel_id = conversation.id
                # Try to extract team ID if available in conversation ID
                if channel_id and "@thread" in channel_id:
                    parts = channel_id.split("@")
                    if len(parts) > 0:
                        # The channel ID is typically the part before @thread
                        channel_id = parts[0].split(":")[-1] if ":" in parts[0] else parts[0]
            
            # Build the Teams deep link
            # Format: https://teams.microsoft.com/l/message/{teamId}/{channelId}/{messageId}
            if team_id and channel_id and message_id:
                deep_link = f"https://teams.microsoft.com/l/message/{team_id}/{channel_id}/{message_id}"
                return deep_link
            elif channel_id and message_id:
                # Fallback without team ID
                deep_link = f"https://teams.microsoft.com/l/message/{channel_id}/{message_id}"
                return deep_link
            else:
                # If we can't build a proper deep link, return None
                return None
        except Exception as e:
            print(f"Error creating Teams deep link: {e}")
            return None

    @staticmethod
    def create_notification_card(
        message_text: Optional[str] = None,
        channel_deep_link: Optional[str] = None,
        sender_name: Optional[str] = None
    ) -> dict:
        """Create a notification card JSON structure"""
        buttons = []
        
        # Add "View in Channel" button if deep link is available
        if channel_deep_link:
            buttons.append({
                "type": "openUrl",
                "title": "View in Channel",
                "value": channel_deep_link,
            })
        else:
            # Fallback button if no deep link
            buttons.append({
                "type": "openUrl",
                "title": "Learn More",
                "value": "https://docs.microsoft.com/en-us/azure/bot-service/",
            })
        
        # Build card text with sender info if available
        card_text = message_text or "You have received a notification from the channel!"
        if sender_name and message_text:
            card_text = f"From {sender_name}: {message_text}"
        
        # Create Hero Card structure
        card = {
            "contentType": "application/vnd.microsoft.card.hero",
            "content": {
                "title": "Channel Notification",
                "text": card_text,
                "images": [
                    {
                        "url": "https://blogs.microsoft.com/wp-content/uploads/prod/2023/09/Press-Image_FINAL_16x9-4.jpg"
                    }
                ],
                "buttons": buttons,
            }
        }
        
        return card
