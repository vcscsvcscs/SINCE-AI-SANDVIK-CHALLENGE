<script lang="ts">
	import { onMount } from 'svelte';
	import UserSelection from '$lib/components/UserSelection.svelte';
	import ChatView from '$lib/components/ChatView.svelte';
	import CallsView from '$lib/components/CallsView.svelte';
	import FilesView from '$lib/components/FilesView.svelte';
	import TeamsView from '$lib/components/TeamsView.svelte';
	import CalendarView from '$lib/components/CalendarView.svelte';
	import ActivityView from '$lib/components/ActivityView.svelte';
	import {
		getMessageText,
		getMessageId,
		getMessageTimestamp,
		isSimplifiedMessage
	} from '$lib/types';

	// User management
	let currentUser: any = null;
	let showUserSelection = true;

	// Store messages per channel
	let channelMessages: Record<string, any[]> = {
		'General': [],
		'Parts Support': [],
		'Technical Help': [],
		'Warehouse': []
	};

	// Current messages for the selected channel
	$: messages = channelMessages[selectedChannel] || [];

	let currentView = 'chat';
	let selectedChannel = 'Parts Support';
	let selectedChat = 'Ray Tanaka'; // Default - will be set based on user role
	let messageInput = '';
	let chatMessages: any[] = [];

	// Chat conversations list - dynamic based on user
	$: conversations = currentUser?.role === 'Administrator' 
		? [
				{
					id: 1,
					name: 'TestBot',
					initials: 'TB',
					color: 'bg-purple-600',
					lastMessage: conversationMessages['TestBot']?.length > 0 
						? conversationMessages['TestBot'][conversationMessages['TestBot'].length - 1]?.card?.title || 'Bot notifications here'
						: 'Bot notifications here',
					timestamp: conversationMessages['TestBot']?.length > 0
						? conversationMessages['TestBot'][conversationMessages['TestBot'].length - 1]?.timestamp || '11:44 AM'
						: '11:44 AM',
					online: true,
					unread: 0,
					isBot: true
				},
				{
					id: 2,
					name: 'Ray Tanaka',
					initials: 'RT',
					color: 'bg-blue-600',
					lastMessage: 'Louisa will send the initial list of...',
					timestamp: '1:47 PM',
					online: true,
					unread: 0
				},
		  ]
		: [
				{
					id: 2,
					name: 'Ray Tanaka',
					initials: 'RT',
					color: 'bg-blue-600',
					lastMessage: 'Louisa will send the initial list of...',
					timestamp: '1:47 PM',
					online: true,
					unread: 0
				},
		  ];
	
	// Auto-switch to valid conversation if current selection is not available for this user
	$: if (currentUser && conversations.length > 0) {
		const isCurrentChatAvailable = conversations.some(conv => conv.name === selectedChat);
		if (!isCurrentChatAvailable) {
			// Selected chat not available for this user, switch to first available
			console.log('⚠️ Selected chat', selectedChat, 'not available for', currentUser.role, '- switching to', conversations[0].name);
			selectedChat = conversations[0].name;
		}
	}

	// Store messages per conversation
	let conversationMessages: Record<string, any[]> = {
		'TestBot': [], // Empty - will be populated with bot notifications
		'Ray Tanaka': [
			{
				id: 1,
				sender: 'user',
				name: 'Ray Tanaka',
				initials: 'RT',
				color: 'bg-blue-600',
				text: 'Hi, can you help me with the project timeline?',
				timestamp: '1:30 PM',
				reactions: []
			},
			{
				id: 2,
				sender: 'user',
				name: 'You',
				initials: 'ME',
				color: 'bg-blue-600',
				text: 'Sure! What do you need?',
				timestamp: '1:32 PM',
				reactions: []
			},
			{
				id: 3,
				sender: 'user',
				name: 'Ray Tanaka',
				initials: 'RT',
				color: 'bg-blue-600',
				text: 'Louisa will send the initial list of requirements tomorrow.',
				timestamp: '1:47 PM',
				reactions: []
			}
		]
	};

	// Debug: Log when conversationMessages changes
	$: console.log('🔄 conversationMessages updated. TestBot has:', (conversationMessages['TestBot'] || []).length, 'messages');
	
	// Current chat messages - updates when selectedChat or conversationMessages changes
	$: {
		const messages = conversationMessages[selectedChat] || [];
		chatMessages = messages;
		console.log('📋 Selected chat:', selectedChat, '| Messages:', messages.length);
		if (selectedChat === 'TestBot' && messages.length > 0) {
			console.log('✅ TestBot messages:', messages);
		}
	}

	// Teams data
	const teams = [
		{ name: 'Sandvik Support', initials: 'SS', color: 'bg-blue-600' },
	];

	function handleUserSelected(event: CustomEvent) {
		currentUser = event.detail.user;
		showUserSelection = false;
		
		// Set default chat based on user role
		if (currentUser.role === 'Administrator') {
			selectedChat = 'TestBot'; // Admin can see TestBot
		} else {
			selectedChat = 'Ray Tanaka'; // Regular users default to Ray Tanaka
		}
		
		// Load messages from localStorage when user logs in
		loadMessagesFromStorage();
	}

	function loadMessagesFromStorage() {
		const stored = localStorage.getItem('teamChannelMessages');
		if (stored) {
			try {
				channelMessages = JSON.parse(stored);
			} catch (e) {
				channelMessages = {
					'General': [],
					'Parts Support': [],
					'Technical Help': [],
					'Warehouse': []
				};
			}
		}
	}

	function saveMessagesToStorage() {
		localStorage.setItem('teamChannelMessages', JSON.stringify(channelMessages));
		// Dispatch storage event for other windows
		window.dispatchEvent(new StorageEvent('storage', {
			key: 'teamChannelMessages',
			newValue: JSON.stringify(channelMessages)
		}));
	}

	onMount(async () => {
		// Listen for storage changes from other windows
		window.addEventListener('storage', (e) => {
			if (e.key === 'teamChannelMessages' && e.newValue) {
				try {
					channelMessages = JSON.parse(e.newValue);
				} catch (err) {
					console.error('Error parsing messages:', err);
				}
			}
		});
	});

	// Bot endpoint configuration - defaults to local API endpoint
	const BOT_ENDPOINT = '/api/bot';

	async function notifyBot(message: any, channel: string) {
		try {
			const response = await fetch(BOT_ENDPOINT, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					message: message.message,
					message_id: message.message_id,
					timestamp: message.timestamp,
					channel: channel,
					user: {
						name: message.from.displayName,
						initials: message.from.initials,
						role: currentUser.role
					}
				})
			});

			if (response.ok) {
				const botResponse = await response.json();
				console.log('✅ Bot response received:', botResponse);
				
				// If bot sends an adaptive card, add it to the specified conversation
				if (botResponse.adaptiveCard && botResponse.sendToConversation) {
					const conversationName = botResponse.sendToConversation;
					console.log('📝 Target conversation:', conversationName);
					
					const currentMessages = conversationMessages[conversationName] || [];
					console.log('📨 Current messages in', conversationName, ':', currentMessages.length);
					
					const botMessage = {
						id: currentMessages.length + 1,
						sender: 'bot',
						name: 'TestBot',
						initials: 'TB',
						color: 'bg-purple-600',
						timestamp: new Date().toLocaleTimeString('en-US', {
							hour: '2-digit',
							minute: '2-digit'
						}),
						reactions: [],
						card: {
							title: botResponse.adaptiveCard.title,
							description: botResponse.adaptiveCard.description,
							chatLink: botResponse.adaptiveCard.chatLink
						}
					};

					console.log('🤖 Bot message created:', botMessage);

					// Add to the conversation (e.g., TestBot conversation with admin)
					conversationMessages = {
						...conversationMessages,
						[conversationName]: [...currentMessages, botMessage]
					};
					
					console.log('✅ Updated conversationMessages:', conversationMessages);
					console.log('✅ TestBot messages now:', conversationMessages['TestBot'].length);
				} else {
					console.log('⚠️ No adaptive card in bot response or missing sendToConversation');
				}
			} else {
				console.error('❌ Bot API returned error:', response.status, await response.text());
			}
		} catch (error) {
			console.error('Error notifying bot:', error);
			// Bot is not available, continue without it
		}
	}

	function sendMessage() {
		if (messageInput.trim() && currentUser) {
			// Create message with current user info
			const newMessage: any = {
				message_id: `msg_${Date.now()}`,
				timestamp: new Date().toISOString(),
				message: messageInput,
				query_type: 'user_message',
				referenced_sku: null,
				has_typo: false,
				from: {
					displayName: currentUser.name,
					initials: currentUser.initials,
					color: currentUser.color
				}
			};
			
			// Add message to the current channel
			const currentMessages = channelMessages[selectedChannel] || [];
			channelMessages = {
				...channelMessages,
				[selectedChannel]: [...currentMessages, newMessage]
			};
			
			saveMessagesToStorage();
			messageInput = '';

			// Notify the bot about the new message
			notifyBot(newMessage, selectedChannel);
		}
	}

	function handleChatMessage(event: CustomEvent) {
		const messageInput = event.detail.message;
		const currentMessages = conversationMessages[selectedChat] || [];
		
		// Add user message to the current conversation
		const userMessage = {
			id: currentMessages.length + 1,
			sender: 'user',
			name: 'You',
			initials: 'ME',
			color: 'bg-blue-600',
			text: messageInput,
			timestamp: new Date().toLocaleTimeString('en-US', {
				hour: '2-digit',
				minute: '2-digit'
			}),
			reactions: []
		};
		
		conversationMessages = {
			...conversationMessages,
			[selectedChat]: [...currentMessages, userMessage]
		};

		// Only simulate bot response if chatting with a bot
		const currentConversation = conversations.find(c => c.name === selectedChat);
		if (currentConversation?.isBot) {
			setTimeout(() => {
				const responses = [
					{
						title: 'Information Found',
						description:
							'I found that information for you! Here are the details. This information is current as of today and includes availability, pricing, and compatibility information.',
						chatLink: '#parts-support-channel'
					},
					{
						title: 'Processing Your Request',
						description:
							'Let me check that for you... I am searching through our database for the most relevant information. This may take a moment.',
						chatLink: '#technical-help-channel'
					},
					{
						title: 'Parts Available',
						description:
							'Great news! The parts you requested are available in stock. Lead time is 2-3 business days. Click to view more details in the channel.',
						chatLink: '#parts-warehouse-channel'
					}
				];

				const response = responses[Math.floor(Math.random() * responses.length)];
				const updatedMessages = conversationMessages[selectedChat] || [];

				conversationMessages = {
					...conversationMessages,
					[selectedChat]: [...updatedMessages, {
						id: updatedMessages.length + 1,
						sender: 'bot',
						name: 'TestBot',
						initials: 'TB',
						color: 'bg-purple-600',
						timestamp: new Date().toLocaleTimeString('en-US', {
							hour: '2-digit',
							minute: '2-digit'
						}),
						reactions: [],
						card: {
							title: response.title,
							description: response.description,
							chatLink: response.chatLink
						}
					}]
				};
			}, 1000);
		}
	}

	function handleCloseCard(event: CustomEvent) {
		const messageId = event.detail.messageId;
		// Remove the message with the specified ID from the current conversation
		if (conversationMessages[selectedChat]) {
			conversationMessages = {
				...conversationMessages,
				[selectedChat]: conversationMessages[selectedChat].filter((msg) => msg.id !== messageId)
			};
		}
	}

	function handleGoToChat(event: CustomEvent) {
		const chatLink = event.detail.chatLink;
		// Navigate to the channel based on the chatLink
		if (chatLink.includes('parts-support')) {
			currentView = 'chat';
			selectedChannel = 'Parts Support';
		} else if (chatLink.includes('technical-help')) {
			currentView = 'chat';
			selectedChannel = 'Technical Help';
		} else if (chatLink.includes('parts-warehouse')) {
			currentView = 'chat';
			selectedChannel = 'Warehouse';
		}
	}

	function handleSelectChat(event: CustomEvent) {
		selectedChat = event.detail.name;
		// Initialize empty messages array if conversation doesn't exist
		if (!conversationMessages[selectedChat]) {
			conversationMessages = {
				...conversationMessages,
				[selectedChat]: []
			};
		}
	}

	function handleSelectTeam(event: CustomEvent) {
		currentView = 'chat';
		selectedChannel = event.detail.teamName;
	}

	function formatTime(timestamp: string) {
		const date = new Date(timestamp);
		return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
	}

	function formatDate(timestamp: string) {
		const date = new Date(timestamp);
		return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
	}
