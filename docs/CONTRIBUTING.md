# Contributing

## Workflow
- Fork & branch from `main`
- `make fmt && make lint`
- Add tests for new features
- Submit PR with clear description

## Coding Standards
- Rust: `clippy` clean, `rustfmt` enforced
- TS: ESLint + Prettier
- Commits: `feat:`, `fix:`, `docs:`, `chore:`

## Testing
- `anchor test --skip-local-validator`
- Add integration tests for router<->slab flows
