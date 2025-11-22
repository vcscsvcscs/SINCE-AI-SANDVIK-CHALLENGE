<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let teams: Array<{
		name: string;
		initials: string;
		color: string;
	}> = [];

	const dispatch = createEventDispatcher();

	function handleTeamClick(teamName: string) {
		dispatch('selectTeam', { teamName });
	}
</script>

<div class="flex-1 flex flex-col bg-white overflow-hidden">
	<!-- Top Header -->
	<div class="h-16 border-b border-gray-200 flex items-center justify-between px-8 bg-[#464775]">
		<div class="flex items-center space-x-4">
			<svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
				<path
					d="M20.625 8.25h-7.5V2.625c0-.345-.28-.625-.625-.625h-7.5c-.345 0-.625.28-.625.625V8.25h-1.5c-.345 0-.625.28-.625.625v10.5c0 .345.28.625.625.625h18c.345 0 .625-.28.625-.625v-10.5c0-.345-.28-.625-.625-.625z"
				/>
			</svg>
			<h1 class="text-2xl font-semibold text-white">Teams</h1>
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
					on:click={() => handleTeamClick(team.name)}
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
						<span class="text-sm text-gray-600">{Math.floor(Math.random() * 20) + 5} members</span
						>
					</div>
				</button>
			{/each}
		</div>
	</div>
</div>

