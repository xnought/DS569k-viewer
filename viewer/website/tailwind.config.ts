import flowbitePlugin from "flowbite/plugin";

import type { Config } from "tailwindcss";

export default {
	content: [
		"./src/**/*.{html,js,svelte,ts}",
		"./node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}",
	],
	darkMode: "class",
	theme: {
		extend: {
			colors: {
				// flowbite-svelte
				primary: {
					"50": "#fffee4",
					"100": "#fffec4",
					"200": "#fffe90",
					"300": "#faff50",
					"400": "#eeff00",
					"500": "#d1e600",
					"600": "#a2b800",
					"700": "#7a8b00",
					"800": "#606d07",
					"900": "#505c0b",
					"950": "#2a3400",
				},
			},
		},
	},

	plugins: [flowbitePlugin],
} as Config;
