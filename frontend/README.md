# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## API adapter and mock mode

The frontend uses a single canonical API adapter at `src/services/api.js` which normalizes backend responses into the UI model. Use this adapter from all pages/components so backend shape changes don't require UI rewrites.

- Toggle mock mode with `VITE_USE_MOCK=true` to use `src/mock/demoSession.json` and localStorage fallbacks.
- Configure `VITE_API_BASE_URL` to point the adapter at your backend in production or local testing.

Example: `VITE_USE_MOCK=true VITE_API_BASE_URL=https://guardian-ai-api-c2d5132c.fastapicloud.dev npm run dev`
