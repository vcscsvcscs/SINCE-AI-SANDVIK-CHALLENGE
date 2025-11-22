<script lang="ts">
	// Calls View Component
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
					d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
				/>
			</svg>
			<h1 class="text-2xl font-semibold text-white">Calls</h1>
		</div>
		<div class="flex items-center space-x-4">
			<div class="relative">
				<input
					type="text"
					placeholder="Search calls"
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

	<!-- Empty State Content -->
	<div class="flex-1 flex items-center justify-center bg-gray-50">
		<div class="text-center max-w-md px-6">
			<div class="mb-6">
				<svg
					class="w-32 h-32 mx-auto text-gray-300"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1.5"
						d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
					/>
				</svg>
			</div>
			<h2 class="text-2xl font-semibold text-gray-700 mb-3">No calls yet</h2>
			<p class="text-gray-500 mb-6">
				Your call history will appear here. Start a video or audio call from any chat or channel.
			</p>
			<div class="flex items-center justify-center space-x-4">
				<button
					class="px-6 py-3 bg-[#6264a7] text-white rounded-lg hover:bg-[#5558a0] transition-colors flex items-center space-x-2"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
						/>
					</svg>
					<span>Start Video Call</span>
				</button>
				<button
					class="px-6 py-3 bg-white border-2 border-[#6264a7] text-[#6264a7] rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
						/>
					</svg>
					<span>Start Audio Call</span>
				</button>
			</div>
		</div>
	</div>
</div>

