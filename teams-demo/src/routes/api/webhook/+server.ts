import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// In-memory storage for adaptive cards (in production, use a database or Redis)
interface AdaptiveCard {
	id: string;
	message_id: string;
	timestamp: string;
	channel: string;
	user: {
		name: string;
		id?: string;
	};
	adaptiveCard: {
		title: string;
		description: string;
		chatLink: string;
	};
	sendToConversation: string;
	createdAt: number;
}

const adaptiveCards: AdaptiveCard[] = [];

export const POST: RequestHandler = async ({ request }) => {
	try {
		const data = await request.json();
		
		// Log the incoming webhook request
		console.log('Webhook received:', {
			message: data.message,
			message_id: data.message_id,
			channel: data.channel,
			user: data.user,
			timestamp: data.timestamp
		});

		// Create adaptive card data
		const adaptiveCard: AdaptiveCard = {
			id: `card_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
			message_id: data.message_id || `msg_${Date.now()}`,
			timestamp: data.timestamp || new Date().toISOString(),
			channel: data.channel || 'Unknown Channel',
			user: {
				name: data.user?.name || 'Unknown User',
				id: data.user?.id
			},
			adaptiveCard: {
				title: `Message Received from ${data.channel || 'Unknown Channel'}`,
				description: `${data.user?.name || 'Unknown User'} said: "${data.message}"\n\nChannel: ${data.channel || 'Unknown'}\nTime: ${new Date(data.timestamp || Date.now()).toLocaleString()}`,
				chatLink: `#${(data.channel || 'unknown').toLowerCase().replace(/\s+/g, '-')}`
			},
			sendToConversation: 'TestBot',
			createdAt: Date.now()
		};

		// Store the adaptive card
		adaptiveCards.push(adaptiveCard);
		
		// Keep only the last 100 cards to prevent memory issues
		if (adaptiveCards.length > 100) {
			adaptiveCards.shift();
		}

		console.log('✅ Adaptive card stored:', adaptiveCard.id);

		// Return success response
		return json({
			success: true,
			message: 'Adaptive card received and stored',
			cardId: adaptiveCard.id
		});
	} catch (error) {
		console.error('Error processing webhook:', error);
		return json(
			{
				success: false,
				error: 'Failed to process webhook'
			},
			{ status: 500 }
		);
	}
};

export const GET: RequestHandler = async ({ url }) => {
	try {
		const since = url.searchParams.get('since');
		const sinceTimestamp = since ? parseInt(since, 10) : 0;

		// Filter cards created after the 'since' timestamp
		const newCards = adaptiveCards.filter(card => card.createdAt > sinceTimestamp);

		return json({
			success: true,
			cards: newCards,
			count: newCards.length,
			latestTimestamp: adaptiveCards.length > 0 
				? Math.max(...adaptiveCards.map(c => c.createdAt))
				: Date.now()
		});
	} catch (error) {
		console.error('Error fetching adaptive cards:', error);
		return json(
			{
				success: false,
				error: 'Failed to fetch adaptive cards'
			},
			{ status: 500 }
		);
	}
};

