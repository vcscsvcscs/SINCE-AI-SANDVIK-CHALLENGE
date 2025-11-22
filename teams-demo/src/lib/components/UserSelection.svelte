<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	
	const dispatch = createEventDispatcher();

	const users = [
		{
			id: 'admin',
			name: 'Admin Sarah',
			initials: 'AS',
			color: 'bg-gradient-to-br from-purple-500 to-pink-500',
			role: 'Administrator'
		},
		{
			id: 'user1',
			name: 'Mike Chen',
			initials: 'MC',
			color: 'bg-gradient-to-br from-blue-500 to-cyan-500',
			role: 'User'
		},
		{
			id: 'user2',
			name: 'Emma Park',
			initials: 'EP',
			color: 'bg-gradient-to-br from-green-500 to-emerald-500',
			role: 'User'
		}
	];

	function selectUser(user: typeof users[0]) {
		dispatch('userSelected', { user });
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-[#464775] via-[#5b5d8a] to-[#6264a7] flex items-center justify-center p-8">
	<div class="text-center">
		<h1 class="text-5xl font-bold text-white mb-4">Who's using Teams?</h1>
		<p class="text-white/80 mb-16 text-lg">Select your profile to continue</p>
		
		<div class="flex gap-12 justify-center items-center">
			{#each users as user}
				<button
					on:click={() => selectUser(user)}
					class="group cursor-pointer transition-transform hover:scale-110 duration-300"
				>
					<div class="relative">
						<!-- User Circle -->
						<div class="{user.color} w-40 h-40 rounded-2xl flex items-center justify-center shadow-2xl group-hover:shadow-purple-500/50 transition-all duration-300 border-4 border-transparent group-hover:border-white">
							<span class="text-white text-5xl font-bold">{user.initials}</span>
						</div>
						
						<!-- Role Badge -->
						{#if user.role === 'Administrator'}
							<div class="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full shadow-lg">
								⭐ ADMIN
							</div>
						{/if}
					</div>
					
					<!-- User Name -->
					<h3 class="text-white text-2xl font-semibold mt-6 group-hover:text-yellow-300 transition-colors">
						{user.name}
					</h3>
					<p class="text-white/60 text-sm mt-1">{user.role}</p>
				</button>
			{/each}
		</div>
		
		<p class="text-white/40 mt-16 text-sm">Click a profile to sign in to Sandvik Teams</p>
	</div>
</div>

