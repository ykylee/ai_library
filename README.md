# ai_library

**AI Agent Library — OKF (Open Knowledge Format) bundle engine + LLM enrich agents + SvelteKit query UI.**

> 본 repo 는 **2026-06-23** `DevHub v0.2.0` 의 `backend-knowledge/` 디렉터리를 **외부 repo 로 extraction** 한 결과물. vendor import pattern 의 **역방향 정공법** — 외부 발매자 (= 본 repo) 가 DevHub 의 ADR-0037 OKF 채택 + ADR-0038 backend-knowledge 신설 결정을 흡수.

## 1차 출처 (Provenance)

| 흡수 source | DevHub 측 결정 | 본 repo 의 흡수 위치 |
| --- | --- | --- |
| [DevHub ADR-0037 OKF v0.1 채택](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0037-okf-adoption.md) | Google Cloud `Open Knowledge Format v0.1` (2026-06-12 발표, Apache 2.0, 1 concept = 1 .md, frontmatter `type` 1개 필수, 8종 type enum, `x_devhub_*` prefix 확장) | `docs/adr/0002-okf-adoption.md` |
| [DevHub ADR-0038 backend-knowledge 신설](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0038-backend-knowledge-creation.md) | 외부 시스템 7종 source 만 단방향 (Gitea 4 sub-plugin + homelab + metrics + hrdb), M-v0.2.0~v0.3.0 6 마일스톤, **완전 standalone** (다른 backend 연결 ❌, OIDC ❌) | `docs/adr/0001-ai-library-extraction.md` + `docs/planning/v0.3.0-ai-library-roadmap.md` |
| DevHub umbrella `release_v0-2_roadmap.md` §1.2 G7 standalone 정책 | vendor-neutral + git 가능 + agent-friendly 한 지식 표현 | `docs/planning/v0.3.0-ai-library-roadmap.md` §1.2 G7 흡수 |

## 디렉터리 구조

```
ai_library/
├── README.md                          # 본 파일 (1차 출처 + 흡수 정공법)
├── AGENTS.md                          # 본 repo 의 4-워커 분업 + tier 정책 (DevHub 와 무관)
├── LICENSE                            # MIT (ykylee)
├── .gitignore                         # node_modules/ / .svelte-kit/ / var/ / __pycache__/ / .env*
├── web/                               # SvelteKit 2 + Svelte 5 frontend shell (DevHub backend-knowledge/web/ 이식)
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── app.html / app.css / app.d.ts
│       ├── lib/
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
├── backend/                           # FastAPI + OKF bundle engine + Pi (pi.dev) LLM enrich (M-v0.3.0+ 본격 구현)
│   ├── pyproject.toml                  # Python 3.13+ / FastAPI / Pydantic v2 / Pi SDK
│   ├── .env.example
│   ├── README.md
│   ├── src/
│   │   ├── main.py                     # FastAPI app entry + typer CLI (ai-library 진입점)
│   │   ├── config.py                   # 4-priority REPO_ROOT auto-detect (§2.4 정합)
│   │   ├── api/
│   │   │   └── v0_2/                   # /api/v0-2/ 6 router placeholder (ingest / bundles / concepts / raw / audit / graph)
│   │   ├── sources/
│   │   │   └── base.py                 # SourcePlugin ABC (M-v0.3.0 PoC 의 1차 작성 정공법)
│   │   ├── okf/
│   │   │   └── envelope.py             # OKF bundle wrapping (M-v0.3.0+ make_envelope / parse_envelope)
│   │   └── llm/
│   │       └── pi_enrich.py            # Pi LLM enrich placeholder (M-v0.3.1+ sdk mode)
│   ├── okf/
│   │   └── SPEC.md                     # OKF v0.1 in-repo 적응 (Apache 2.0, Google SPEC.md 1차 출처)
│   ├── var/
│   │   ├── raw/                        # 1차 raw 데이터 (봉투 암호화 M-v0.3.0+ 정합)
│   │   ├── concepts/                   # OKF bundle 디렉터리 (1 concept = 1 .md, 5 카테고리 × 8 type)
│   │   ├── cross-link/                 # cross-link reverse index (§3.5.6)
│   │   └── audit/                      # governance audit log (§3.6.6)
│   └── scripts/
│       ├── dev.sh                      # uvicorn dev server
│       └── smoke.sh                    # 8 smoke test (DevHub §6.5.4 E2E 정합)
└── docs/
    ├── adr/
    │   ├── 0001-ai-library-extraction.md   # 본 repo 의 핵심 ADR — DevHub ADR-0038 흡수 + extraction 결정
    │   └── 0002-okf-adoption.md            # DevHub ADR-0037 흡수
    └── planning/
        └── v0.3.0-ai-library-roadmap.md    # 본 repo 의 umbrella doc (DevHub umbrella §1.2 G7 standalone 정책 흡수)
```

