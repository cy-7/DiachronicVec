/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ancient: "#D97706",
        medieval: "#4F46E5",
        modern: "#059669",
        contemporary: "#DB2777",
        surface: "#1a1a2e",
        panel: "#16213e",
        accent: "#0f3460",
      }
    }
  },
  plugins: [],
}
