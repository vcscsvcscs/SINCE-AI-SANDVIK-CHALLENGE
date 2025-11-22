import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const data = await request.json();
		
		// Log the incoming message
		console.log('Bot received message:', {
			message: data.message,
			message_id: data.message_id,
			channel: data.channel,
			user: data.user,
			timestamp: data.timestamp
		});

		// Here you can process the message and generate a bot response
		// For now, we'll send a simple acknowledgment with an adaptive card
		
		// Example: You can add logic here to:
		// - Analyze the message content
		// - Query a database
		// - Call an AI service
		// - Return a response based on the message

		// Return a response with an adaptive card for the bot conversation
		return json({
			success: true,
			message: 'Message received',
			// Send adaptive card to bot conversation with the administrator
			sendToConversation: 'TestBot', // Name of the bot conversation
			adaptiveCard: {
				title: `Message Received from ${data.channel}`,
				description: `${data.user.name} said: "${data.message}"\n\nChannel: ${data.channel}\nTime: ${new Date(data.timestamp).toLocaleString()}`,
				chatLink: `#${data.channel.toLowerCase().replace(/\s+/g, '-')}`
			}
		});
	} catch (error) {
		console.error('Error processing bot message:', error);
		return json(
			{
				success: false,
				error: 'Failed to process message'
			},
			{ status: 500 }
		);
	}
};

