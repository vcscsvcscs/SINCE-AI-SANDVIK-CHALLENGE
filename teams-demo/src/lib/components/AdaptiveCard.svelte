<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let title: string;
	export let description: string;
	export let chatLink: string;
	export let messageId: number | string;

	const dispatch = createEventDispatcher();

	function handleClose() {
		dispatch('close', { messageId });
	}

	function handleGoToChat() {
		dispatch('goToChat', { chatLink });
	}
</script>

<div class="bg-white rounded-lg shadow-md border border-gray-200 max-w-2xl overflow-hidden">
	<div class="p-4">
		<!-- Header with Title -->
		<div class="mb-3">
			<h3 class="font-semibold text-base text-gray-900">{title}</h3>
		</div>

		<!-- Description -->
		<p class="text-sm text-gray-700 mb-4 leading-relaxed">{description}</p>

		<!-- Action Buttons -->
		<div class="flex items-center space-x-2">
			<button
				on:click={handleGoToChat}
				class="px-4 py-2 bg-[#6264a7] text-white rounded hover:bg-[#5558a0] text-sm font-medium transition-colors flex items-center space-x-2"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
					/>
				</svg>
				<span>Go to Chat</span>
			</button>
			<button
				on:click={handleClose}
				class="px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded hover:bg-gray-50 text-sm font-medium transition-colors flex items-center space-x-2"
				title="Close"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					/>
				</svg>
				<span>Close</span>
			</button>
		</div>
	</div>
</div>

