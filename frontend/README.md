# Frontend

This project uses a modern web frontend rather than Python files for UI/UX.

Recommended stack:
- React + TypeScript
- Vite for the development/build tool
- Tailwind CSS for styling
- shadcn/ui for accessible UI components
- React Router for dashboard navigation

Python remains the backend/automation language. The frontend communicates with the backend through HTTP APIs and should never contain secrets such as API keys, browser-session data, or Meesho/Instagram credentials.

Suggested structure:

```text
frontend/
  src/
    components/
    pages/
    layouts/
    hooks/
    lib/
    types/
    api/
    App.tsx
    main.tsx
  index.html
  package.json
  vite.config.ts
  tsconfig.json
```

Planned dashboard sections:
- Overview / daily automation status
- Trend research
- Selected product and all reference images
- Video generation status
- Scheduled jobs
- Meesho browser connection status
- Instagram browser connection status
- Generated videos/history
- Settings and safe secret configuration

Do not put passwords, cookies, session profiles, or API keys into frontend source code.
