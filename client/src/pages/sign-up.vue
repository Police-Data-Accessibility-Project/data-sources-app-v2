<template>
	<main v-if="auth.userId" class="pdap-flex-container">
		<h1>Your account is now active</h1>
		<p data-test="success-subheading">Enjoy the data sources app.</p>

		<RouterLink class="pdap-button-secondary mt-6" to="/">
			Search data sources
		</RouterLink>
	</main>

	<!-- Otherwise, the form (form handles error UI on its own) -->
	<main v-else class="pdap-flex-container mx-auto max-w-2xl">
		<h1>Sign Up</h1>
		<Button
			class="border-2 border-neutral-950 border-solid [&>svg]:ml-0"
			intent="tertiary"
			@click="() => console.log('GH button clicked')"
		>
			<FontAwesomeIcon :icon="faGithub" />
			Sign up with Github
		</Button>

		<h2>Or sign up with email</h2>
		<FormV2
			id="login"
			class="flex flex-col"
			data-test="login-form"
			name="login"
			:error="error"
			:schema="VALIDATION_SCHEMA"
			@change="onChange"
			@submit="onSubmit"
			@input="onInput"
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
				v-for="input of PASSWORD_INPUTS"
				v-bind="{ ...input }"
				:key="input.name"
			/>

			<PasswordValidationChecker ref="passwordRef" />

			<Button
				class="max-w-full"
				:disabled="loading"
				type="submit"
				data-test="submit-button"
			>
				<Spinner :show="loading" />
				<template v-if="!loading" #default>Create Account</template>
			</Button>
		</FormV2>
		<div
			class="flex flex-col items-start gap-3 sm:flex-row sm:items-center sm:gap-4 sm:flex-wrap w-full"
		>
			<p class="w-full max-w-[unset]">Already have an account?</p>

			<RouterLink
				class="pdap-button-secondary flex-1 max-w-full"
				data-test="toggle-button"
				to="/sign-in"
			>
				Log in
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
import { useRouter } from 'vue-router';

const { userId } = useAuthStore();

export const useDataSourceData = defineBasicLoader('/sign-up', async () => {
	if (userId) return new NavigationResult({ path: '/' });
});
</script>

<script setup>
// Imports
import {
	Button,
	FormV2,
	InputText,
	InputPassword,
	Spinner,
} from 'pdap-design-system';
import PasswordValidationChecker from '@/components/PasswordValidationChecker.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';

// Constants
const PASSWORD_INPUTS = [
	{
		autocomplete: 'new-password',
		'data-test': 'password',
		id: 'password',
		name: 'password',
		label: 'Password',
		placeholder: 'Your password',
	},
	{
		autocomplete: 'new-password',
		'data-test': 'confirm-password',
		id: 'confirmPassword',
		name: 'confirmPassword',
		label: 'Confirm Password',
		placeholder: 'Confirm your password',
	},
];
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
	{
		name: 'confirmPassword',
		validators: {
			required: {
				value: true,
			},
			password: {
				message: 'Please confirm your password',
				value: true,
			},
		},
	},
];

// Router
const router = useRouter();

// Store
const auth = useAuthStore();
const user = useUserStore();

// Reactive vars
const passwordRef = ref();
const error = ref(undefined);
const loading = ref(false);

// Functions
// Handlers
/**
 * When signing up: handles clearing pw-match form errors on change if they exist
 */
function onChange(formValues) {
	passwordRef.value.updatePasswordValidation(formValues.password);

	if (error.value) {
		handleValidatePasswordMatch(formValues);
	}
}

function onInput(e) {
	if (e.target.name === 'password') {
		passwordRef.value.updatePasswordValidation(e.target.value);
	}
}

function handleValidatePasswordMatch(formValues) {
	if (formValues.password !== formValues.confirmPassword) {
		if (!error.value) {
			error.value = 'Passwords do not match, please try again.';
		}
		return false;
	} else {
		error.value = undefined;
		return true;
	}
}

async function onSubmit(formValues) {
	const isPasswordValid = passwordRef.value.isPasswordValid();

	if (!isPasswordValid) {
		error.value = 'Password is not valid';
	} else {
		if (error.value) error.value = undefined;
	}

	if (!handleValidatePasswordMatch(formValues) || !isPasswordValid) return;

	try {
		loading.value = true;
		const { email, password } = formValues;

		await user.signupWithEmail(email, password);
		await router.push(auth.redirectTo ?? { path: '/sign-up/success' });
	} catch (err) {
		console.error(err);
		error.value = 'Something went wrong, please try again.';
	} finally {
		loading.value = false;
	}
}
</script>
