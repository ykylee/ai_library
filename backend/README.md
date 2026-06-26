# ai_library — backend

**AI Agent Library backend (FastAPI + OKF + Pi LLM enrich). 본 repo 의 standalone 운영 backend.**

- **Status**: M-v0.0.1-alpha (founding scaffold, 2026-06-26)
- **Source-of-truth**: 본 디렉터리. 외부 umbrella / monorepo / vendor import 패턴의 vendored re-introduce 가능 (downstream consumer 결정).
- **1차 출처 결정**: [Google Cloud `Open Knowledge Format v0.1`](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md) (Apache 2.0, spec baseline) + [본 repo ADR-0001 founding charter](../docs/adr/0001-founding-charter.md) (tier / standalone 정책) + [본 repo ADR-0002 OKF v0.1 채택](../docs/adr/0002-okf-adoption.md)
- **본 repo 의 운영 위치**: [`docs/adr/0001-founding-charter.md`](../docs/adr/0001-founding-charter.md) + [`docs/adr/0002-okf-adoption.md`](../docs/adr/0002-okf-adoption.md) + [`docs/planning/v0.0.1-ai-library-roadmap.md`](../docs/planning/v0.0.1-ai-library-roadmap.md)

## 디렉터리 구조

```
backend/
├── README.md                  # 본 파일
├── pyproject.toml             # Python 3.13+ / FastAPI / Pi SDK
├── Dockerfile                 # M-v0.0.2+ (선택)
├── .env.example               # 환경 변수 예시 (시크릿 ❌)
├── okf/
│   └── SPEC.md                # OKF v0.1 spec in-repo 사본 (Apache 2.0)
├── src/
│   ├── main.py                # FastAPI app entry + typer CLI
│   ├── api/
│   │   └── v1/              # /api/v1/ endpoint (6 router, 17 endpoint placeholder)
│   │       ├── ingest.py      # POST /ingest/{source}/pull + GET /ingest/statuses
│   │       ├── bundles.py     # GET /bundles/{name} + GET /bundles + POST /bundles/{name}/rebuild
│   │       ├── concepts.py    # GET /concepts + GET /concepts/{type}/{name}
│   │       ├── raw.py         # GET /raw + DELETE /raw/{id}
│   │       ├── audit.py       # GET /audit
│   │       └── graph.py       # GET /graph + POST /graph/reindex
│   ├── sources/               # 5종 source plugin (mock + Gitea 4)
│   │   ├── base.py            # SourcePlugin abstract base
│   │   ├── mock.py
│   │   ├── gitea_repo_pull.py
│   │   ├── gitea_issue.py
│   │   ├── gitea_wiki.py
│   │   └── gitea_action.py
│   ├── okf/                   # OKF bundle engine
│   │   ├── envelope.py        # make_envelope() / parse_envelope() (placeholder)
│   │   ├── frontmatter.py     # YAML frontmatter parse/emit
│   │   ├── normalize.py       # data normalization pipeline
│   │   ├── link_graph.py      # cross-link reverse index
│   │   └── audit.py           # governance audit log
│   ├── llm/                   # Pi LLM enrich agent (M-v0.0.3+ 부터 활성화)
│   │   └── pi_enrich.py
│   └── config.py              # 4-priority REPO_ROOT auto-detect
├── scripts/
│   ├── dev.sh                 # uvicorn 로컬 dev
│   └── smoke.sh               # 8 smoke test
└── var/                       # runtime state (gitignored, except .gitkeep)
    ├── raw/                   # ingested raw data
    ├── concepts/              # OKF concept bundles
    ├── cross-link/            # cross-link reverse index
    └── audit/                 # governance audit log
```

## 로컬 실행 (M-v0.0.1-alpha)

```bash
# 1. 의존성 설치
cd backend/
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .

# 2. 환경 변수 (시크릿 ❌)
cp .env.example .env

# 3. dev server
bash scripts/dev.sh
# → http://localhost:8000 (FastAPI Swagger UI)

# 4. smoke test
bash scripts/smoke.sh
```

## standalone 운영 정책

본 backend 는 **완전 standalone** (ADR-0001 §2.3) — 다른 backend 연결 ❌, OIDC ❌, vendored re-introduce 가능.

- Network: 3 단계 (dev 사외 / staging 사내 / production 사내)
- Storage: file-based + DB-based 듀얼 모드 (M-v0.0.2+ default file-based, M-v0.0.4+ DB 옵션)
- Audit: governance audit log 정공법 정합
- API versioning: §16 정책 (M-v0.0.2+ `/api/v1/` prefix, M-v0.0.6+ `/api/v2/` dual endpoint, 12개월 deprecation policy)

## Tier

- **사외** (사내 한정 정보 0) — vendor-neutral + 독립 운영
- 사내 한정 패턴 (예: `DEVHUB_KEYCLOAK_*` / `kc.internal.example.com` / 사내 NAS hostname / `172.16.0.0/12`) 일절 없음