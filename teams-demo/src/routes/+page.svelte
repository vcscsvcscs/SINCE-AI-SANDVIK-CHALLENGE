<script lang="ts">
	import { onMount } from 'svelte';
	import ChatView from '$lib/components/ChatView.svelte';

	// Load synthetic data
	let messages: any[] = [];
	let currentView = 'chat';
	let selectedChannel = 'Parts Support';
	let selectedChat = 'TestBot';
	let messageInput = '';

	// Chat conversations list
	const conversations = [
		{
			id: 1,
			name: 'TestBot',
			initials: 'TB',
			color: 'bg-purple-600',
			lastMessage: 'Here is an adaptive card with some options...',
			timestamp: '11:44 AM',
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
		{
			id: 3,
			name: 'Beth Davies',
			initials: 'BD',
			color: 'bg-green-600',
			lastMessage: 'Thanks, that would be nice.',
			timestamp: '1:43 PM',
			online: false,
			unread: 0
		},
		{
			id: 4,
			name: 'Kayo Miwa',
			initials: 'KM',
			color: 'bg-orange-600',
			lastMessage: 'I reviewed with the client on...',
			timestamp: 'Yesterday',
			online: true,
			unread: 0
		},
		{
			id: 5,
			name: 'Will, Kayo, Eric, +2',
			initials: 'WK',
			color: 'bg-pink-600',
			lastMessage: 'Kayo: It would be great to sync...',
			timestamp: '12:00 PM',
			online: false,
			unread: 0
		},
		{
			id: 6,
			name: 'August Bergman',
			initials: 'AB',
			color: 'bg-yellow-600',
			lastMessage: "I haven't checked available time...",
			timestamp: '1:20 PM',
			online: false,
			unread: 0
		},
		{
			id: 7,
			name: 'Charlotte and Babak',
			initials: 'CB',
			color: 'bg-indigo-600',
			lastMessage: 'Babak: I asked the client to send...',
			timestamp: '1:58 PM',
			online: true,
			unread: 0
		},
		{
			id: 8,
			name: 'Emiliano Ceballos',
			initials: 'EC',
			color: 'bg-cyan-600',
			lastMessage: 'Sounds good?',
			timestamp: '1:55 PM',
			online: true,
			unread: 0
		},
		{
			id: 9,
			name: 'Marie Beaudouin',
			initials: 'MB',
			color: 'bg-blue-500',
			lastMessage: 'Sounds good?',
			timestamp: '1:00 PM',
			online: true,
			unread: 0
		},
		{
			id: 10,
			name: 'Oscar Krogh',
			initials: 'OK',
			color: 'bg-green-500',
			lastMessage: 'You: Thanks! Have a nice...',
			timestamp: '11:02 AM',
			online: true,
			unread: 0
		}
	];

	// Chat messages for TestBot
	let chatMessages = [
		{
			id: 1,
			sender: 'user',
			name: 'You',
			initials: 'ME',
			color: 'bg-blue-600',
			text: 'Hi TestBot, can you help me with parts information?',
			timestamp: '5/12, 9:15 AM',
			reactions: []
		},
		{
			id: 2,
			sender: 'bot',
			name: 'TestBot',
			initials: 'TB',
			color: 'bg-purple-600',
			text: 'Hello! I can help you find parts information, check availability, and provide lead times. What would you like to know?',
			timestamp: '5/12, 9:15 AM',
			reactions: [
				{ emoji: '👍', count: 2 },
				{ emoji: '❤️', count: 1 }
			]
		},
		{
			id: 3,
			sender: 'user',
			name: 'You',
			initials: 'ME',
			color: 'bg-blue-600',
			text: 'I need information about part 00002771',
			timestamp: '5/12, 9:16 AM',
			reactions: []
		},
		{
			id: 4,
			sender: 'bot',
			name: 'TestBot',
			initials: 'TB',
			color: 'bg-purple-600',
			text: 'Thank you for always being so positive!',
			timestamp: '11:44 AM',
			reactions: [],
			isCard: false
		},
		{
			id: 5,
			sender: 'bot',
			name: 'TestBot',
			initials: 'TB',
			color: 'bg-purple-600',
			text: 'And this is the subhead, or a message preview. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod...',
			timestamp: '11:44 AM',
			reactions: [],
			isCard: true,
			card: {
				title: 'Part Information Card',
				subtitle: 'SKU: 00002771 - PUMP',
				body: 'This part is currently in stock and available for immediate shipment. Lead time is 2-3 business days for standard delivery. The part is compatible with multiple machine models.',
				buttons: [
					{ label: 'Check Stock', action: 'stock' },
					{ label: 'View Details', action: 'details' },
					{ label: 'Order Now', action: 'order' },
					{ label: 'Contact Support', action: 'support' }
				]
			}
		}
	];

	// Teams data
	const teams = [
		{ name: 'Sandvik Support', initials: 'SS', color: 'bg-blue-600' },
		{ name: 'Parts Warehouse', initials: 'PW', color: 'bg-green-600' },
		{ name: 'Technical Help', initials: 'TH', color: 'bg-yellow-600' },
		{ name: 'Engineering', initials: 'EN', color: 'bg-cyan-600' },
		{ name: 'Quality Control', initials: 'QC', color: 'bg-orange-600' },
		{ name: 'Logistics', initials: 'LO', color: 'bg-green-700' },
		{ name: 'Manufacturing', initials: 'MA', color: 'bg-yellow-700' },
		{ name: 'Product Development', initials: 'PD', color: 'bg-blue-500' },
		{ name: 'Customer Service', initials: 'CS', color: 'bg-orange-700' },
		{ name: 'Field Operations', initials: 'FO', color: 'bg-green-500' }
	];

	onMount(async () => {
		// Load English messages
		const response = await fetch('/synthetic-data_EN.json');
		const data = await response.json();
		messages = data.slice(0, 15); // Show first 15 messages
	});

	function sendMessage() {
		if (messageInput.trim()) {
			// For channel view (not chat-view)
			messages = [
				...messages,
				{
					message_id: `msg_${Date.now()}`,
					timestamp: new Date().toISOString(),
					message: messageInput,
					query_type: 'user_query',
					referenced_sku: null,
					has_typo: false
				}
			];
			messageInput = '';
		}
	}

	function handleChatMessage(event: CustomEvent) {
		const messageInput = event.detail.message;
		// Add user message to chat
		chatMessages = [
			...chatMessages,
			{
				id: chatMessages.length + 1,
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
			}
		];

		// Simulate bot response with adaptive card
		setTimeout(() => {
			const responses = [
				{
					text: 'I found that information for you!',
					hasCard: true,
					card: {
						title: 'Search Results',
						subtitle: 'Based on your query',
						body: 'Here are the details I found. This information is current as of today and includes availability, pricing, and compatibility information.',
						buttons: [
							{ label: 'View More', action: 'more' },
							{ label: 'Add to Cart', action: 'cart' },
							{ label: 'Share', action: 'share' },
							{ label: 'Save', action: 'save' }
						]
					}
				},
				{
					text: 'Let me check that for you...',
					hasCard: false
				}
			];

			const response = responses[Math.floor(Math.random() * responses.length)];

			chatMessages = [
				...chatMessages,
				{
					id: chatMessages.length + 1,
					sender: 'bot',
					name: 'TestBot',
					initials: 'TB',
					color: 'bg-purple-600',
					text: response.text,
					timestamp: new Date().toLocaleTimeString('en-US', {
						hour: '2-digit',
						minute: '2-digit'
					}),
					reactions: [],
					isCard: response.hasCard,
					card: response.hasCard ? response.card : undefined
				}
			];
		}, 1000);
	}

	function handleCardButton(event: CustomEvent) {
		const action = event.detail.action;
		chatMessages = [
			...chatMessages,
			{
				id: chatMessages.length + 1,
				sender: 'bot',
				name: 'TestBot',
				initials: 'TB',
				color: 'bg-purple-600',
				text: `You clicked: ${action}. Processing your request...`,
				timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
				reactions: []
			}
		];
	}

	function handleSelectChat(event: CustomEvent) {
		selectedChat = event.detail.name;
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

		<button
			class="w-12 h-12 flex flex-col items-center justify-center hover:bg-[#5b5d8a] rounded transition-colors"
		>
			<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
		</button>
	</div>

	{#if currentView === 'chat-view'}
		<ChatView
			{conversations}
			{selectedChat}
			{chatMessages}
			on:sendMessage={handleChatMessage}
			on:cardAction={handleCardButton}
			on:selectChat={handleSelectChat}
		/>
	{:else if currentView === 'teams'}
		<!-- Teams View -->
		<div class="flex-1 flex flex-col bg-white overflow-hidden">
			<!-- Top Header -->
			<div class="h-16 border-b border-gray-200 flex items-center justify-between px-8 bg-[#464775]">
				<div class="flex items-center space-x-4">
					<svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
						<path
							d="M20.625 8.25h-7.5V2.625c0-.345-.28-.625-.625-.625h-7.5c-.345 0-.625.28-.625.625V8.25h-1.5c-.345 0-.625.28-.625.625v10.5c0 .345.28.625.625.625h18c.345 0 .625-.28.625-.625v-10.5c0-.345-.28-.625-.625-.625z"
						/>
					</svg>
					<h1 class="text-2xl font-semibold text-white">Microsoft Teams</h1>
				</div>
				<div class="flex items-center space-x-4">
					<div class="relative">
						<input
							type="text"
							placeholder="Search"
							class="w-96 pl-10 pr-4 py-2 bg-[#5b5d8a] border-0 rounded text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-white"
						/>
						<svg
							class="w-5 h-5 text-gray-300 absolute left-3 top-2.5"
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
					<div
						class="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center"
					>
						<span class="text-white font-semibold text-sm">KR</span>
					</div>
				</div>
			</div>

			<!-- Teams Content -->
			<div class="flex-1 overflow-y-auto p-8 bg-gray-50">
				<!-- Secondary Navigation -->
				<div class="mb-6 flex items-center justify-between">
					<div class="flex space-x-6">
						<button class="pb-2 border-b-2 border-[#6264a7] text-[#6264a7] font-semibold">
							Your teams
						</button>
						<button class="pb-2 text-gray-600 hover:text-gray-900">All teams</button>
					</div>
				</div>

				<!-- Page Title and Actions -->
				<div class="mb-8 flex items-center justify-between">
					<h2 class="text-3xl font-bold">Teams</h2>
					<div class="flex space-x-3">
						<button
							class="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 flex items-center space-x-2"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
								/>
							</svg>
							<span>Join a team</span>
						</button>
						<button
							class="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 flex items-center space-x-2"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
								/>
							</svg>
							<span>Create a team</span>
						</button>
					</div>
				</div>

				<!-- Your Teams Section -->
				<div class="mb-6">
					<h3 class="text-xl font-semibold mb-4">Your Teams</h3>
				</div>

				<!-- Teams Grid -->
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
					{#each teams as team}
						<button
							class="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden group cursor-pointer border border-gray-200"
							on:click={() => {
								currentView = 'chat';
								selectedChannel = team.name;
							}}
						>
							<div class="p-6 flex flex-col items-center justify-center space-y-4">
								<div
									class="w-24 h-24 {team.color} rounded-lg flex items-center justify-center transform group-hover:scale-105 transition-transform"
								>
									<span class="text-white font-bold text-3xl">{team.initials}</span>
								</div>
								<div class="text-center">
									<h4 class="font-semibold text-base">{team.name}</h4>
								</div>
							</div>
							<div
								class="border-t border-gray-200 px-6 py-3 bg-gray-50 group-hover:bg-gray-100 transition-colors flex items-center justify-center space-x-2"
							>
								<svg
									class="w-4 h-4 text-gray-500"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
									/>
								</svg>
								<span class="text-sm text-gray-600"
									>{Math.floor(Math.random() * 20) + 5} members</span
								>
							</div>
						</button>
					{/each}
				</div>
			</div>
		</div>
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
					<button class="text-gray-400 hover:text-gray-600">
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
								<span class="bg-[#6264a7] text-white text-xs rounded-full px-2 py-0.5">12</span>
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
					<button class="text-gray-400 hover:text-gray-600">
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
					<button class="p-2 hover:bg-gray-100 rounded transition-colors">
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
						{@const showDate =
							i === 0 ||
							formatDate(message.timestamp) !== formatDate(messages[i - 1].timestamp)}
						{#if showDate}
							<div class="flex items-center justify-center my-4">
								<div class="bg-gray-200 text-gray-600 text-xs px-3 py-1 rounded-full">
									{formatDate(message.timestamp)}
								</div>
							</div>
						{/if}

						<div class="flex space-x-3 group hover:bg-gray-50 -mx-6 px-6 py-2 rounded">
							<div
								class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center flex-shrink-0"
							>
								<span class="text-white text-sm font-medium">
									{message.message_id.includes('user')
										? 'ME'
										: message.message_id.slice(-2).toUpperCase()}
								</span>
							</div>
							<div class="flex-1 min-w-0">
								<div class="flex items-baseline space-x-2">
									<span class="font-semibold text-sm">
										{message.message_id.includes('user')
											? 'You'
											: `User ${message.message_id.slice(-3)}`}
									</span>
									<span class="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
									{#if message.has_typo}
										<span
											class="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded"
											title="Contains typo">✏️</span
										>
									{/if}
								</div>
								<div class="text-sm text-gray-800 mt-1 break-words">
									{message.message}
								</div>
								{#if message.referenced_sku}
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
									<button class="text-gray-400 hover:text-gray-600 text-xs flex items-center space-x-1">
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
											/>
										</svg>
									</button>
									<button class="text-gray-400 hover:text-gray-600 text-xs flex items-center space-x-1">
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

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		overflow: hidden;
	}
</style>
