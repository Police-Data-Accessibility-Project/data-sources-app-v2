import { defineStore } from 'pinia';

export const useDataSourceStore = defineStore('data-source', {
	state: () => ({
		/** Previous route visited - useful for determining whether we are incrementing or decrementing pages in data source by id */
		previousDataSourceRoute: null,
	}),
	persist: {
		storage: sessionStorage,
	},
	actions: {
		setPreviousDataSourceRoute(route) {
			this.$patch({
				previousDataSourceRoute: route,
			});
		},
	},
});
