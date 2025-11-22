<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import AdaptiveCard from './AdaptiveCard.svelte';

	const dispatch = createEventDispatcher();

	export let conversations: any[];
	export let selectedChat: string;
	export let chatMessages: any[];

	let messageInput = '';

	function sendMessage() {
		if (messageInput.trim()) {
			dispatch('sendMessage', { message: messageInput });
			messageInput = '';
		}
	}

	function handleCardButton(action: string) {
		dispatch('cardAction', { action });
	}

	function selectChat(name: string) {
		dispatch('selectChat', { name });
	}

	function handleCloseCard(event: CustomEvent) {
		dispatch('closeCard', { messageId: event.detail.messageId });
	}

	function handleGoToChat(event: CustomEvent) {
		dispatch('goToChat', { chatLink: event.detail.chatLink });
	}
</script>

<div class="flex-1 flex flex-col overflow-hidden bg-white">
	<!-- Top Header -->
	<div class="h-16 border-b border-gray-200 flex items-center justify-between px-8 bg-[#464775]">
		<div class="flex items-center space-x-4">
			<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
				/>
			</svg>
			<h1 class="text-2xl font-semibold text-white">Chat</h1>
		</div>
		<div class="flex items-center space-x-4">
			<div class="relative">
				<input
					type="text"
					placeholder="Search chats"
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

	<!-- Main Content Area -->
	<div class="flex-1 flex overflow-hidden">
		<!-- Conversations List -->
		<div class="w-80 border-r border-gray-200 flex flex-col bg-gray-50">
		<!-- Header -->
		<div class="p-4 bg-white border-b border-gray-200">
			<div class="flex items-center justify-between mb-3">
				<div class="flex items-center space-x-2">
					<h2 class="text-xl font-semibold">Chat</h2>
					<button class="text-gray-400 hover:text-gray-600" title="Details">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 9l-7 7-7-7"
							/>
						</svg>
					</button>
				</div>
				<div class="flex items-center space-x-2">
					<button class="p-1 hover:bg-gray-100 rounded" title="Filter">
						<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
							/>
						</svg>
					</button>
					<button class="p-1 hover:bg-gray-100 rounded" title="New chat">
						<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
							/>
						</svg>
					</button>
				</div>
			</div>
		</div>

		<!-- Pinned Section -->
		<div class="px-3 pt-2">
			<button class="flex items-center space-x-2 text-xs text-gray-500 hover:text-gray-700 mb-2">
				<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M19 9l-7 7-7-7"
					/>
				</svg>
				<span class="font-semibold">Pinned</span>
			</button>
		</div>

		<!-- Conversations -->
		<div class="flex-1 overflow-y-auto">
			{#each conversations as conv}
				<button
					class="w-full px-4 py-3 hover:bg-white flex items-center space-x-3 border-l-4 {selectedChat ===
					conv.name
						? 'border-[#6264a7] bg-white'
						: 'border-transparent'}"
					on:click={() => selectChat(conv.name)}
				>
					<div class="relative flex-shrink-0">
						<div
							class="w-10 h-10 {conv.color} rounded-full flex items-center justify-center text-white font-semibold"
						>
							{conv.initials}
						</div>
						{#if conv.online}
							<div
								class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"
							></div>
						{/if}
					</div>
					<div class="flex-1 min-w-0 text-left">
						<div class="flex items-center justify-between">
							<span class="font-semibold text-sm truncate">{conv.name}</span>
							<span class="text-xs text-gray-500">{conv.timestamp}</span>
						</div>
						<p class="text-xs text-gray-600 truncate mt-0.5">{conv.lastMessage}</p>
					</div>
				</button>
			{/each}

			<!-- Recent Section -->
			<div class="px-3 pt-4 pb-2">
				<button class="flex items-center space-x-2 text-xs text-gray-500 hover:text-gray-700">
					<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
					<span class="font-semibold">Recent</span>
				</button>
			</div>
		</div>
	</div>

	<!-- Chat Messages Area -->
	<div class="flex-1 flex flex-col">
		<!-- Chat Header -->
		<div class="h-14 border-b border-gray-200 flex items-center justify-between px-6 bg-white">
			<div class="flex items-center space-x-3">
				<div class="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
					<span class="text-white text-sm font-semibold">TB</span>
				</div>
				<div>
					<h1 class="text-base font-semibold">{selectedChat}</h1>
				</div>
			</div>

			<div class="flex items-center space-x-1">
				<button class="p-2 hover:bg-gray-100 rounded" title="Video call">
					<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
						/>
					</svg>
				</button>
				<button class="p-2 hover:bg-gray-100 rounded" title="Audio call">
					<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
						/>
					</svg>
				</button>
				<button class="p-2 hover:bg-gray-100 rounded" title="Screen share">
					<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
						/>
					</svg>
				</button>
				<button class="p-2 hover:bg-gray-100 rounded" title="More options">
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

		<!-- Messages -->
		<div class="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
			{#each chatMessages as msg}
				<div class="flex space-x-3 group">
					<div class="w-8 h-8 {msg.color} rounded-full flex items-center justify-center flex-shrink-0">
						<span class="text-white text-sm font-medium">{msg.initials}</span>
					</div>
					<div class="flex-1 min-w-0">
						<div class="flex items-baseline space-x-2 mb-1">
							<span class="font-semibold text-sm">{msg.name}</span>
							<span class="text-xs text-gray-500">{msg.timestamp}</span>
						</div>

						{#if msg.sender === 'user'}
							<!-- User messages: plain text bubble -->
							<div class="bg-white rounded-lg shadow-sm p-3 max-w-2xl">
								<p class="text-sm text-gray-800">{msg.text}</p>
							</div>
						{:else if msg.sender === 'bot'}
							<!-- Bot messages: ONLY adaptive cards -->
							{#if msg.card}
								<AdaptiveCard
									title={msg.card.title}
									description={msg.card.description}
									chatLink={msg.card.chatLink}
									messageId={msg.id}
									on:close={handleCloseCard}
									on:goToChat={handleGoToChat}
								/>
							{/if}
						{/if}

						<!-- Reactions -->
						{#if msg.reactions && msg.reactions.length > 0}
							<div class="flex items-center space-x-2 mt-2">
								{#each msg.reactions as reaction}
									<button
										class="flex items-center space-x-1 bg-white border border-gray-200 rounded-full px-2 py-1 hover:border-gray-300"
									>
										<span class="text-sm">{reaction.emoji}</span>
										<span class="text-xs text-gray-600">{reaction.count}</span>
									</button>
								{/each}
								<button
									class="w-6 h-6 bg-white border border-gray-200 rounded-full hover:border-gray-300 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
									title="More reactions"
								>
									<svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
								</button>
							</div>
						{/if}
					</div>
				</div>
			{/each}
		</div>

		<!-- Message Input -->
		<div class="border-t border-gray-200 bg-white p-4">
			<div class="flex items-end space-x-2">
				<div class="flex-1">
					<textarea
						bind:value={messageInput}
						placeholder="Type a new message"
						class="w-full resize-none border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#6264a7] focus:border-transparent text-sm"
						rows="2"
						on:keydown={(e) => {
							if (e.key === 'Enter' && !e.shiftKey) {
								e.preventDefault();
								sendMessage();
							}
						}}
					></textarea>
					<div class="flex items-center justify-between mt-2">
						<div class="flex items-center space-x-1">
							<button class="p-1.5 hover:bg-gray-100 rounded" title="Format">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
									/>
								</svg>
							</button>
							<button class="p-1.5 hover:bg-gray-100 rounded" title="Attach">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
									/>
								</svg>
							</button>
							<button class="p-1.5 hover:bg-gray-100 rounded" title="Link">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
									/>
								</svg>
							</button>
							<button class="p-1.5 hover:bg-gray-100 rounded" title="Emoji">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
							</button>
							<button class="p-1.5 hover:bg-gray-100 rounded" title="GIF">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"
									/>
								</svg>
							</button>
							<button class="p-1.5 hover:bg-gray-100 rounded" title="Sticker">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
									/>
								</svg>
							</button>
							<button class="p-1.5 hover:bg-gray-100 rounded" title="Apps">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
									/>
								</svg>
							</button>
							<button class="p-1.5 hover:bg-gray-100 rounded" title="More">
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z"
									/>
								</svg>
							</button>
						</div>
					</div>
				</div>
				<button
					on:click={sendMessage}
					disabled={!messageInput.trim()}
					class="p-2 bg-[#6264a7] text-white rounded-lg hover:bg-[#5558a0] disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end mb-10"
					title="Send"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
						/>
					</svg>
				</button>
			</div>
		</div>
	</div>
	</div>
</div>
