<template>
	<main class="flex items-center justify-center">
		<Spinner :size="48" :show="true" text="Signing out..." />
	</main>
</template>

<script setup>
import { Spinner } from 'pdap-design-system';
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRoute } from 'vue-router';

const auth = useAuthStore();
const route = useRoute();

onMounted(async () => {
	await auth.logout(route?.redirectedFrom);
});
</script>
