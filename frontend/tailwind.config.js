/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        iq: {
          bg: "#F9FAFB",
          text: "#111827",
          sub: "#6B7280",
          border: "#E5E7EB",
          primary: "#3B82F6",
          danger: "#EF4444",
          warning: "#F97316",
          success: "#10B981",
          amber: "#F59E0B",
          hover: "#F3F4F6",
          body: "#374151",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(0,0,0,0.06), 0 1px 2px 0 rgba(0,0,0,0.04)",
        "card-hover":
          "0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.05)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "slide-in-right": {
          "0%": { opacity: "0", transform: "translateX(24px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-468px 0" },
          "100%": { backgroundPosition: "468px 0" },
        },
        "pulse-soft": {
          "0%, 100%": { transform: "scale(1)" },
          "50%": { transform: "scale(1.03)" },
        },
        "bounce-soft": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-2px)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.2s ease",
        "slide-up": "slide-up 0.2s ease",
        "slide-in-right": "slide-in-right 0.3s ease",
        shimmer: "shimmer 1.2s linear infinite",
        "pulse-soft": "pulse-soft 1.8s ease-in-out infinite",
        "bounce-soft": "bounce-soft 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};