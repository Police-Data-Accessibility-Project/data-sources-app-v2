<template>
	<div id="wrapper" class="h-full w-full" v-on="handlers">
		<slot />
	</div>
</template>

<script setup>
import debounce from 'lodash/debounce';
import { useAuthStore } from '@/stores/auth';
import { useRoute } from 'vue-router';

const route = useRoute();
const auth = useAuthStore();

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
	const now = Date.now();
	const difference = auth.tokens.accessToken.expires - now;

	// User's token is about to expire, update it.
	if (difference <= 60 * 1000 && difference > 0) {
		return auth.refreshAccessToken();
		// User's token is expired, log out.
	} else if (difference <= 0 && auth.userId) {
		return auth.logout(route.meta.auth);
	}
}
</script>
