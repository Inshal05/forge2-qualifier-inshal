# Architecture

## Brain: Hermes

Hermes owns planning, memory, reusable skills and autonomous progress updates.

- Memory: `memory_store/`
- Skill: `skills/status-report/SKILL.md`
- Autonomous run: `hermes.py` schedules `auto_status`
- Model route: Groq free model for planning (`openai/gpt-oss-120b` or `llama-3.3-70b-versatile`)

## Hands: OpenClaw

OpenClaw owns code edits, command execution and implementation reports.

- Slack config: `openclaw.json`
- Model route: Ollama `qwen2.5-coder` at `http://localhost:11434/v1`
- Expected report format: What I Did / What's Left / What Needs Your Call

## Human-In-The-Loop Channels

- `#sprint-main`: human goal, Hermes plan, approvals and decisions
- `#agent-coder`: Hermes assigns coding work; OpenClaw reports implementation
- `#agent-log`: raw agent activity, autonomous run output and audit trail

## App

- `frontend/`: React/Vite Kanban UI
- `backend/`: Laravel API source skeleton with boards, lists, cards, members and tags

The frontend can demo independently with local storage. The backend is ready to install and migrate on a PHP 8.2+ machine.
