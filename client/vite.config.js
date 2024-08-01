import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import svgLoader from 'vite-svg-loader';
import VueRouter from 'unplugin-vue-router/vite';
import path from 'path';

export default defineConfig({
	plugins: [
		VueRouter({
			routesFolder: 'src/pages',
			extendRoute(route) {
				if (ROUTES_TO_META.has(route.name)) {
					route.meta = { ...route.meta, ...ROUTES_TO_META.get(route.name) };
				}
			},
		}),
		vue(),
		svgLoader({ defaultImport: 'url' }),
	],
	resolve: {
		alias: {
			'@': path.resolve(__dirname, './src'),
		},
	},
	server: {
		port: 8888,
	},
	test: {
		coverage: {
			all: true,
			include: ['src/components/*.vue', 'src/util/**/*.js'],
			provider: 'v8',
			reportsDirectory: './coverage',
		},
		environment: 'happy-dom',
		exclude: ['node_modules'],
		globals: true,
		include: ['src/{components,util}/{__tests__,__spec__}/*.test.js'],
		setupFiles: ['tools/testing/setup.js'],
	},
});

/**
 * To override or add meta to a route, add a tuple to this `Map` which contains the route as the zeroth index and the meta object as the first index
 * Defining in vite.config rather than util/router because of import issues.
 */
const ROUTES_TO_META = new Map([
	[
		'/',
		{
			title: 'Police Data Accessibility Project - Search',
			metaTags: [
				{
					property: 'og:title',
					title: 'Police Data Accessibility Project - Search',
				},
			],
		},
	],
]);
