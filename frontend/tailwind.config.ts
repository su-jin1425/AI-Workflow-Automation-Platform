import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18202f",
        panel: "#f7f8fb",
        line: "#d7dbe7",
        brand: "#2563eb",
        success: "#188a55",
        danger: "#c2413b",
        warning: "#b7791f"
      }
    }
  },
  plugins: []
};

export default config;
