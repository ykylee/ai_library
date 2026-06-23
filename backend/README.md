# ai_library — backend

**AI Agent Library backend (FastAPI + OKF + Pi LLM enrich). 본 repo 의 standalone 운영 backend.**

- **Status**: M-v0.3.0-alpha (initial scaffold, 2026-06-23 extraction from DevHub v0.2.0 `backend-knowledge/`)
- **Source-of-truth**: 본 디렉터리. DevHub 측은 vendor import pattern 으로 vendored re-introduce 가능 (별도 결정)
- **1차 출처 결정**: [DevHub ADR-0037 OKF v0.1 채택](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0037-okf-adoption.md), [DevHub ADR-0038 backend-knowledge 신설](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0038-backend-knowledge-creation.md), [DevHub umbrella `release_v0-2_roadmap.md` §1.2 G1~G7 + §3 OKF 결정](https://github.com/ykylee/Devhub_example/blob/main/docs/planning/release_v0-2_roadmap.md)
- **본 repo 의 흡수 위치**: [`docs/adr/0001-ai-library-extraction.md`](../docs/adr/0001-ai-library-extraction.md) + [`docs/adr/0002-okf-adoption.md`](../docs/adr/0002-okf-adoption.md) + [`docs/planning/v0.3.0-ai-library-roadmap.md`](../docs/planning/v0.3.0-ai-library-roadmap.md)

## 디렉터리 구조

```
backend/
├── README.md                  # 본 파일
├── pyproject.toml             # Python 3.13+ / FastAPI / Pi SDK
├── Dockerfile                 # M-v0.3.0+ (선택)
├── .env.example               # 환경 변수 예시 (시크릿 ❌)
├── okf/
│   └── SPEC.md                # OKF v0.1 spec in-repo (Apache 2.0, Google SPEC.md 1차 출처)
├── src/
│   ├── main.py                # FastAPI app entry
│   ├── api/
│   │   └── v0_2/              # /api/v0-2/ endpoint (DevHub umbrella §3.1 API 매트릭스 정합)
│   │       ├── ingest.py      # POST /ingest/{source}/pull + GET /ingest/statuses
│   │       ├── bundles.py     # GET /bundles/{name} + GET /bundles + POST /bundles/{name}/rebuild
│   │       ├── concepts.py    # GET /concepts + GET /concepts/{type}/{name}
│   │       ├── raw.py         # GET /raw + DELETE /raw/{id}
│   │       ├── audit.py       # GET /audit
│   │       └── graph.py       # GET /graph + POST /graph/reindex
│   ├── sources/               # 7종 source plugin (Gitea 4 sub + homelab + metrics + hrdb)
│   │   ├── base.py            # SourcePlugin abstract base
│   │   ├── gitea_repo_pull.py
│   │   ├── gitea_issue.py
│   │   ├── gitea_wiki.py
│   │   ├── gitea_action.py
│   │   ├── homelab.py
│   │   ├── metrics.py
│   │   └── hrdb.py
│   ├── okf/                   # OKF bundle engine
│   │   ├── envelope.py        # make_envelope() / parse_envelope()
│   │   ├── frontmatter.py     # YAML frontmatter parse/emit
│   │   ├── normalize.py       # data normalization pipeline (§3.7)
│   │   ├── link_graph.py      # cross-link reverse index (§3.5.6)
│   │   └── audit.py           # governance audit log (§3.6.6)
│   ├── llm/                   # Pi LLM enrich agent (M-v0.3.1+ 부터 활성화)
│   │   └── pi_enrich.py
│   └── config.py              # 4-priority REPO_ROOT auto-detect (§2.4)
├── scripts/
│   ├── dev.sh                 # uvicorn 로컬 dev
│   └── smoke.sh               # 8 smoke test (DevHub §6.5.4 E2E 정합)
└── var/                       # runtime state (gitignored, except .gitkeep)
    ├── raw/                   # ingested raw data
    ├── concepts/              # OKF concept bundles
    ├── cross-link/            # cross-link reverse index
    └── audit/                 # governance audit log
```

## 로컬 실행 (M-v0.3.0-alpha)

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

본 backend 는 **완전 standalone** — 다른 backend (DevHub `backend-core` 등) 연결 ❌, OIDC ❌, vendored re-introduce 가능.

- Network: §2.6.1 3 단계 (dev 사외 / staging 사내 / production 사내)
- Storage: file-based + DB-based 듀얼 모드 (M-v0.3.0+ default file-based, M-v0.3.2+ DB 옵션)
- Audit: §3.6.6 governance audit log 정공법 정합
- API versioning: §16 정책 (M-v0.3.0+ `/api/v0-2/` prefix, 12개월 deprecation policy)

## Tier

- **사외** (사내 한정 정보 0) — DevHub 와 독립 운영, 외부 발매자 = 본 repo
- 사내 한정 패턴 (172.16.0.0/12, `DEVHUB_KEYCLOAK_*` 등) 일절 없음
