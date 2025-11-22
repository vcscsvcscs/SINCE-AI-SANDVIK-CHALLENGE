import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

// Teams agent Python service URL - defaults to localhost:3978
const TEAMS_AGENT_URL = (env?.TEAMS_AGENT_URL as string) || 'http://localhost:3978/api/messages';

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

		// Transform the data to MessageActionsPayload format expected by teams-agent
		const messageActionsPayload = {
			id: data.message_id || `msg_${Date.now()}`,
			message_type: 'message',
			created_date_time: data.timestamp || new Date().toISOString(),
			from: {
				user: {
					id: data.user?.id || `user_${data.user?.name || 'unknown'}`,
					display_name: data.user?.name || 'Unknown User',
					user_identity_type: 'aadUser'
				},
				conversation: {
					id: `channel_${data.channel?.toLowerCase().replace(/\s+/g, '-') || 'unknown'}`,
					display_name: data.channel || 'Unknown Channel',
					conversation_identity_type: 'channel'
				}
			},
			body: {
				content_type: 'text',
				content: data.message || ''
			},
			subject: `Message from ${data.channel}`,
			locale: 'en-US'
		};

		// Forward the message to the teams-agent Python service
		let teamsAgentResponse = null;
		try {
			const response = await fetch(TEAMS_AGENT_URL, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(messageActionsPayload)
			});

			if (response.ok) {
				teamsAgentResponse = await response.json();
				console.log('✅ Teams agent response:', teamsAgentResponse);
			} else {
				const errorText = await response.text();
				console.error('❌ Teams agent error:', response.status, errorText);
			}
		} catch (error) {
			console.error('❌ Error forwarding to teams-agent:', error);
			// Continue even if teams-agent is not available
		}

		// Return simple acknowledgment
		return json({
			success: true,
			message: 'Message received and forwarded to teams-agent',
			forwardedToAgent: teamsAgentResponse !== null
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

