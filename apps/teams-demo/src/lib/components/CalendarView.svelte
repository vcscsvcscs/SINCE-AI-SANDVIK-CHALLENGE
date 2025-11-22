<script lang="ts">
	// Calendar Week View Component
	let currentDate = new Date();

	$: year = currentDate.getFullYear();
	$: month = currentDate.getMonth();
	$: monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

	const weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
	const timeSlots = [
		'08:00',
		'09:00',
		'10:00',
		'11:00',
		'12:00',
		'13:00',
		'14:00',
		'15:00',
		'16:00',
		'17:00'
	];

	// Sample events
	const events = [
		{
			id: 1,
			title: 'Design standup',
			attendees: 'Tom Davis',
			day: 1,
			startTime: '09:00',
			duration: 1,
			color: 'bg-blue-100 border-blue-500'
		},
		{
			id: 2,
			title: 'Engineering sync',
			attendees: 'Aadi Kapoor',
			day: 1,
			startTime: '10:00',
			duration: 1,
			color: 'bg-purple-900 text-white border-purple-900'
		},
		{
			id: 3,
			title: 'Research workshop',
			attendees: 'Laurence Gilbertson',
			day: 2,
			startTime: '10:00',
			duration: 2,
			color: 'bg-blue-50 border-blue-400'
		},
		{
			id: 4,
			title: 'Files review',
			attendees: 'Eric Ishida',
			day: 1,
			startTime: '12:00',
			duration: 1,
			color: 'bg-blue-50 border-blue-400'
		},
		{
			id: 5,
			title: 'LT Review',
			attendees: 'Microsoft Teams Meeting\nDarren Moulton',
			day: 3,
			startTime: '09:00',
			duration: 3,
			color: 'bg-blue-100 border-blue-500'
		},
		{
			id: 6,
			title: 'Happy hours - on call',
			attendees: 'Kayo Miwa',
			day: 3,
			startTime: '12:00',
			duration: 1,
			color: 'bg-blue-50 border-blue-400'
		},
		{
			id: 7,
			title: 'LT Review',
			attendees: 'Microsoft Teams Meeting\nDarren Moulton',
			day: 4,
			startTime: '10:00',
			duration: 2,
			color: 'bg-blue-100 border-blue-500'
		},
		{
			id: 8,
			title: 'Friday Checkout',
			attendees: 'Chris Naidoo',
			day: 5,
			startTime: '10:00',
			duration: 1,
			color: 'bg-blue-100 border-blue-500'
		},
		{
			id: 9,
			title: 'Brainstorm: Meeting Fatig...',
			attendees: 'Bryan Wright',
			day: 5,
			startTime: '14:00',
			duration: 1,
			color: 'bg-blue-100 border-blue-500'
		}
	];

	function getWeekDates(): Date[] {
		const curr = new Date(currentDate);
		const first = curr.getDate() - curr.getDay(); // First day is Sunday
		const dates: Date[] = [];
		for (let i = 0; i < 7; i++) {
			dates.push(new Date(curr.setDate(first + i)));
		}
		return dates;
	}

	function isToday(date: Date): boolean {
		const today = new Date();
		return (
			date.getDate() === today.getDate() &&
			date.getMonth() === today.getMonth() &&
			date.getFullYear() === today.getFullYear()
		);
	}

	function previousWeek() {
		currentDate = new Date(currentDate.setDate(currentDate.getDate() - 7));
	}

	function nextWeek() {
		currentDate = new Date(currentDate.setDate(currentDate.getDate() + 7));
	}

	function goToToday() {
		currentDate = new Date();
	}

	$: weekDates = getWeekDates();
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
					d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
				/>
			</svg>
			<h1 class="text-2xl font-semibold text-white">Calendar</h1>
		</div>
		<div class="flex items-center space-x-4">
			<div class="relative">
				<input
					type="text"
					placeholder="Search or type a command"
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

	<!-- Calendar Controls -->
	<div class="bg-white border-b border-gray-200 px-8 py-3 flex items-center justify-between">
		<div class="flex items-center space-x-4">
			<button
				on:click={goToToday}
				class="px-3 py-1.5 border border-gray-300 rounded text-sm hover:bg-gray-50 transition-colors font-medium"
			>
				Today
			</button>
			<div class="flex items-center space-x-2">
				<button
					on:click={previousWeek}
					class="p-1.5 hover:bg-gray-100 rounded transition-colors"
					title="Previous week"
				>
					<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 19l-7-7 7-7"
						/>
					</svg>
				</button>
				<button
					on:click={nextWeek}
					class="p-1.5 hover:bg-gray-100 rounded transition-colors"
					title="Next week"
				>
					<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
					</svg>
				</button>
			</div>
			<button
				class="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded transition-colors flex items-center space-x-1"
			>
				<span>{monthName}</span>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			</button>
		</div>
		<div class="flex items-center space-x-2">
			<button
				class="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded transition-colors flex items-center space-x-1"
			>
				<span>Week</span>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			</button>
			<button
				class="px-4 py-1.5 border border-gray-300 rounded text-sm hover:bg-gray-50 transition-colors font-medium flex items-center space-x-2"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
					/>
				</svg>
				<span>Meet now</span>
			</button>
			<button
				class="px-4 py-1.5 bg-[#6264a7] text-white rounded text-sm hover:bg-[#5558a0] transition-colors font-medium flex items-center space-x-2"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				<span>New meeting</span>
			</button>
		</div>
	</div>

	<!-- Calendar Week View -->
	<div class="flex-1 overflow-auto bg-gray-50">
		<div class="min-w-[1200px]">
			<!-- Week Header -->
			<div class="grid grid-cols-8 bg-white border-b border-gray-200 sticky top-0 z-10">
				<div class="border-r border-gray-200"></div>
				{#each weekDates as date, i}
					<div class="border-r border-gray-200 p-3 text-center">
						<div class="text-xs text-gray-600 mb-1">{weekDays[i]}</div>
						<div
							class="text-2xl font-semibold {isToday(date)
								? 'bg-[#6264a7] text-white w-10 h-10 rounded-full flex items-center justify-center mx-auto'
								: 'text-gray-800'}"
						>
							{date.getDate()}
						</div>
					</div>
				{/each}
			</div>

			<!-- Time Grid -->
			<div class="grid grid-cols-8 bg-white">
				<div class="border-r border-gray-200">
					{#each timeSlots as time}
						<div class="h-20 border-b border-gray-200 pr-2 pt-1 text-right">
							<span class="text-xs text-gray-500">{time}</span>
						</div>
					{/each}
				</div>

				<!-- Days columns -->
				{#each Array(7) as _, dayIndex}
					<div class="border-r border-gray-200 relative">
						{#each timeSlots as time}
							<div class="h-20 border-b border-gray-200"></div>
						{/each}

						<!-- Events for this day -->
						{#each events.filter((e) => e.day === dayIndex) as event}
							{@const timeIndex = timeSlots.indexOf(event.startTime)}
							{@const topPosition = timeIndex * 80}
							{@const height = event.duration * 80 - 4}
							<div
								class="absolute left-1 right-1 {event.color} border-l-4 rounded p-2 shadow-sm overflow-hidden"
								style="top: {topPosition}px; height: {height}px;"
							>
								<div class="text-xs font-semibold truncate">{event.title}</div>
								<div class="text-xs text-gray-600 whitespace-pre-line">{event.attendees}</div>
							</div>
						{/each}
					</div>
				{/each}
			</div>
		</div>
	</div>
</div>
