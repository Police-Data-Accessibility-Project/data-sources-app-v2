import axios from 'axios';
import { isCachedResponseValid } from '@/api/util';
import { useAuthStore } from '@/stores/auth';
import { useDataSourceStore } from '@/stores/data-source';
import { useSearchStore } from '@/stores/search';

const DATA_SOURCES_BASE = `${import.meta.env.VITE_VUE_API_BASE_URL}/data-sources`;
const HEADERS_BASE = {
	'Content-Type': 'application/json',
};
const HEADERS_BASIC = {
	...HEADERS_BASE,
	authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
};

export async function createDataSource(data) {
	const auth = useAuthStore();
	const dataSourceStore = useDataSourceStore();
	const searchStore = useSearchStore();

	const response = await axios.post(DATA_SOURCES_BASE, data, {
		headers: {
			...HEADERS_BASE,
			authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
		},
	});

	dataSourceStore.clearCache();
	searchStore.clearCache();
	return response;
}

export async function getDataSource(id) {
	const dataSourceStore = useDataSourceStore();

	const cached = dataSourceStore.getDataSourceFromCache(id);

	if (
		cached &&
		isCachedResponseValid({
			cacheTime: cached.timestamp,
			// Cache for 3 minutes
			intervalBeforeInvalidation: 1000 * 60 * 3,
		})
	) {
		return cached.data;
	}

	const response = await axios.get(`${DATA_SOURCES_BASE}/${id}`, {
		headers: HEADERS_BASIC,
	});

	dataSourceStore.setDataSourceToCache(id, response);

	return response;
}
