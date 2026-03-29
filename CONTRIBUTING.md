# Contributing to EZ Agentic Study Buddy

Thanks for your interest in contributing! This project was built as a hands-on learning exercise during the [IBM Building AI Agents and Agentic Workflows Specialization](https://coursera.org/verify/specialization/RNDUBZX0R6KV) on Coursera — and it's open for anyone who wants to learn agentic AI by building.

Whether you're fixing a bug, improving the UI, adding a feature, or just cleaning up docs — all contributions are welcome.

---

## Security

- Put **API keys only in your local `.env`** (copied from `.env.example`). **Do not commit `.env`**, real keys, or token-bearing URLs.
- **Never** add live **Groq** or **OpenAI** keys to the repository, sample configs, tests, or documentation. If a key was ever pushed or leaked, **rotate it immediately** in the provider’s console and assume it is no longer secret.

---

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 18+ (for the React frontend)
- A free [Groq API key](https://console.groq.com) (for LLM-dependent features/tests)

### Setup

```bash
# 1. Fork the repo, then clone your fork
git clone https://github.com/<your-username>/ez-agentic-study-buddy.git
cd ez-agentic-study-buddy

# 2. Install Python dependencies (backend + dev: ruff, mypy, pytest).
#    uv.lock is committed — use --locked so your env matches CI.
uv sync --extra web --group dev --locked

# 3. Configure environment
cp .env.example .env
# Edit .env → add your GROQ_API_KEY (never commit .env — see Security above)

# 4. Install frontend dependencies (lockfile lives in webui/ only)
cd webui
npm install
cd ..

# 5. Verify everything works
uv run pytest -q
```

### Running the App

```bash
# Backend
uv run uvicorn webapi.main:app --reload --port 8000

# Frontend (separate terminal)
cd webui
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

---

## How to Contribute

### 1. Find Something to Work On

- Check [open issues](https://github.com/ebinzacharias/ez-agentic-study-buddy/issues) — look for `good first issue` or `help wanted` labels.
- Have your own idea? Open an issue first to discuss it.

### 2. Branch from `develop`

We use `develop` as the integration branch. Create your feature branch from there:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

**Branch naming conventions:**

| Prefix | Use |
|--------|-----|
| `feature/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation only |
| `test/` | Test additions or fixes |
| `refactor/` | Code restructuring (no behavior change) |

### 3. Make Your Changes

- Keep commits focused — one logical change per commit.
- Write clear commit messages:
  ```
  feat: add progress bar to React UI
  fix: handle empty file upload gracefully
  docs: add API examples to USAGE.md
  test: add quiz retry edge case coverage
  ```

### 4. Run the Checks Locally

Before pushing, make sure everything passes (after `uv sync --extra web --group dev --locked`):

```bash
uv run ruff check .
uv run mypy .
uv run pytest
```

**Ruff** is pinned to **0.11.7** in `[dependency-groups].dev` and matches the revision **v0.11.7** in `.pre-commit-config.yaml`. **mypy** uses `ignore_missing_imports = false` in `pyproject.toml` so missing stubs are reported project-wide; the optional **pymupdf** import (`fitz`) is annotated with `# type: ignore[import-not-found]` because that dependency is not in the default lockfile. **`return-value`** and **`operator`** remain disabled because FastAPI handlers often return `JSONResponse` alongside `dict` return types, and LangChain runnables are typed narrowly enough to produce noisy false positives until those callsites are refined.

These same checks run in CI on every PR.

### 5. Open a Pull Request

- Target your PR at the `develop` branch (not `main`).
- Fill in what you changed and why.
- Link to the related issue if there is one.
- PRs are merged after review. Don't worry about being perfect — feedback is part of the process.

---

## Project Structure at a Glance

```
agent/
  core/       # Agent loop, state, decision rules, retry manager, tool executor
  chains/     # LCEL chain composition (observe → decide → act)
  tools/      # Planner, Teacher, Quizzer, Evaluator, Adapter
  agents/     # Agent classes (Planner, Teacher, Quizzer, Adapter)
  utils/      # LLM client, content loader
webapi/
  main.py     # FastAPI backend — sessions, upload, plan, teach, quiz, evaluate
webui/
  src/        # React frontend (Vite)
scripts/      # Pytest test suite
LEARNINGS/    # Step-by-step build notes & agentic AI concepts
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed design and diagrams.

---

## Code Style

- **Python**: We use [ruff](https://docs.astral.sh/ruff/) **0.11.7** (same as [pre-commit](https://pre-commit.com/) and CI). No `ruff.toml` — project defaults are fine.
- **Types**: [mypy](https://mypy-lang.org/) for type checking. Use type hints on function signatures. See §4 above for why a subset of error codes is suppressed.
- **Models**: Use [Pydantic](https://docs.pydantic.dev/) for data models and validation.
- **Frontend**: Standard React/JSX. No strict formatter enforced yet — just keep it readable.

---

## Testing

Tests live in `scripts/`. Key conventions:

- **Offline tests** (no API key needed): `test_decision_rules.py`, `test_quizzer_schema_validation.py`
- **LLM tests**: Auto-skip when `GROQ_API_KEY` is not set (via `pytest.mark.skipif`)
- **Web tests**: Auto-skip when `fastapi` is not installed (via `pytest.importorskip`)

If you add a new feature, add a test. If you fix a bug, add a regression test.

```bash
# Run a specific test file
uv run python -m pytest scripts/test_decision_rules.py -v

# Run all tests
uv run python -m pytest -q
```

---

## Ideas for Contributions

Not sure where to start? Here are some areas that would make a real impact:

- 🎨 **Frontend improvements** — Progress indicators, better quiz UI, responsive design
- 💾 **Persistent sessions** — Replace in-memory `SESSIONS` dict with SQLite or Redis
- 📄 **PDF preview** — Show uploaded content preview in the UI
- 📊 **Learning analytics** — Visualize scores, progress, difficulty changes over time
- 🌐 **Deploy** — Add a Dockerfile or Railway/Render config for one-click deploy
- 🧪 **More tests** — Edge cases, integration tests, frontend tests
- 📝 **Documentation** — Tutorials, API examples, LEARNINGS additions

---

## Code of Conduct

Be kind, be constructive, and assume good intent. This is a learning project — everyone is here to grow.

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](./LICENSE).

---

Questions? Open an issue or start a discussion. Happy building! 🚀
