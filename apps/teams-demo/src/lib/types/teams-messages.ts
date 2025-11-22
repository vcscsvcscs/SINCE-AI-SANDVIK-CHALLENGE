/**
 * Microsoft Teams Message Types
 * Based on @microsoft/agents-activity MessageActionsPayload
 */

// Your current simplified message format
export interface SimplifiedMessage {
	message_id: string;
	timestamp: string;
	message: string;
	query_type: string;
	referenced_sku: string | null;
	has_typo: boolean;
}

// Microsoft Teams MessageActionsPayload types
export interface MessageActionsPayloadFrom {
	user?: {
		id?: string;
		displayName?: string;
		userPrincipalName?: string;
	};
	application?: {
		id?: string;
		displayName?: string;
	};
}

export interface MessageActionsPayloadBody {
	contentType?: 'html' | 'text';
	content?: string;
}

export interface MessageActionsPayloadAttachment {
	id?: string;
	contentType?: string;
	contentUrl?: string;
	content?: any;
	name?: string;
	thumbnailUrl?: string;
}

export interface MessageActionsPayloadMention {
	id?: number;
	mentionText?: string;
	mentioned?: {
		user?: {
			id?: string;
			displayName?: string;
			userPrincipalName?: string;
		};
	};
}

export interface MessageActionsPayloadReaction {
	reactionType?: string;
	createdDateTime?: string;
	user?: {
		id?: string;
		displayName?: string;
		userPrincipalName?: string;
	};
}

export interface MessageActionsPayload {
	id?: string;
	reply_to_id?: string;
	message_type?: string;
	created_date_time?: string;
	last_modified_date_time?: string;
	deleted?: boolean;
	subject?: string;
	summary?: string;
	importance?: 'normal' | 'high' | 'urgent';
	locale?: string;
	link_to_message?: string;
	from_property?: MessageActionsPayloadFrom;
	body?: MessageActionsPayloadBody;
	attachment_layout?: string;
	attachments?: MessageActionsPayloadAttachment[];
	mentions?: MessageActionsPayloadMention[];
	reactions?: MessageActionsPayloadReaction[];
}

// Union type that can handle both formats
export type TeamMessage = SimplifiedMessage | MessageActionsPayload;

// Type guards to distinguish between the two formats
export function isSimplifiedMessage(message: TeamMessage): message is SimplifiedMessage {
	return 'message_id' in message && 'query_type' in message;
}

export function isMessageActionsPayload(message: TeamMessage): message is MessageActionsPayload {
	return 'id' in message || 'body' in message || 'from_property' in message;
}

// Adapter functions to convert between formats
export function simplifiedToTeamsPayload(
	simplified: SimplifiedMessage
): MessageActionsPayload {
	return {
		id: simplified.message_id,
		created_date_time: simplified.timestamp,
		message_type: 'message',
		body: {
			contentType: 'text',
			content: simplified.message
		},
		importance: 'normal',
		deleted: false,
		// Add SKU reference as metadata in subject if present
		subject: simplified.referenced_sku
			? `Part Query: ${simplified.referenced_sku}`
			: undefined,
		// Store additional metadata in summary as JSON
		summary: JSON.stringify({
			query_type: simplified.query_type,
			referenced_sku: simplified.referenced_sku,
			has_typo: simplified.has_typo
		})
	};
}

export function teamsPayloadToSimplified(
	payload: MessageActionsPayload
): SimplifiedMessage {
	// Try to extract metadata from summary if it exists
	let metadata = {
		query_type: 'general',
		referenced_sku: null as string | null,
		has_typo: false
	};

	if (payload.summary) {
		try {
			const parsed = JSON.parse(payload.summary);
			metadata = { ...metadata, ...parsed };
		} catch (e) {
			// If summary is not JSON, leave defaults
		}
	}

	return {
		message_id: payload.id || `msg_${Date.now()}`,
		timestamp: payload.created_date_time || new Date().toISOString(),
		message: payload.body?.content || '',
		query_type: metadata.query_type,
		referenced_sku: metadata.referenced_sku,
		has_typo: metadata.has_typo
	};
}

// Helper function to extract text content from any message format
export function getMessageText(message: TeamMessage): string {
	if (isSimplifiedMessage(message)) {
		return message.message;
	} else if (message.body?.content) {
		return message.body.content;
	}
	return '';
}

// Helper function to get message ID from any format
export function getMessageId(message: TeamMessage): string {
	if (isSimplifiedMessage(message)) {
		return message.message_id;
	}
	return message.id || '';
}

// Helper function to get timestamp from any format
export function getMessageTimestamp(message: TeamMessage): string {
	if (isSimplifiedMessage(message)) {
		return message.timestamp;
	}
	return message.created_date_time || new Date().toISOString();
}

// Helper function to get sender name from Teams payload
export function getSenderName(message: MessageActionsPayload): string {
	return (
		message.from_property?.user?.displayName ||
		message.from_property?.application?.displayName ||
		'Unknown'
	);
}

// Helper function to extract SKU references from message text
export function extractSkuFromText(text: string): string | null {
	// Match patterns like: SKU 00002771, part no. 00025620, BC00004214, etc.
	const patterns = [
		/\b(?:SKU|sku|part|Part|PART)\s*(?:no\.?|number|#)?\s*([A-Z0-9]{8,})/i,
		/\b([A-Z]{2}[0-9]{8})\b/,
		/\b([0-9]{8})\b/
	];

	for (const pattern of patterns) {
		const match = text.match(pattern);
		if (match) {
			return match[1];
		}
	}
	return null;
}
