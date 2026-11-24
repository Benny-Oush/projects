# Dad Jokes

A single-page React app for browsing dad jokes, translating them into Hebrew, and keeping a personal list of favorites in the browser.

## Features

- Fetches a random dad joke from the [icanhazdadjoke](https://icanhazdadjoke.com/) API.
- Translates jokes into Hebrew.
- Saves favorite jokes in `localStorage`, so they remain available after a page refresh.
- Lets users remove favorites or translate them from the Favorites page.
- Displays loading feedback while a joke or translation is being fetched.
- Uses client-side routes for the Home, Browse, and Favorites pages.

## Tech Stack

- React 19
- React Router DOM
- Vite
- JavaScript (ES modules)
- CSS

## Getting Started

### Prerequisites

Install [Node.js](https://nodejs.org/) and [pnpm](https://pnpm.io/).

### Installation

```bash
git clone <repository-url>
cd jokes
pnpm install
```

### Run Locally

```bash
pnpm dev
```

Vite will print the local development URL in the terminal.

## Pages

| Route | Description |
| --- | --- |
| `/` | Welcome page. |
| `/brows` | Shows a random joke, with translation and favorite controls. |
| `/favorites` | Displays the jokes saved by the user. |

## Available Scripts

| Command | Description |
| --- | --- |
| `pnpm dev` | Starts the development server. |
| `pnpm build` | Creates an optimized production build in `dist/`. |
| `pnpm preview` | Serves the production build locally. |
| `pnpm lint` | Runs ESLint checks. |

## Project Structure

```text
src/
├── assets/       # Background image and bookmark icon
├── components/   # Routed pages and reusable UI components
├── utils/        # API, translation, and localStorage helpers
├── App.jsx       # Router configuration
└── main.jsx      # React entry point
```

## APIs and Storage

- Joke data comes from the [icanhazdadjoke API](https://icanhazdadjoke.com/api).
- Translation requests use Google Translate's public endpoint.
- Favorite joke IDs are stored locally under the `liked` key in `localStorage`.
- When a fetched joke is already saved, its bookmark is shown as active.

## Notes

Translations can affect wordplay and punchlines, so the original English version is always available with one click.

## Quality Checks

```bash
pnpm lint
pnpm build
```

The first command checks code quality with ESLint; the second creates a production-ready build.
