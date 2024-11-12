<template>
	<div id="wrapper" class="h-full w-full" v-on="handlers">
		<slot />
	</div>
</template>

<script setup>
import debounce from 'lodash/debounce';
import { useAuthStore } from '@/stores/auth';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const { refreshAccessToken, setRedirectTo, logout, tokens, isAuthenticated } =
	useAuthStore();
const { id: userId } = useUserStore();

// Debounce func for performance
const refreshAuth = debounce(handleAuthRefresh, 350, { leading: true });

const handlers = {
	click: refreshAuth,
	keydown: refreshAuth,
	keypress: refreshAuth,
	keyup: refreshAuth,
	touchstart: refreshAuth,
	touchend: refreshAuth,
	touchcancel: refreshAuth,
	touchmove: refreshAuth,
	scroll: refreshAuth,
	submit: refreshAuth,
};

function handleAuthRefresh() {
	const now = new Date().getTime();
	const differenceFromAccess = tokens.accessToken.expires - now;
	const isExpiredAccess = differenceFromAccess <= 0;
	const shouldRefresh = differenceFromAccess <= 60 * 1000 && isAuthenticated();
	const shouldLogout = isExpiredAccess;

	console.debug({
		differenceFromAccess,
		isExpiredAccess,
		shouldRefresh,
		isAuthenticated: isAuthenticated(),
	});

	// User's token is about to expire, so we refresh it.g
	if (shouldRefresh) {
		return refreshAccessToken();
		// User's tokens are all expired, log out.
	} else if (shouldLogout && userId) {
		setRedirectTo(route);
		return logout();
	} else return;
}
</script>
