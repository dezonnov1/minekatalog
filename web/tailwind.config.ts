import type {Config} from "tailwindcss";

const config: Config = {
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "var(--background)",
                foreground: "var(--foreground)",
            },
        },
        keyframes: {
            shimmer: {
                '100%': {
                    transform: 'translateX(100%)',
                },
            },
            menu: {
                '0%': {
                    height: '0',
                },
                '100%': {
                    height: '100vh',
                },
            },
            close: {
                '0%': {
                    height: '100vh',
                },
                '100%': {
                    height: '0vh',
                },
            },
        }
    },
    plugins: [],
};
export default config;
