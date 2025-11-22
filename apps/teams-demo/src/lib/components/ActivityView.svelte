<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	// Sample activity feed items
	const activities = [
		{
			id: 1,
			type: 'reply',
			user: 'Joni',
			userInitials: 'JO',
			userColor: 'bg-blue-600',
			action: '+1 replied',
			channel: 'Communications > General',
			preview: "This is awesome! I'm excited for online yoga and...",
			date: '4/28',
			isOnline: true
		},
		{
			id: 2,
			type: 'reaction',
			user: 'Lidia',
			userInitials: 'LI',
			userColor: 'bg-green-600',
			action: '+5 reacted to your post',
			channel: 'Communications > General',
			preview: 'Good morning Design and Communications! Our...',
			date: '4/28',
			isOnline: true
		},
		{
			id: 3,
			type: 'reaction',
			user: 'Joni',
			userInitials: 'JO',
			userColor: 'bg-blue-600',
			action: '+2 reacted to your post',
			channel: 'Communications > General',
			preview: 'Good afternoon! - A reminder the AD awards...',
			date: '4/28',
			isOnline: true
		},
		{
			id: 4,
			type: 'mention',
			user: 'Diego',
			userInitials: 'DI',
			userColor: 'bg-orange-600',
			action: 'mentioned you',
			channel: 'Communications > UI UX copy guidelines',
			preview: 'UI UX copy guidelines kick-off - Please find the...',
			date: '4/28',
			isOnline: false
		},
		{
			id: 5,
			type: 'reaction',
			user: 'Miriam',
			userInitials: 'MI',
			userColor: 'bg-pink-600',
			action: 'reacted to your reply',
			channel: 'Remote living > General',
			preview: ':D',
			date: '4/28',
			isOnline: true
		},
		{
			id: 6,
			type: 'mention',
			user: 'Miriam',
			userInitials: 'MI',
			userColor: 'bg-pink-600',
			action: 'mentioned you',
			channel: 'Remote living > General',
			preview: 'Megan Bowen please share...',
			date: '4/28',
			isOnline: true
		}
	];

	let selectedActivity = activities[0];

	function selectActivity(activity: any) {
		selectedActivity = activity;
	}
</script>

<div class="flex-1 flex flex-col bg-white overflow-hidden">
	<!-- Top Header -->
	<div class="h-16 border-b border-gray-200 flex items-center justify-between px-8 bg-[#464775]">
		<div class="flex items-center space-x-4">
			<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
				/>
			</svg>
			<h1 class="text-2xl font-semibold text-white">Activity</h1>
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

	<!-- Main Content: Feed + Preview -->
	<div class="flex-1 flex overflow-hidden">
		<!-- Left: Activity Feed -->
		<div class="w-[600px] border-r border-gray-200 flex flex-col bg-gray-50">
			<!-- Feed Header -->
			<div class="p-4 bg-white border-b border-gray-200 flex items-center justify-between">
				<button
					class="flex items-center space-x-2 text-2xl font-semibold text-gray-800 hover:bg-gray-50 px-2 py-1 rounded transition-colors"
				>
					<span>Feed</span>
					<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>
				<button class="p-2 hover:bg-gray-100 rounded transition-colors" title="Filter">
					<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
						/>
					</svg>
				</button>
			</div>

			<!-- Activity Feed List -->
			<div class="flex-1 overflow-y-auto">
				{#each activities as activity}
					<button
						on:click={() => selectActivity(activity)}
						class="w-full p-4 border-b border-gray-200 hover:bg-white transition-colors text-left flex items-start space-x-3 {selectedActivity.id ===
						activity.id
							? 'bg-white border-l-4 border-l-[#6264a7]'
							: 'border-l-4 border-l-transparent'}"
					>
						<!-- User Avatar -->
						<div class="relative flex-shrink-0">
							<div
								class="w-10 h-10 {activity.userColor} rounded-full flex items-center justify-center text-white font-semibold"
							>
								{activity.userInitials}
							</div>
							{#if activity.isOnline}
								<div
									class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"
								></div>
							{/if}
						</div>

						<!-- Activity Content -->
						<div class="flex-1 min-w-0">
							<div class="flex items-center space-x-2 mb-1">
								<!-- Icon based on type -->
								{#if activity.type === 'reply'}
									<svg
										class="w-4 h-4 text-gray-600"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
										/>
									</svg>
								{:else if activity.type === 'reaction'}
									<svg
										class="w-4 h-4 text-pink-500"
										fill="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
										/>
									</svg>
								{:else if activity.type === 'mention'}
									<svg
										class="w-4 h-4 text-red-500"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
										/>
									</svg>
								{/if}
								<span class="text-sm font-medium text-gray-800"
									>{activity.user} {activity.action}</span
								>
							</div>
							<div class="text-xs text-gray-500 mb-1">{activity.channel}</div>
							<div class="text-sm text-gray-600 truncate">{activity.preview}</div>
						</div>

						<!-- Date -->
						<div class="text-xs text-gray-500 flex-shrink-0">{activity.date}</div>
					</button>
				{/each}
			</div>
		</div>

		<!-- Right: Channel Preview -->
		<div class="flex-1 flex flex-col bg-white overflow-hidden">
			<!-- Channel Header -->
			<div class="h-14 border-b border-gray-200 flex items-center px-6">
				<div class="flex items-center space-x-3">
					<div class="w-10 h-10 bg-gray-600 rounded flex items-center justify-center">
						<span class="text-white font-semibold text-sm">C</span>
					</div>
					<div>
						<h2 class="text-lg font-semibold text-gray-800">General</h2>
					</div>
				</div>
				<div class="ml-6 flex items-center space-x-6 text-sm">
					<button class="px-3 py-1 font-semibold text-[#6264a7] border-b-2 border-[#6264a7]">
						Posts
					</button>
					<button class="px-3 py-1 text-gray-600 hover:text-gray-800">Files</button>
					<button class="px-3 py-1 text-gray-600 hover:text-gray-800">Wiki</button>
					<button class="px-3 py-1 text-gray-600 hover:text-gray-800">+</button>
				</div>
			</div>

			<!-- Channel Content Preview -->
			<div class="flex-1 overflow-y-auto p-6 bg-gray-50">
				<div class="max-w-4xl">
					<!-- Sample Post -->
					<div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
						<div class="bg-gradient-to-r from-pink-200 to-pink-100 p-8 border-l-4 border-red-500">
							<h1 class="text-4xl font-bold text-red-800 mb-6">Digital Offsite</h1>
							<div class="space-y-4">
								<div>
									<p class="text-red-600 font-bold text-sm mb-2">IMPORTANT!</p>
									<p class="text-gray-700 leading-relaxed">
										Good morning Design and Communications! Our digital offsite agenda kicks off
										with an optional morning yoga and deep meditation session. Be sure to take a
										break! We'll have food delivered to your home in time for lunch. Afterwards,
										we'll work on goals with our assigned teams. We have a lot to work through, but
										we'll...
									</p>
								</div>
								<button class="text-[#6264a7] text-sm font-medium hover:underline">
									See more
								</button>
							</div>
						</div>
						<div class="p-4 border-t border-gray-200 flex items-center justify-between">
							<div class="flex items-center space-x-4">
								<button class="flex items-center space-x-1 text-gray-600 hover:text-gray-800">
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
										/>
									</svg>
									<span class="text-sm">Like</span>
								</button>
								<button class="flex items-center space-x-1 text-gray-600 hover:text-gray-800">
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
										/>
									</svg>
									<span class="text-sm">Reply</span>
								</button>
							</div>
							<div class="text-xs text-gray-500">Posted 4/28</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>