## Quick start

```bash
# web/ frontend (단독 실행 가능, backend 없이 viz.html 자가 viewer 만 standalone)
cd web
npm ci
npm run dev          # SvelteKit dev server

# backend/ (M-v0.3.0+ 본격 구현)
cd backend
pip install -e .
ai-library serve                      # FastAPI server (pyproject.toml [project.scripts] entry)

# standalone 검증 (M-v0.3.0 release 시점에 활성화)
bash scripts/check_standalone_drift.sh
bash scripts/check_network_isolation.sh
```

## Vendor import (DevHub 측)

DevHub 측에서 본 repo 를 vendor import 패턴으로 들여올 때 (vendor import 역방향 — 외부 발매자 → 본 repo):

```bash
# DevHub 측 vendored re-introduce
mkdir -p vendor/ai_library
cp -R /Users/yklee/repos/ai_library/{web,backend,docs,LICENSE,README.md,AGENTS.md} vendor/ai_library/

# vendor smoke 2종
cd vendor/ai_library/web && npm ci && npm run build  # web frontend build OK
cd vendor/ai_library/backend && pip install -e . && python -m pytest  # backend pytest OK
```

## Status

- **2026-06-23**: Initial commit + Gitea push (DevHub v0.2.0 backend-knowledge/ extraction, vendor import pattern 역방향).
- **M-v0.3.0-alpha**: FastAPI backend 본격 구현 (1차 = source plugin 7종 PoC = Gitea 4 + homelab + metrics + hrdb).
- **M-v0.3.0**: 1차 release (rule-based enricher + OKF bundle CRUD + Ingest/Curate/Query 14 endpoint).
- **M-v0.3.1**: Pi (pi.dev) LLM enrich 활성화 (1 vendor).
- **M-v0.3.2**: hrdb source + GDPR/PII compliance (§3.6.6.5 정합).
- **M-v0.3.3**: Cross-link 자동 resolution (§3.5.7 + §3.5.8 false positive rollback).
- **M-v0.4.0**: Multi-vendor LLM (Pi → OpenAI / Anthropic / Gemini 추가), deprecation policy 12개월.

## Cross-reference (DevHub ↔ 본 repo)

- DevHub umbrella `release_v0-2_roadmap.md` §1.2 G1 redirect: 본 repo 의 `yklee/ai_library` Gitea URL
- DevHub umbrella §9 변경 이력 2026-06-23 row: 본 repo 의 extraction 결정 row
- DevHub ADR-0037 §6 Supersession row: 본 repo 의 `docs/adr/0002-okf-adoption.md`
- DevHub ADR-0038 §6 Supersession row: 본 repo 의 `docs/adr/0001-ai-library-extraction.md`
- DevHub child doc `external-integrations-agentic-rag-roadmap.md` §8 row: 본 repo 의 source plugin redirect
- DevHub AGENTS.md line 29 redirect: 본 repo 의 standalone 정책 + 외부 repo reference

## Tier 정책

본 repo 는 **사외 tier** (DevHub 와 무관, vendor-neutral + 외부 인프라 의존 0 + 다른 backend 연결 ❌ + OIDC ❌). 본 저장소에서 사내 한정 정보 (`DEVHUB_KEYCLOAK_*` / `kc.internal.example.com` / `devhub.example.com` / `172.16.0.0/12` / `internal-registry.example.com`) 의 단일 occurrence ❌. 사내 한정 시크릿/호스트 도입 시 §2.4 standalone 검증 매트릭스 + §2.6 network 정책 으로 자동 fail.

## License

MIT — see [LICENSE](./LICENSE).
