# Teams Message Format Support

This application supports **two message formats**:

1. **Simplified Format** - Your current test data format
2. **Microsoft Teams MessageActionsPayload** - Full Teams message format

## You Don't Need to Change Your JSON Files! 🎉

Your existing JSON files in the test folder can stay as they are. The application includes adapter functions to convert between formats automatically.

## Message Formats

### 1. Simplified Message Format (Current Test Data)

```json
{
  "message_id": "msg_001",
  "timestamp": "2025-11-20T09:15:23Z",
  "message": "Need replacement part for SKU 00002771",
  "query_type": "replacement_availability",
  "referenced_sku": "00002771",
  "has_typo": false
}
```

### 2. Microsoft Teams MessageActionsPayload Format

```json
{
  "id": "msg_001",
  "created_date_time": "2025-11-20T09:15:23Z",
  "message_type": "message",
  "body": {
    "contentType": "text",
    "content": "Need replacement part for SKU 00002771"
  },
  "from_property": {
    "user": {
      "id": "user123",
      "displayName": "John Doe",
      "userPrincipalName": "john.doe@example.com"
    }
  },
  "importance": "normal",
  "attachments": [],
  "mentions": [],
  "reactions": []
}
```

## Usage in Code

### Import the Types and Helpers

```typescript
import {
  type SimplifiedMessage,
  type MessageActionsPayload,
  type TeamMessage,
  isSimplifiedMessage,
  isMessageActionsPayload,
  simplifiedToTeamsPayload,
  teamsPayloadToSimplified,
  getMessageText,
  getMessageId,
  getMessageTimestamp,
  getSenderName,
  extractSkuFromText
} from '$lib/types/teams-messages';
```

### Handle Both Formats

```typescript
// Your messages can be either format
let messages: TeamMessage[] = [];

// Load simplified format (your current test data)
const response = await fetch('/synthetic-data_EN.json');
const data = await response.json();
messages = data; // Works directly

// OR load from Teams (real MessageActionsPayload)
// messages = teamsData; // Also works!

// Use helper functions to extract data regardless of format
messages.forEach(msg => {
  const text = getMessageText(msg);
  const id = getMessageId(msg);
  const timestamp = getMessageTimestamp(msg);
  
  console.log(`${id}: ${text}`);
});
```

### Convert Between Formats

```typescript
// Convert simplified to Teams format
const simplified: SimplifiedMessage = {
  message_id: "msg_001",
  timestamp: "2025-11-20T09:15:23Z",
  message: "Need part 00002771",
  query_type: "general",
  referenced_sku: "00002771",
  has_typo: false
};

const teamsFormat = simplifiedToTeamsPayload(simplified);
// Now you can send teamsFormat to Microsoft Teams APIs

// Convert Teams format back to simplified
const backToSimplified = teamsPayloadToSimplified(teamsFormat);
```

### Type Guards

```typescript
function processMessage(message: TeamMessage) {
  if (isSimplifiedMessage(message)) {
    // TypeScript knows this is SimplifiedMessage
    console.log(message.query_type);
    console.log(message.referenced_sku);
  } else if (isMessageActionsPayload(message)) {
    // TypeScript knows this is MessageActionsPayload
    console.log(message.importance);
    console.log(message.from_property?.user?.displayName);
  }
}
```

### Extract SKU from Any Text

```typescript
const text = "Need part 00002771 urgently";
const sku = extractSkuFromText(text); // "00002771"

const text2 = "BC00004214 is out of stock";
const sku2 = extractSkuFromText(text2); // "BC00004214"
```

## Complete Example

```typescript
<script lang="ts">
  import { onMount } from 'svelte';
  import type { TeamMessage } from '$lib/types/teams-messages';
  import { 
    getMessageText, 
    getMessageId, 
    getMessageTimestamp 
  } from '$lib/types/teams-messages';
  
  let messages: TeamMessage[] = [];
  
  onMount(async () => {
    // Load your existing test data - no changes needed!
    const response = await fetch('/synthetic-data_EN.json');
    const data = await response.json();
    messages = data;
  });
  
  function displayMessage(msg: TeamMessage) {
    return {
      id: getMessageId(msg),
      text: getMessageText(msg),
      time: formatTime(getMessageTimestamp(msg))
    };
  }
</script>

{#each messages as message}
  {@const display = displayMessage(message)}
  <div>
    <strong>{display.id}</strong>: {display.text}
    <small>{display.time}</small>
  </div>
{/each}
```

## Benefits

✅ **No JSON file changes required** - Keep your existing test data  
✅ **Type-safe** - Full TypeScript support for both formats  
✅ **Flexible** - Easily work with both simplified and full Teams messages  
✅ **Helper functions** - Extract common data regardless of format  
✅ **Future-proof** - Ready for real Teams integration  

## When to Use Which Format

- **Simplified Format**: For testing, demos, and internal tools
- **Teams MessageActionsPayload**: When integrating with actual Microsoft Teams Bot Framework

The adapter functions make it seamless to switch between them!

