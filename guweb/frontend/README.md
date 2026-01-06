# Inlayo guweb Frontend - TypeScript

Modern TypeScript-based frontend for Inlayo using Vue 3 + Vite.

## Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Pinia** - State management
- **Axios** - HTTP client

## Project Structure

```
src/
├── api/              # API client and endpoints
│   ├── client.ts     # Axios client setup
│   ├── users.ts      # User API endpoints
│   ├── beatmaps.ts   # Beatmap API endpoints
│   └── leaderboard.ts # Leaderboard API endpoints
├── components/       # Vue components
├── composables/      # Vue composables
│   └── useGameMode.ts
├── stores/           # Pinia stores
│   └── session.ts    # Session store
├── types/            # TypeScript types
│   └── index.ts      # Global types
├── utils/            # Utility functions
│   ├── format.ts     # Number/date formatting
│   ├── mods.ts       # Mods parsing
│   └── grade.ts      # Grade utilities
├── styles/           # Global styles
│   └── main.css
├── pages/            # Page-specific entry points
└── main.ts           # Main entry point
```

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

4. Type checking:
```bash
npm run type-check
```

## Development

The frontend is built with Vite and outputs to `../static/dist/`. The Flask backend serves these files in production.

### Adding a new page

1. Create entry point in `src/pages/pagename.ts`
2. Add to `vite.config.ts` inputs
3. Create Vue component in `src/components/`
4. Update Jinja2 template to load the built file

### API Calls

```typescript
import { userApi } from '@/api/users'

const userData = await userApi.getProfile(userId, mode, mods)
```

### State Management

```typescript
import { useSessionStore } from '@/stores/session'

const sessionStore = useSessionStore()
const isLoggedIn = sessionStore.isAuthenticated
```

## Build Output

Production build outputs to `../static/dist/` with manifest for asset loading.
