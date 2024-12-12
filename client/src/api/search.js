import axios from 'axios';
import { ENDPOINTS } from './constants';
import { useAuthStore } from '@/stores/auth';
import _isEqual from 'lodash/isEqual';

const SEARCH_BASE = `${import.meta.env.VITE_VUE_API_BASE_URL}/search`;
const HEADERS = {
	'Content-Type': 'application/json',
};
const HEADERS_BASIC = {
	...HEADERS,
	authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
};

export async function search(params) {
	return await axios.get(`${SEARCH_BASE}/${ENDPOINTS.SEARCH.RESULTS}`, {
		params,
		headers: HEADERS_BASIC,
	});
}

export async function followSearch(params) {
	const auth = useAuthStore();

	return await axios.post(`${SEARCH_BASE}/${ENDPOINTS.SEARCH.FOLLOW}`, null, {
		params,
		headers: {
			...HEADERS,
			Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
		},
	});
}
export async function getFollowedSearches() {
	const auth = useAuthStore();

	const response = await axios.get(
		`${SEARCH_BASE}/${ENDPOINTS.SEARCH.FOLLOW}`,
		{
			headers: {
				...HEADERS,
				Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
			},
		},
	);

	response.data.data.map((followed) => {
		Object.entries(followed).forEach(([key, value]) => {
			if (!value) {
				delete followed[key];
			}
		});
		return followed;
	});

	return response;
}
export async function getFollowedSearch(params) {
	const auth = useAuthStore();

	if (!auth.isAuthenticated()) return false;

	try {
		const response = await getFollowedSearches();

		return response.data.data.find((search) => {
			return _isEqual(search, params);
		});
	} catch (error) {
		return null;
	}
}
export async function deleteFollowedSearch(params) {
	const auth = useAuthStore();

	return await axios.delete(`${SEARCH_BASE}/${ENDPOINTS.SEARCH.FOLLOW}`, {
		params,
		headers: {
			...HEADERS,
			Authorization: `Bearer ${auth.$state.tokens.accessToken.value}`,
		},
	});
}
