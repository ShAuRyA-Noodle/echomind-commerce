# Contributing to Echomind Commerce

Thanks for your interest. This is a hackathon submission for Track 5 of the [KASPARRO Agentic Commerce Hackathon 2026](https://kasparro.com), so the contribution surface is intentionally narrow during the build window (10-20 May 2026). The repo will open up post-submission.

## Ground rules

1. **No em dashes** anywhere in code, docs, prompts, or commit messages. CI enforces this.
2. **Documentation gate is hard.** Every PR that touches behavior must update [docs/DECISION_LOG.md](docs/DECISION_LOG.md) with a new entry following the existing format (Decision / Considered / Chose / Reason / Tradeoff / Implication).
3. **Atomic commits.** One concern per commit. Conventional Commits style: `feat(domain): ...` / `fix(domain): ...` / `docs(domain): ...` / `chore: ...` / `test(domain): ...`. The git history is a graded artifact (see [docs/PRODUCT_DOC.md](docs/PRODUCT_DOC.md) section on docs-first Day 1).
4. **No mocks in production paths.** Real Shopify, real Neo4j, real LLMs. Mocks belong in `backend/tests/` only.
5. **Calibration discipline.** The 5-bucket label is the load-bearing trust signal. Never claim numerical accuracy you have not measured.

## Development setup

See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for full environment setup. Quick start:

```bash
git clone https://github.com/ShAuRyA-Noodle/echomind-commerce.git
cd echomind-commerce
cp .env.example .env  # fill in keys
docker compose up
```

## Code style

### Python (backend)
- Python 3.11+, `from __future__ import annotations`, type hints everywhere.
- pydantic 2 for any data crossing the network or LLM boundary.
- `ruff check .` must pass.
- Tests in `backend/tests/`, run via `pytest`.

### TypeScript (frontend)
- TypeScript strict mode, no `any`.
- shadcn/ui copy-in components only. No Material UI / Chakra / Ant.
- Tailwind utilities, not CSS-in-JS.
- `npm run lint` and `npm run type-check` must pass.

### Cypher
- All queries live in `backend/graph/queries.py` as named constants.
- Idempotent MERGE on `id` for all writes.
- `IF NOT EXISTS` on all DDL.

### Prompts
- All LLM prompts live in `backend/config/prompts.py`. No inline f-strings or template literals in service code.
- Templates use named placeholders (e.g. `{phase}`, `{graph_stats}`), `.format()`-rendered at call time.
- Calibration discipline: every reasoning prompt asks for a confidence score and forbids fabrication outside the supplied subgraph.

## PR checklist

Before opening a PR:

- [ ] `make test` passes.
- [ ] `make lint` passes.
- [ ] No em dashes (CI will reject).
- [ ] DECISION_LOG.md updated if behavior changed.
- [ ] CHANGELOG.md updated under `[Unreleased]`.
- [ ] No secrets committed (`git diff` and check `.env` is gitignored).
- [ ] Tests added/updated for the change.

## Commit message format

```
<type>(<scope>): <imperative summary, ~70 chars>

<optional body explaining why>

<optional footer with refs / breaking changes>
```

Types: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `perf`.
Scope examples: `socratic`, `agents`, `diagnose`, `fix`, `graph`, `api`, `frontend/audit`.

## Reporting security issues

See [SECURITY.md](SECURITY.md) for vulnerability disclosure. Do not open public issues for security concerns.

## License

By contributing, you agree your contribution is licensed under the [MIT License](LICENSE).
