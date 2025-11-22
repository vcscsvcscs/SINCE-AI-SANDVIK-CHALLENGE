from microsoft_agents.activity import ActionTypes, Activity, ActivityTypes, Attachment
from microsoft_agents.hosting.core import CardFactory, TurnContext
from microsoft_agents.activity import (
    HeroCard,
    CardAction,
    CardImage,
)


class CardMessages:

    @staticmethod
    def create_teams_deep_link(activity: Activity) -> str:
        """Create a Teams deep link URL to the channel message"""
        try:
            # Extract channel information from activity
            channel_id = None
            team_id = None
            message_id = activity.id
            
            # Try to get channel ID from channel_data (Teams specific)
            if activity.channel_data and isinstance(activity.channel_data, dict):
                channel_info = activity.channel_data.get("channel", {})
                channel_id = channel_info.get("id")
                team_info = activity.channel_data.get("team", {})
                team_id = team_info.get("id")
            
            # Fallback: try to extract from conversation ID
            # Teams conversation IDs are in format: 19:xxx@thread.tacv2 or 19:xxx_xxx@thread.skype
            if not channel_id and activity.conversation:
                conv_id = activity.conversation.id
                # Extract channel ID from conversation ID if possible
                if "@thread" in conv_id:
                    parts = conv_id.split("@")
                    if len(parts) > 0:
                        # The channel ID is typically the part before @thread
                        channel_id = parts[0].split(":")[-1] if ":" in parts[0] else parts[0]
            
            # Build the Teams deep link
            # Format: https://teams.microsoft.com/l/message/{teamId}/{channelId}/{messageId}
            if team_id and channel_id and message_id:
                # Encode the IDs properly for URL
                tenant_id = ""
                if activity.channel_data and isinstance(activity.channel_data, dict):
                    tenant_id = activity.channel_data.get('tenant', {}).get('id', '') if isinstance(activity.channel_data.get('tenant'), dict) else ''
                deep_link = f"https://teams.microsoft.com/l/message/{team_id}/{channel_id}/{message_id}"
                if tenant_id:
                    deep_link += f"?tenantId={tenant_id}"
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
    async def send_notification_card(
        context: TurnContext, 
        message_text: str = None, 
        channel_deep_link: str = None,
        sender_name: str = None
    ):
        """Send a notification card to a user"""
        buttons = []
        
        # Add "View in Channel" button if deep link is available
        if channel_deep_link:
            buttons.append(
                CardAction(
                    type=ActionTypes.open_url,
                    title="View in Channel",
                    value=channel_deep_link,
                )
            )
        else:
            # Fallback button if no deep link
            buttons.append(
                CardAction(
                    type=ActionTypes.open_url,
                    title="Learn More",
                    value="https://docs.microsoft.com/en-us/azure/bot-service/",
                )
            )
        
        # Build card text with sender info if available
        card_text = message_text or "You have received a notification from the channel!"
        if sender_name and message_text:
            card_text = f"From {sender_name}: {message_text}"
        
        card = CardFactory.hero_card(
            HeroCard(
                title="Channel Notification",
                text=card_text,
                images=[
                    CardImage(
                        url="https://blogs.microsoft.com/wp-content/uploads/prod/2023/09/Press-Image_FINAL_16x9-4.jpg"
                    )
                ],
                buttons=buttons,
            )
        )
        await CardMessages.send_activity(context, card)

    @staticmethod
    async def send_activity(context: TurnContext, card: Attachment):
        activity = Activity(type=ActivityTypes.message, attachments=[card])
        await context.send_activity(activity)

