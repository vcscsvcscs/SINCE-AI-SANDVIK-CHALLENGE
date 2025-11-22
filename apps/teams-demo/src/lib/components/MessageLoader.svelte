<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getMessageText,
		getMessageId,
		getMessageTimestamp,
		isSimplifiedMessage,
		isMessageActionsPayload,
		getSenderName,
		extractSkuFromText
	} from '$lib/types';

	export let dataSource = 'simplified';
	export let messages = [];

	let loading = false;
	let error = '';

	onMount(async () => {
		await loadMessages();
	});

	async function loadMessages() {
		loading = true;
		error = '';
		try {
			let url = '';
			if (dataSource === 'simplified') {
				// Load your existing test data
				url = '/synthetic-data_EN.json';
			} else {
				// Load Teams format example
				url = '/example-teams-message.json';
			}

			const response = await fetch(url);
			if (!response.ok) {
				throw new Error(`Failed to load messages: ${response.statusText}`);
			}
			const data = await response.json();
			messages = data;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Unknown error';
		} finally {
			loading = false;
		}
	}

	function formatTime(timestamp) {
		const date = new Date(timestamp);
		return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
	}

	function formatDate(timestamp) {
		const date = new Date(timestamp);
		return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}
</script>

<div class="message-loader">
	<div class="controls mb-4 flex items-center space-x-4">
		<label class="flex items-center space-x-2">
			<input
				type="radio"
				bind:group={dataSource}
				value="simplified"
				on:change={loadMessages}
				class="text-[#6264a7]"
			/>
			<span>Simplified Format (Test Data)</span>
		</label>
		<label class="flex items-center space-x-2">
			<input
				type="radio"
				bind:group={dataSource}
				value="teams"
				on:change={loadMessages}
				class="text-[#6264a7]"
			/>
			<span>Teams MessageActionsPayload</span>
		</label>
	</div>

	{#if loading}
		<div class="text-center py-8 text-gray-500">Loading messages...</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 text-red-800 p-4 rounded">
			Error: {error}
		</div>
	{:else if messages.length === 0}
		<div class="text-center py-8 text-gray-500">No messages loaded</div>
	{:else}
		<div class="space-y-4">
			<div class="bg-blue-50 border border-blue-200 text-blue-800 p-3 rounded text-sm">
				<strong>Loaded {messages.length} messages</strong> in
				{dataSource === 'simplified' ? 'Simplified' : 'Teams MessageActionsPayload'} format
			</div>

			{#each messages as message}
				{@const msgId = getMessageId(message)}
				{@const msgText = getMessageText(message)}
				{@const msgTimestamp = getMessageTimestamp(message)}
				{@const sku = isSimplifiedMessage(message)
					? message.referenced_sku
					: extractSkuFromText(msgText)}

				<div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
					<div class="flex items-start justify-between mb-2">
						<div class="flex items-center space-x-2">
							<div
								class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center"
							>
								<span class="text-white text-xs font-medium">
									{msgId.slice(-2).toUpperCase()}
								</span>
							</div>
							<div>
								<div class="font-semibold text-sm">
									{#if isMessageActionsPayload(message) && message.from_property}
										{getSenderName(message)}
									{:else}
										User {msgId.slice(-3)}
									{/if}
								</div>
								<div class="text-xs text-gray-500">
									{formatDate(msgTimestamp)} at {formatTime(msgTimestamp)}
								</div>
							</div>
						</div>

						<!-- Format badge -->
						<span
							class="text-xs px-2 py-1 rounded {dataSource === 'simplified'
								? 'bg-green-100 text-green-800'
								: 'bg-purple-100 text-purple-800'}"
						>
							{dataSource === 'simplified' ? 'Simplified' : 'Teams'}
						</span>
					</div>

					<div class="text-sm text-gray-800 mb-2">
						{msgText}
					</div>

					<!-- Show importance for Teams messages -->
					{#if isMessageActionsPayload(message) && message.importance && message.importance !== 'normal'}
						<div class="inline-flex items-center space-x-1 mb-2">
							<svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
								<path
									fill-rule="evenodd"
									d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
									clip-rule="evenodd"
								/>
							</svg>
							<span class="text-xs font-semibold text-red-600 uppercase"
								>{message.importance}</span
							>
						</div>
					{/if}

					<!-- SKU badge -->
					{#if sku}
						<div class="inline-flex items-center space-x-2 bg-blue-50 border border-blue-200 rounded px-3 py-1">
							<svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
								/>
							</svg>
							<span class="text-xs font-mono text-blue-800">SKU: {sku}</span>
						</div>
					{/if}

					<!-- Show additional Teams-specific data -->
					{#if isMessageActionsPayload(message)}
						<div class="mt-3 pt-3 border-t border-gray-100">
							<div class="text-xs text-gray-500 space-y-1">
								{#if message.reply_to_id}
									<div>↪ Reply to: {message.reply_to_id}</div>
								{/if}
								{#if message.mentions && message.mentions.length > 0}
									<div>
										@Mentions: {message.mentions.map((m) => m.mentionText).join(', ')}
									</div>
								{/if}
								{#if message.reactions && message.reactions.length > 0}
									<div class="flex items-center space-x-2">
										<span>Reactions:</span>
										{#each message.reactions as reaction}
											<span class="bg-gray-100 px-2 py-0.5 rounded">
												{reaction.reactionType}
											</span>
										{/each}
									</div>
								{/if}
								{#if message.attachments && message.attachments.length > 0}
									<div>📎 {message.attachments.length} attachment(s)</div>
								{/if}
							</div>
						</div>
					{/if}

					<!-- Show simplified format specific data -->
					{#if isSimplifiedMessage(message)}
						<div class="mt-3 pt-3 border-t border-gray-100">
							<div class="text-xs text-gray-500 space-y-1">
								<div>Query Type: <span class="font-mono">{message.query_type}</span></div>
								{#if message.has_typo}
									<div class="text-yellow-600">⚠️ Contains typo</div>
								{/if}
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>