</script>

{#if showUserSelection}
	<UserSelection on:userSelected={handleUserSelected} />
{:else}
<div class="flex h-screen bg-gray-100 overflow-hidden">
	<!-- Left Sidebar - App Navigation -->
	<div class="w-16 bg-[#464775] flex flex-col items-center py-2 space-y-4">
		<div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center mb-2">
			<span class="text-[#464775] font-bold text-sm">SK</span>
		</div>

		<button
			class="w-12 h-12 flex flex-col items-center justify-center hover:bg-[#5b5d8a] rounded transition-colors {currentView ===
			'activity'
				? 'bg-[#5b5d8a]'
				: ''}"
			on:click={() => (currentView = 'activity')}
		>
			<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
				/>
			</svg>
			<span class="text-white text-[10px] mt-1">Activity</span>
		</button>

		<button
			class="w-12 h-12 flex flex-col items-center justify-center hover:bg-[#5b5d8a] rounded transition-colors relative {currentView ===
				'chat-view' || currentView === 'chat'
				? 'bg-[#5b5d8a]'
				: ''}"
			on:click={() => (currentView = 'chat-view')}
		>
			<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
				/>
			</svg>
			<span class="text-white text-[10px] mt-1">Chat</span>
			<span
				class="absolute top-1 right-1 bg-red-500 text-white text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center"
				>3</span
			>
		</button>

		<button
			class="w-12 h-12 flex flex-col items-center justify-center hover:bg-[#5b5d8a] rounded transition-colors {currentView ===
			'teams'
				? 'bg-[#5b5d8a]'
				: ''}"
			on:click={() => (currentView = 'teams')}
		>
			<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
				/>
			</svg>
			<span class="text-white text-[10px] mt-1">Teams</span>
		</button>

		<button
			class="w-12 h-12 flex flex-col items-center justify-center hover:bg-[#5b5d8a] rounded transition-colors {currentView ===
			'calendar'
				? 'bg-[#5b5d8a]'
				: ''}"
			on:click={() => (currentView = 'calendar')}
		>
			<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
				/>
			</svg>
			<span class="text-white text-[10px] mt-1">Calendar</span>
		</button>

		<button
			class="w-12 h-12 flex flex-col items-center justify-center hover:bg-[#5b5d8a] rounded transition-colors {currentView ===
			'calls'
				? 'bg-[#5b5d8a]'
				: ''}"
			on:click={() => (currentView = 'calls')}
		>
			<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
				/>
			</svg>
			<span class="text-white text-[10px] mt-1">Calls</span>
		</button>

		<button
			class="w-12 h-12 flex flex-col items-center justify-center hover:bg-[#5b5d8a] rounded transition-colors {currentView ===
			'files'
				? 'bg-[#5b5d8a]'
				: ''}"
			on:click={() => (currentView = 'files')}
		>
			<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
				/>
			</svg>
			<span class="text-white text-[10px] mt-1">Files</span>
		</button>

		<div class="flex-1"></div>

		<!-- User profile button at bottom -->
		<button 
			on:click={() => { showUserSelection = true; currentUser = null; }}
			class="w-12 h-12 {currentUser?.color} rounded-full flex items-center justify-center hover:ring-2 hover:ring-white transition-all mb-2"
			title="Switch User - {currentUser?.name}"
		>
			<span class="text-white text-sm font-bold">{currentUser?.initials}</span>
		</button>
	</div>

	{#if currentView === 'activity'}
		<ActivityView />
	{:else if currentView === 'chat-view'}
		{#key `${selectedChat}-${(conversationMessages[selectedChat] || []).length}`}
			<ChatView
				{conversations}
				{selectedChat}
				{chatMessages}
				on:sendMessage={handleChatMessage}
				on:closeCard={handleCloseCard}
				on:goToChat={handleGoToChat}
				on:selectChat={handleSelectChat}
			/>
		{/key}
	{:else if currentView === 'calls'}
		<CallsView />
	{:else if currentView === 'files'}
		<FilesView />
	{:else if currentView === 'calendar'}
		<CalendarView />
	{:else if currentView === 'teams'}
		<TeamsView {teams} on:selectTeam={handleSelectTeam} />
	{:else}
		<!-- Original Chat View (Channel View) -->
		<!-- Channel/Team List Sidebar -->
		<div class="w-80 bg-white border-r border-gray-200 flex flex-col">
			<!-- Search Bar -->
			<div class="p-3 border-b border-gray-200">
				<div class="relative">
					<input
						type="text"
						placeholder="Search"
						class="w-full pl-10 pr-4 py-2 bg-gray-100 border-0 rounded-md focus:outline-none focus:ring-2 focus:ring-[#6264a7]"
					/>
					<svg
						class="w-5 h-5 text-gray-400 absolute left-3 top-2.5"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
						/>
					</svg>
				</div>
			</div>

		<!-- Back to Teams Button -->
		<div class="p-3 border-b border-gray-200">
			<button
				on:click={() => (currentView = 'teams')}
				class="w-full flex items-center space-x-2 px-3 py-2 rounded hover:bg-gray-100 text-[#6264a7] transition-colors"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 19l-7-7 7-7"
					/>
				</svg>
				<span class="text-sm font-medium">Back to Teams</span>
			</button>
		</div>

		<!-- Team Header -->
		<div class="p-4 border-b border-gray-200">
			<div class="flex items-center justify-between">
				<div class="flex items-center space-x-2">
					<div class="w-8 h-8 bg-[#6264a7] rounded flex items-center justify-center">
						<span class="text-white font-semibold text-sm">S</span>
					</div>
					<div>
						<h2 class="font-semibold text-sm">Sandvik Support</h2>
						<p class="text-xs text-gray-500">Parts & Technical</p>
					</div>
				</div>
				<button class="text-gray-400 hover:text-gray-600" title="Options">
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>
			</div>
		</div>

			<!-- Channel List -->
			<div class="flex-1 overflow-y-auto">
				<div class="px-3 py-2">
					<div class="text-xs font-semibold text-gray-500 uppercase mb-2">Channels</div>

					<button
						class="w-full flex items-center space-x-3 px-3 py-2 rounded hover:bg-gray-100 {selectedChannel ===
						'General'
							? 'bg-gray-200'
							: ''}"
						on:click={() => (selectedChannel = 'General')}
					>
						<svg
							class="w-5 h-5 text-gray-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"
							/>
						</svg>
						<span class="text-sm font-medium">General</span>
					</button>

					<button
						class="w-full flex items-center space-x-3 px-3 py-2 rounded hover:bg-gray-100 {selectedChannel ===
						'Parts Support'
							? 'bg-gray-200'
							: ''}"
						on:click={() => (selectedChannel = 'Parts Support')}
					>
						<svg
							class="w-5 h-5 text-gray-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"
							/>
						</svg>
						<div class="flex-1 text-left">
							<div class="flex items-center justify-between">
								<span class="text-sm font-medium">Parts Support</span>
							</div>
						</div>
					</button>

					<button
						class="w-full flex items-center space-x-3 px-3 py-2 rounded hover:bg-gray-100 {selectedChannel ===
						'Technical Help'
							? 'bg-gray-200'
							: ''}"
						on:click={() => (selectedChannel = 'Technical Help')}
					>
						<svg
							class="w-5 h-5 text-gray-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"
							/>
						</svg>
						<span class="text-sm font-medium">Technical Help</span>
					</button>

					<button
						class="w-full flex items-center space-x-3 px-3 py-2 rounded hover:bg-gray-100 {selectedChannel ===
						'Warehouse'
							? 'bg-gray-200'
							: ''}"
						on:click={() => (selectedChannel = 'Warehouse')}
					>
						<svg
							class="w-5 h-5 text-gray-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"
							/>
						</svg>
						<span class="text-sm font-medium">Warehouse</span>
					</button>

					<button
						class="w-full flex items-center space-x-3 px-3 py-2 rounded hover:bg-gray-100 text-[#6264a7]"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4v16m8-8H4"
							/>
						</svg>
						<span class="text-sm font-medium">Add channel</span>
					</button>
				</div>
			</div>
		</div>

		<!-- Main Chat Area -->
		<div class="flex-1 flex flex-col bg-white">
			<!-- Top Header -->
			<div class="h-14 border-b border-gray-200 flex items-center justify-between px-6">
				<div class="flex items-center space-x-3">
					<h1 class="text-lg font-semibold">{selectedChannel}</h1>
					<button class="text-gray-400 hover:text-gray-600" title="Edit channel">
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
							/>
						</svg>
					</button>
				</div>

				<div class="flex items-center space-x-2">
					<button class="p-2 hover:bg-gray-100 rounded transition-colors" title="Video call">
						<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
							/>
						</svg>
					</button>
					<button class="p-2 hover:bg-gray-100 rounded transition-colors" title="Audio call">
						<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
							/>
						</svg>
					</button>
					<button class="p-2 hover:bg-gray-100 rounded transition-colors" title="Share screen">
						<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
							/>
						</svg>
					</button>
					<div class="w-px h-6 bg-gray-300 mx-2"></div>
					<button class="p-2 hover:bg-gray-100 rounded transition-colors" title="More options">
						<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
							/>
						</svg>
					</button>
				</div>
			</div>

			<!-- Messages Area -->
			<div class="flex-1 overflow-y-auto px-6 py-4 space-y-4">
				{#if messages.length === 0}
					<div class="flex items-center justify-center h-full text-gray-400">
						<div class="text-center">
							<svg
								class="w-16 h-16 mx-auto mb-4 text-gray-300"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
								/>
							</svg>
							<p class="text-sm">Loading messages...</p>
						</div>
					</div>
				{:else}
					{#each messages as message, i}
						{@const msgId = getMessageId(message)}
						{@const msgTimestamp = getMessageTimestamp(message)}
						{@const msgText = getMessageText(message)}
						{@const msgFrom = message.from || { displayName: 'Unknown', initials: 'UN', color: 'bg-gray-600' }}
						{@const isMe = message.from && message.from.displayName === currentUser?.name}
						{@const showDate =
							i === 0 ||
							formatDate(msgTimestamp) !== formatDate(getMessageTimestamp(messages[i - 1]))}
						{#if showDate}
							<div class="flex items-center justify-center my-4">
								<div class="bg-gray-200 text-gray-600 text-xs px-3 py-1 rounded-full">
									{formatDate(msgTimestamp)}
								</div>
							</div>
						{/if}

						<div class="flex space-x-3 group hover:bg-gray-50 -mx-6 px-6 py-2 rounded">
							<div
								class="w-8 h-8 rounded-full {msgFrom.color} flex items-center justify-center flex-shrink-0"
							>
								<span class="text-white text-sm font-medium">
									{msgFrom.initials}
								</span>
							</div>
							<div class="flex-1 min-w-0">
								<div class="flex items-baseline space-x-2">
									<span class="font-semibold text-sm">
										{isMe ? 'You' : msgFrom.displayName}
									</span>
									<span class="text-xs text-gray-500">{formatTime(msgTimestamp)}</span>
									{#if isSimplifiedMessage(message) && message.has_typo}
										<span
											class="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded"
											title="Contains typo">✏️</span
										>
									{/if}
								</div>
								<div class="text-sm text-gray-800 mt-1 break-words">
									{msgText}
								</div>
								{#if isSimplifiedMessage(message) && message.referenced_sku}
									<div
										class="mt-2 inline-flex items-center space-x-2 bg-blue-50 border border-blue-200 rounded px-3 py-2"
									>
										<svg
											class="w-4 h-4 text-blue-600"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
											/>
										</svg>
										<span class="text-xs font-mono text-blue-800">SKU: {message.referenced_sku}</span
										>
									</div>
								{/if}
								<div
									class="mt-1 opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-3"
								>
									<button class="text-gray-400 hover:text-gray-600 text-xs flex items-center space-x-1" title="Edit message">
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
											/>
										</svg>
									</button>
									<button class="text-gray-400 hover:text-gray-600 text-xs flex items-center space-x-1" title="Reply to message">
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
											/>
										</svg>
									</button>
									<button class="text-gray-400 hover:text-gray-600 text-xs flex items-center space-x-1">
										<span>Reply</span>
									</button>
								</div>
							</div>
						</div>
					{/each}
				{/if}
			</div>

			<!-- Message Input Area -->
			<div class="border-t border-gray-200 p-4">
				<div
					class="bg-white border border-gray-300 rounded-lg focus-within:border-[#6264a7] focus-within:ring-1 focus-within:ring-[#6264a7]"
				>
					<div class="p-3">
						<textarea
							bind:value={messageInput}
							placeholder="Type a message"
							class="w-full resize-none border-0 focus:outline-none text-sm"
							rows="3"
							on:keydown={(e) => {
								if (e.key === 'Enter' && !e.shiftKey) {
									e.preventDefault();
									sendMessage();
								}
							}}
						></textarea>
					</div>
					<div class="flex items-center justify-between px-3 pb-3 pt-1 border-t border-gray-200">
						<div class="flex items-center space-x-2">
							<button class="p-1.5 hover:bg-gray-100 rounded transition-colors" title="Format">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 6h16M4 12h16m-7 6h7"
									/>
								</svg>
							</button>
							<button class="p-1.5 hover:bg-gray-100 rounded transition-colors" title="Attach file">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
									/>
								</svg>
							</button>
							<button class="p-1.5 hover:bg-gray-100 rounded transition-colors" title="Emoji">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
							</button>
							<button class="p-1.5 hover:bg-gray-100 rounded transition-colors" title="GIF">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
									/>
								</svg>
							</button>
						</div>
						<button
							on:click={sendMessage}
							disabled={!messageInput.trim()}
							class="px-4 py-2 bg-[#6264a7] text-white rounded hover:bg-[#5558a0] disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
						>
							Send
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
{/if}

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		overflow: hidden;
	}
</style>
