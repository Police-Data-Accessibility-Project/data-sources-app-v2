<template>
	<main class="pdap-flex-container mx-auto max-w-2xl pb-24">
		<h1>Sign In</h1>
		<Button
			class="border-2 border-neutral-950 border-solid [&>svg]:ml-0"
			intent="tertiary"
			@click="async () => await auth.loginWithGithub()"
		>
			<FontAwesomeIcon :icon="faGithub" />
			Sign in with Github
		</Button>

		<h2>Or sign in with email</h2>
		<FormV2
			id="login"
			class="flex flex-col"
			data-test="login-form"
			name="login"
			:error="error"
			:schema="VALIDATION_SCHEMA"
			@submit="onSubmit"
		>
			<InputText
				id="email"
				autocomplete="email"
				data-test="email"
				name="email"
				label="Email"
				type="text"
				placeholder="Your email address"
			/>
			<InputPassword
				id="password"
				autocomplete="password"
				data-test="password"
				name="password"
				label="Password"
				type="password"
				placeholder="Your password"
			/>

			<Button
				class="max-w-full"
				:is-loading="loading"
				type="submit"
				data-test="submit-button"
			>
				<Spinner v-if="loading" :show="loading" />
				{{ !loading ? 'Sign in' : '' }}
			</Button>
		</FormV2>
		<div
			class="flex flex-col items-start sm:flex-row sm:items-center sm:gap-4 w-full"
		>
			<RouterLink
				class="pdap-button-secondary flex-1 max-w-full"
				intent="secondary"
				data-test="toggle-button"
				to="/sign-up"
			>
				Create Account
			</RouterLink>
			<RouterLink
				class="pdap-button-secondary flex-1 max-w-full"
				data-test="reset-link"
				to="/reset-password"
			>
				Reset Password
			</RouterLink>
		</div>
	</main>
</template>

<script>
// Navigation guard via data loader
import { NavigationResult } from 'unplugin-vue-router/data-loaders';
import { defineBasicLoader } from 'unplugin-vue-router/data-loaders/basic';
import { useAuthStore } from '@/stores/auth';

const { userId } = useAuthStore();

export const useDataSourceData = defineBasicLoader('/sign-in', async () => {
	if (userId) return new NavigationResult({ path: '/' });
});
</script>

<script setup>
// Imports
import {
	Button,
	FormV2,
	InputPassword,
	InputText,
	Spinner,
} from 'pdap-design-system';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Constants
const VALIDATION_SCHEMA = [
	{
		name: 'email',
		validators: {
			required: {
				value: true,
			},
			email: {
				message: 'Please provide your email address',
				value: true,
			},
		},
	},
	{
		name: 'password',
		validators: {
			required: {
				value: true,
			},
			password: {
				message: 'Please provide your password',
				value: true,
			},
		},
	},
];

// Store
const auth = useAuthStore();

// Reactive vars
const error = ref(undefined);
const loading = ref(false);

// Handlers
/**
 * Logs user in
 */
async function onSubmit(formValues) {
	try {
		loading.value = true;
		const { email, password } = formValues;

		await auth.loginWithEmail(email, password);

		error.value = undefined;
		router.push(auth.redirectTo ?? '/');
	} catch (err) {
		error.value = 'Something went wrong, please try again.';
	} finally {
		loading.value = false;
	}
}
</script>
