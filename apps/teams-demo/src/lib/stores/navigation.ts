import { writable, derived } from 'svelte/store';

interface NavigationState {
    currentView: 'chat' | 'teams' | 'activity' | 'calendar' | 'calls' | 'files';
    selectedChannel?: string;
    selectedChat?: string;
    history: Array<{
        view: string;
        channel?: string;
        chat?: string;
    }>;
}

function createNavigationStore() {
    const { subscribe, set, update } = writable<NavigationState>({
        currentView: 'teams',
        history: []
    });

    return {
        subscribe,
        navigateTo: (view: NavigationState['currentView'], options?: { channel?: string; chat?: string }) => {
            update(state => {
                // Add current state to history
                const newHistory = [...state.history, {
                    view: state.currentView,
                    channel: state.selectedChannel,
                    chat: state.selectedChat
                }];

                return {
                    currentView: view,
                    selectedChannel: options?.channel,
                    selectedChat: options?.chat,
                    history: newHistory
                };
            });
        },
        goBack: () => {
            update(state => {
                if (state.history.length === 0) return state;

                const previousState = state.history[state.history.length - 1];
                const newHistory = state.history.slice(0, -1);

                return {
                    currentView: previousState.view as NavigationState['currentView'],
                    selectedChannel: previousState.channel,
                    selectedChat: previousState.chat,
                    history: newHistory
                };
            });
        },
        canGoBack: derived(
            { subscribe },
            $state => $state.history.length > 0
        ),
        reset: () => set({
            currentView: 'teams',
            history: []
        })
    };
}

export const navigation = createNavigationStore();