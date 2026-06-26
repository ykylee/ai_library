# ai_library

**AI Agent Library — OKF (Open Knowledge Format) bundle engine + LLM enrich agents + SvelteKit query UI.**

> 본 repo 는 **standalone** 으로 운영되는 reference implementation 이다. vendor-neutral + 사외 tier (public, MIT) + 외부 인프라 의존 0 + 다른 backend 연결 ❌ + OIDC ❌.

## 1차 출처 (Provenance)

| 출처 | 결정 | 본 repo 의 흡수 위치 |
| --- | --- | --- |
| [Google Cloud `Open Knowledge Format v0.1`](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md) (2026-06-12 발표, Apache 2.0) | 1 concept = 1 .md, frontmatter `type` 1개 필수, 8종 type enum, `x_<publisher>_*` prefix 확장 | `docs/adr/0002-okf-adoption.md` + `backend/okf/SPEC.md` |
| [본 repo ADR-0001 founding charter](docs/adr/0001-founding-charter.md) (2026-06-26) | 사외 tier + standalone 정책 + 0.0.1-alpha 시작 | `docs/adr/0001-founding-charter.md` |
| [본 repo roadmap v0.0.1](docs/planning/v0.0.1-ai-library-roadmap.md) | M-v0.0.1-alpha~v0.1.0 7 마일스톤 | `docs/planning/v0.0.1-ai-library-roadmap.md` |

## 디렉터리 구조

```
ai_library/
├── README.md                          # 본 파일
├── AGENTS.md                          # AI 워커 workflow 진입 규칙
├── LICENSE                            # MIT
├── .gitignore
├── web/                               # SvelteKit 2 + Svelte 5 frontend
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── app.html / app.css / app.d.ts
│       ├── lib/                       # types / api / path-y / components
│       │   ├── api.ts / api.test.ts
│       │   ├── path-y.ts / path-y.test.ts
│       │   ├── types.ts / types.test.ts
│       │   └── components/
│       │       ├── Sidebar.svelte
│       │       └── PathYDevFixture.svelte
│       └── routes/
│           ├── +layout.svelte / +page.svelte
│           ├── audit/+page.svelte
│           ├── bundles/+page.svelte
│           │   └── [name]/+page.svelte
│           ├── concepts/+page.svelte
│           │   └── [type]/[name]/+page.svelte
│           ├── ingest/+page.svelte
│           └── raw/+page.svelte
├── backend/                           # FastAPI + OKF bundle engine + Pi LLM enrich placeholder
│   ├── pyproject.toml                 # name = "ai-library-backend", version = "0.0.1"
│   ├── .env.example
│   ├── README.md
│   ├── src/
│   │   ├── main.py                    # FastAPI app entry + typer CLI
│   │   ├── config.py                  # 4-priority REPO_ROOT auto-detect
│   │   ├── api/
│   │   │   └── v1/                    # /api/v1/ 6 router placeholder
│   │   ├── sources/
│   │   │   └── base.py                # SourcePlugin ABC
│   │   ├── okf/
│   │   │   └── envelope.py            # OKF bundle wrapping (placeholder)
│   │   └── llm/
│   │       └── pi_enrich.py           # Pi LLM enrich placeholder
│   ├── okf/
│   │   └── SPEC.md                    # OKF v0.1 in-repo 사본 (Apache 2.0)
│   ├── var/                           # runtime state (gitignored)
│   │   ├── raw/
│   │   ├── concepts/
│   │   ├── cross-link/
│   │   └── audit/
│   └── scripts/
│       ├── dev.sh                     # uvicorn dev server
│       └── smoke.sh                   # 8 smoke test
└── docs/
    ├── adr/
    │   ├── 0001-founding-charter.md   # 본 repo 의 founding charter
    │   └── 0002-okf-adoption.md       # OKF v0.1 채택 결정
    └── planning/
        └── v0.0.1-ai-library-roadmap.md    # 본 repo 의 umbrella roadmap
```

## Quick start

```bash
# web/ frontend (단독 실행 가능, backend 없이도 viz.html 자가 viewer standalone)
cd web
npm ci
npm run dev          # SvelteKit dev server (http://localhost:5173)

# backend/ (M-v0.0.2+ 본격 구현)
cd backend
pip install -e .
ai-library serve                     # FastAPI server (pyproject.toml [project.scripts] entry)

# standalone 검증 (M-v0.0.2 release 시점에 활성화)
bash scripts/check_standalone_drift.sh
bash scripts/check_network_isolation.sh
```

## Vendor import (downstream consumer)

Downstream consumer 가 본 repo 를 vendor import 패턴으로 들여올 때:

```bash
# downstream vendored re-introduce
mkdir -p vendor/ai_library
cp -R /path/to/ai_library/{web,backend,docs,LICENSE,README.md,AGENTS.md} vendor/ai_library/

# vendor smoke 2종
cd vendor/ai_library/web && npm ci && npm run build
cd vendor/ai_library/backend && pip install -e . && python -m pytest
```

## Status

- **M-v0.0.1-alpha** (founding, 2026-06-26): Frontend shell (SvelteKit 2 + Svelte 5 + vitest) + backend skeleton (FastAPI + OKF + Pi LLM placeholder) + 5종 source plugin (`mock` + Gitea 4) + standalone 운영 + ADR-0001/0002.
- **M-v0.0.2** (2026-Q3): FastAPI app + 6 router (17 endpoint) + 8 smoke test + var/ 초기화.
- **M-v0.0.3** (2026-Q3): Pi LLM enrich 활성화 (sdk mode default).
- **M-v0.0.4** (2026-Q4): DB 듀얼 모드 + 5종 source plugin PoC + 옵션 env (metrics / hrdb).
- **M-v0.0.5** (2026-Q4): cross-link reverse index + governance audit log dashboard.
- **M-v0.0.6** (2027-Q1): API versioning v0-3 (dual endpoint support) + 12개월 deprecation policy 운영.
- **M-v0.1.0** (2027-Q2): Multi-vendor LLM (Pi → OpenAI / Anthropic / Gemini 옵션) — 첫 minor version (1차 "feature complete").

상세: [`docs/planning/v0.0.1-ai-library-roadmap.md`](docs/planning/v0.0.1-ai-library-roadmap.md).

## Cross-reference (본 repo 내부)

- [`AGENTS.md`](AGENTS.md) — AI 워커 workflow 진입 규칙 (tier self-check 포함)
- [`docs/adr/0001-founding-charter.md`](docs/adr/0001-founding-charter.md) — founding charter (tier / standalone 정책 / version 정책)
- [`docs/adr/0002-okf-adoption.md`](docs/adr/0002-okf-adoption.md) — OKF v0.1 채택 결정
- [`docs/planning/v0.0.1-ai-library-roadmap.md`](docs/planning/v0.0.1-ai-library-roadmap.md) — 7 마일스톤 roadmap
- [`backend/okf/SPEC.md`](backend/okf/SPEC.md) — OKF v0.1 in-repo 사본 (Apache 2.0)

## Tier 정책

본 repo 는 **사외 tier** (vendor-neutral + 외부 인프라 의존 0 + 다른 backend 연결 ❌ + OIDC ❌). 본 저장소에서 사내 한정 정보 (예: `DEVHUB_*` / `kc.internal.example.com` / `devhub.example.com` / `172.16.0.0/12` / `internal-registry.example.com` / 특정 NAS hostname) 의 단일 occurrence ❌. 사내 한정 시크릿/호스트 도입 시 ADR-0001 §2.2 self-check + §2.3 standalone 정책 으로 자동 fail.

## License

MIT — see [LICENSE](./LICENSE).