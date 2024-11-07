import axios from 'axios';
import { defineStore } from 'pinia';
import parseJwt from '../util/parseJwt';
import router from '../router';
import { useUserStore } from './user';

const HEADERS = {
	'Content-Type': 'application/json',
};
const LOGIN_WITH_EMAIL_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/login`;
const LOGIN_WITH_GITHUB_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/auth/login-with-github`;
const LINK_WITH_GITHUB_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/auth/link-to-github`;
const REFRESH_SESSION_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/refresh-session`;
const START_OAUTH_URL = `${import.meta.env.VITE_VUE_API_BASE_URL}/auth/oauth`;

export const useAuthStore = defineStore('auth', {
	state: () => ({
		userId: null,
		tokens: {
			accessToken: {
				value: null,
				expires: Date.now(),
			},
			refreshToken: {
				value: null,
				expires: Date.now(),
			},
		},
		redirectTo: null,
	}),
	persist: {
		storage: sessionStorage,
		pick: ['userId', 'tokens'],
	},
	actions: {
		async loginWithEmail(email, password) {
			const user = useUserStore();

			const response = await axios.post(
				LOGIN_WITH_EMAIL_URL,
				{ email, password },
				{
					headers: {
						...HEADERS,
						// TODO: API should require auth
						// authorization: `Basic ${import.meta.env.VITE_ADMIN_API_KEY}`,
					},
				},
			);

			// Update user store with email
			user.$patch({ email });

			this.parseTokensAndSetData(response);
		},

		async beginOAuthLogin(redirectPath = '/sign-in') {
			const redirectTo = encodeURI(
				`${START_OAUTH_URL}?redirect_url=${import.meta.env.VITE_VUE_APP_BASE_URL}${redirectPath}`,
			);

			window.location.href = redirectTo;
		},

		async loginWithGithub(gh_access_token) {
			const response = await axios.post(
				LOGIN_WITH_GITHUB_URL,
				{ gh_access_token },
				{
					headers: {
						...HEADERS,
					},
				},
			);

			this.parseTokensAndSetData(response);
			return true;
		},

		async linkAccountWithGithub(gh_access_token) {
			const { email } = useUserStore();
			const user_email = email || this.userId;

			return await axios.post(
				LINK_WITH_GITHUB_URL,
				{ gh_access_token, user_email },
				{
					headers: {
						...HEADERS,
						// authorization: `Bearer ${this.$state.tokens.accessToken.value}`,
					},
				},
			);
		},

		async logout() {
			const user = useUserStore();

			this.$reset();
			user.$reset();

			router.replace(this.redirectTo?.meta.auth ? '/sign-in' : '/');
		},

		async refreshAccessToken() {
			if (!this.$state.userId) return;
			try {
				const response = await axios.post(
					REFRESH_SESSION_URL,
					{ session_token: this.$state.tokens.accessToken.value },
					{
						headers: {
							...HEADERS,
							authorization: `Bearer ${this.$state.tokens.refreshToken.value}`,
						},
					},
				);
				return this.parseTokensAndSetData(response);
			} catch (error) {
				throw new Error(error.response?.data?.message);
			}
		},

		parseTokensAndSetData(response) {
			const accessToken = response.data.access_token;
			const refreshToken = response.data.refresh_token;
			const accessTokenParsed = parseJwt(accessToken);
			const refreshTokenParsed = parseJwt(refreshToken);

			this.$patch({
				userId: accessTokenParsed.sub,
				tokens: {
					accessToken: {
						value: accessToken,
						expires: new Date(accessTokenParsed.exp * 1000).getTime(),
					},
					refreshToken: {
						value: refreshToken,
						expires: new Date(refreshTokenParsed.exp * 1000).getTime(),
					},
				},
			});
		},

		setRedirectTo(path) {
			this.$patch({
				redirectTo: path,
			});
		},
	},
});
