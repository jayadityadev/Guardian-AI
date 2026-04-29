/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      "colors": {
              "on-primary-fixed": "#100069",
              "on-secondary-container": "#006b7a",
              "primary": "#4d41df",
              "surface-variant": "#e0e0ff",
              "background": "#fbf8ff",
              "surface-container-highest": "#e0e0ff",
              "tertiary-fixed": "#ffd9e3",
              "on-primary": "#ffffff",
              "outline-variant": "#c7c4d8",
              "surface-container-high": "#e7e6ff",
              "surface-container-lowest": "#ffffff",
              "error": "#ba1a1a",
              "inverse-primary": "#c4c0ff",
              "outline": "#777587",
              "surface": "#fbf8ff",
              "on-primary-fixed-variant": "#3622ca",
              "inverse-on-surface": "#f1efff",
              "inverse-surface": "#2c2e49",
              "error-container": "#ffdad6",
              "secondary-fixed": "#a3eeff",
              "primary-container": "#675df9",
              "on-secondary-fixed": "#001f25",
              "tertiary-container": "#cd3b7d",
              "secondary": "#006877",
              "on-surface-variant": "#464555",
              "on-secondary-fixed-variant": "#004e5a",
              "on-surface": "#171933",
              "on-error": "#ffffff",
              "on-tertiary-fixed-variant": "#8d004e",
              "secondary-container": "#8eeafe",
              "surface-tint": "#4f44e2",
              "primary-fixed": "#e3dfff",
              "on-tertiary-container": "#fffbff",
              "on-background": "#171933",
              "on-tertiary": "#ffffff",
              "surface-container-low": "#f4f2ff",
              "surface-container": "#eeecff",
              "surface-dim": "#d7d7fa",
              "secondary-fixed-dim": "#77d4e7",
              "tertiary": "#ac1e64",
              "on-error-container": "#93000a",
              "on-secondary": "#ffffff",
              "surface-bright": "#fbf8ff",
              "on-primary-container": "#fffbff",
              "on-tertiary-fixed": "#3e001f",
              "primary-fixed-dim": "#c4c0ff",
              "tertiary-fixed-dim": "#ffb0ca"
      },
      "borderRadius": {
              "DEFAULT": "0.25rem",
              "lg": "0.5rem",
              "xl": "0.75rem",
              "full": "9999px",
              "2xl": "1rem",
              "3xl": "1.5rem"
      },
      "spacing": {
              "xs": "4px",
              "xl": "64px",
              "base": "8px",
              "md": "24px",
              "gutter": "24px",
              "lg": "40px",
              "container-max": "1440px",
              "sm": "12px",
              "2xl": "96px"
      },
      "fontFamily": {
              "body-md": [
                      "Inter"
              ],
              "body-lg": [
                      "Inter"
              ],
              "headline-md": [
                      "Inter"
              ],
              "display-lg": [
                      "Inter"
              ],
              "label-md": [
                      "Inter"
              ],
              "headline-lg": [
                      "Inter"
              ],
              "display-sm": [
                      "Inter"
              ],
              "label-sm": [
                      "Inter"
              ]
      },
      "fontSize": {
              "body-md": [
                      "16px",
                      {
                              "lineHeight": "1.5",
                              "fontWeight": "400"
                      }
              ],
              "body-lg": [
                      "18px",
                      {
                              "lineHeight": "1.6",
                              "fontWeight": "400"
                      }
              ],
              "headline-md": [
                      "20px",
                      {
                              "lineHeight": "1.4",
                              "fontWeight": "600"
                      }
              ],
              "display-lg": [
                      "48px",
                      {
                              "lineHeight": "1.1",
                              "letterSpacing": "-0.02em",
                              "fontWeight": "700"
                      }
              ],
              "label-md": [
                      "14px",
                      {
                              "lineHeight": "1.2",
                              "letterSpacing": "0.02em",
                              "fontWeight": "500"
                      }
              ],
              "headline-lg": [
                      "24px",
                      {
                              "lineHeight": "1.3",
                              "fontWeight": "600"
                      }
              ],
              "display-sm": [
                      "36px",
                      {
                              "lineHeight": "1.2",
                              "letterSpacing": "-0.01em",
                              "fontWeight": "600"
                      }
              ],
              "label-sm": [
                      "12px",
                      {
                              "lineHeight": "1.2",
                              "fontWeight": "600"
                      }
              ]
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries')
  ],
}
