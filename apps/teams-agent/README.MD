# Teams Agent - Channel Message Notifier

This Teams bot listens for messages in channels and sends notification cards to a pre-configured user.

## Features

- Listens for messages in Teams channels
- Sends notification cards to a pre-chosen user when channel messages are received
- **Deep links to original channel messages** - Cards include a "View in Channel" button that opens the message directly in Teams
- **Conditional notifications** - Only sends notifications when conditions are met:
  - Message is not empty
  - Message is not from the bot itself
  - Optional keyword filtering (configurable)
- Stores conversation references for proactive messaging
- Uses Microsoft Agents SDK for Python

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Copy `env.TEMPLATE` to `.env` (or set environment variables)
   - Fill in your Azure AD app registration details:
     - `CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID`
     - `CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET`
     - `CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID`
   - Set the target user ID:
     - `TARGET_USER_ID` - The Azure AD Object ID of the user who should receive notification cards

3. **Run the application:**
   ```bash
   python app.py
   ```

   Or using Docker:
   ```bash
   docker build -t teams-agent .
   docker run -p 3978:3978 --env-file .env teams-agent
   ```

## How It Works

1. **Initial Setup:** The target user must send at least one message to the bot (via direct message) to establish a conversation reference. This allows the bot to send proactive messages later.

2. **Channel Monitoring:** When a message is posted in any channel where the bot is present, the bot:
   - Detects it's a channel message
   - **Checks conditions** - Only proceeds if message meets criteria (not empty, not from bot, matches keywords if configured)
   - Extracts the message content and sender information
   - Creates a Teams deep link to the original message
   - Sends a notification card to the pre-configured user
   - Acknowledges the action in the channel

3. **Notification Cards:** The cards include:
   - Title: "Channel Notification"
   - Message: The channel message content and sender name
   - Image: Microsoft branding image
   - **"View in Channel" button**: Deep link that opens the original message directly in Teams

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── agent.py          # Main agent logic
│   ├── card_messages.py  # Card creation and sending
│   ├── main.py          # Application entry point
│   └── start_server.py   # HTTP server setup
├── app.py               # Root entry point
├── requirements.txt     # Python dependencies
├── env.TEMPLATE        # Environment variable template
├── DOCKERFILE          # Docker configuration
└── README.md           # This file
```

## Configuration

### Required Environment Variables

- `CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID` - Azure AD App Client ID
- `CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET` - Azure AD App Client Secret
- `CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID` - Azure AD Tenant ID
- `TARGET_USER_ID` - Azure AD Object ID of the user to receive notifications

### Optional Environment Variables

- `PORT` - Server port (default: 3978)
- `TARGET_USER_TENANT_ID` - Tenant ID for target user (usually same as TENANTID)
- `BOT_ID` - Bot ID (usually auto-detected)
- `SERVICE_URL` - Service URL (usually auto-detected)
- `NOTIFICATION_KEYWORDS` - Comma-separated list of keywords. Only messages containing at least one keyword will trigger notifications. Leave empty to send notifications for all messages.
  - Example: `NOTIFICATION_KEYWORDS=urgent,important,help`
  - Example: `NOTIFICATION_KEYWORDS=` (empty = send all messages)

## Notification Conditions

The bot only sends notifications when all of the following conditions are met:

1. **Message is not empty** - Empty messages are ignored
2. **Message is not from the bot** - Prevents notification loops
3. **Keyword filtering (optional)** - If `NOTIFICATION_KEYWORDS` is configured, the message must contain at least one of the specified keywords (case-insensitive)

## Notes

- The bot stores conversation references in memory. In production, consider using persistent storage (CosmosDB, Blob Storage) for conversation references.
- The target user must interact with the bot at least once (send a direct message) before they can receive proactive notifications.
- Channel messages are detected by checking `channel_data` or `conversation_type`.
- Deep links to channel messages require proper channel and team IDs from the activity. If these cannot be extracted, the card will include a fallback button instead.

## Troubleshooting

- **"No conversation reference found"**: The target user needs to send a direct message to the bot first.
- **"TARGET_USER_ID not configured"**: Make sure you've set the `TARGET_USER_ID` environment variable.
- **Authentication errors**: Verify your Azure AD app registration credentials are correct.

