import { defineStore } from 'pinia';

export const useSearchStore = defineStore('search', {
	state: () => ({
		/** Searches performed during session. */
		sessionSearchResultsCache: {},
		/** Needed for `NEXT` / `BACK` functionality in data source id view */
		mostRecentSearchIds: [],
	}),
	persist: {
		storage: sessionStorage,
		pick: ['mostRecentSearchIds'],
	},
	actions: {
		setMostRecentSearchIds(ids) {
			this.$patch({
				mostRecentSearchIds: ids,
			});
		},
	},
});
