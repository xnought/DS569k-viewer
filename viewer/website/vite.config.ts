import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// https://vitejs.dev/config/
export default defineConfig({
	base: "/DS569k/",
	server: {
		port: 4321,
	},
	plugins: [svelte()],
});
