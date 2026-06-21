# Forge 2 Qualifier

This repo contains the Forge 2 qualifier submission pieces:

- Hermes brain scaffold with memory, skill discovery and autonomous status logging.
- OpenClaw Slack configuration template with secrets loaded from environment variables.
- A tiny Trello-style Kanban board: React/Vite frontend plus Laravel API source skeleton.
- Evidence placeholders for Slack logs, autonomous runs and the human-in-the-loop workflow.

## Kanban Features

- Boards -> Lists -> Cards
- Create and edit cards
- Move cards between lists
- Tags / coloured labels
- Board members and card assignment
- Due dates with overdue visual flagging

The React app persists data in browser local storage so it can be demoed immediately even before the Laravel API is deployed.

## Run Locally

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, usually `http://127.0.0.1:5173`.

### Backend API

PHP and Composer were not available on this workstation, so the Laravel backend is committed as source ready for a PHP 8.2+ machine.

```bash
cd backend
composer install
cp .env.example .env
touch database/database.sqlite
php artisan key:generate
php artisan migrate
php artisan serve
```

API base URL: `http://127.0.0.1:8000/api`.

## Models Used

- Hermes brain: Groq free model such as `openai/gpt-oss-120b` or `llama-3.3-70b-versatile` for planning.
- OpenClaw hands: Ollama `qwen2.5-coder` through `http://localhost:11434/v1` for coding tasks.

Reasoning: the brain benefits from stronger planning/context, while the coding agent can run locally and avoid free-tier rate limits.

## Required Evidence

- Put Slack screenshots or copied logs in `slack-export/`.
- Keep real tokens only in `.env`; never commit them.
- Paste the key human -> Hermes plan -> OpenClaw code/report loop into `agent-log.md`.
- Add the deployed frontend URL and walkthrough video link here before submitting.

Live URL: TODO
Walkthrough video: TODO
