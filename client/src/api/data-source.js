import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

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

	return await axios.post(DATA_SOURCES_BASE, data, {
		headers: {
			...HEADERS_BASE,
			authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
		},
	});
}

export async function getDataSource(id) {
	return await axios.get(`${DATA_SOURCES_BASE}/${id}`, {
		headers: HEADERS_BASIC,
	});
}
