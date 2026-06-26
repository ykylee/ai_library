# ADR-0001: ai_library founding charter

- **Status**: ✅ Accepted (2026-06-26)
- **Date**: 2026-06-26
- **Deciders**: yklee (owner, sole maintainer)
- **Tier**: 사외 (external-facing, public, MIT)

## 1. Context

`ai_library` 는 **vendor-neutral 한 knowledge bundle engine + LLM enrich agent** 의 standalone reference implementation 이다. 본 ADR 은 ai_library 의 founding charter 로서, 프로젝트의 존재 이유 / 운영 원칙 / 외부 경계를 선언한다.

본 repo 는 이전에 외부 umbrella 프로젝트의 child directory 였으나, 본 ADR 부터 **완전 독립** 으로 운영된다. 이전 lineage 는 historical supersession 으로 처리 (본 ADR §7) 되며, 더 이상 upstream / downstream 관계가 없다.

## 2. 결정

### 2.1 Scope

본 repo 가 제공하는 것:

| 영역 | 내용 |
| --- | --- |
| **Frontend** | SvelteKit 2 + Svelte 5 + TypeScript 5 standalone management UI (Path Y caller-provided user context, optional) |
| **Backend** | FastAPI + Pydantic v2 + OKF bundle engine + Source plugin ABC + LLM enrich placeholder |
| **OKF spec** | `backend/okf/SPEC.md` — Google Cloud Open Knowledge Format v0.1 의 본 repo 사본 (Apache 2.0, vendor-neutral) |
| **Source plugins** | 5종 = `mock` + `gitea_repo_pull` + `gitea_issue` + `gitea_wiki` + `gitea_action` (모두 SourcePlugin ABC 상속) |
| **LLM enrich** | Pi SDK 기반 placeholder (sdk / rpc / standalone mode), M-v0.0.3+ 부터 활성화 |

본 repo 가 **제공하지 않는** 것:

- 중앙 인증 (OIDC / SSO / Keycloak / LDAP ❌)
- 다른 backend / microservice / message queue 연결 ❌
- 사내 인프라 / private network / vault 자동 주입 ❌
- Source plugin 외의 외부 시스템 통합 (예: Prometheus / HRDB / 사내 metrics 는 옵션 env var 로만 정의, 실제 활성화 시 별도 결정)

### 2.2 Tier 정책 = **사외**

본 repo 는 **사외 tier** 다. 이는 다음을 의미한다:

- 외부 publish 가능 (GitHub public, MIT)
- vendor-neutral (특정 cloud / PaaS / 회사에 종속 ❌)
- 사내 한정 정보 단일 occurrence ❌ (예: `DEVHUB_*` / `kc.internal.example.com` / `devhub.example.com` / `172.16.0.0/12` / `internal-registry.example.com` / 특정 NAS hostname 등)
- 사내 한정 시크릿/호스트 도입 시 즉시 fail (PR 시 self-check 필수)

### 2.3 Standalone 정책

본 repo 는 **완전 standalone** 으로 운영된다:

- 다른 backend / microservice 연결 ❌
- OIDC / SSO / Keycloak 등 인증 게이트웨이 ❌
- 사내 인프라 / private network 직접 의존 ❌
- vendor lock-in (특정 cloud provider / paid service 종속) ❌

**Path Y caller-provided user context (optional)**: 인증 게이트웨이 대신, caller 가 직접 `X-AiLibrary-User-Context` HTTP header 로 user context 를 주입한다. backend 는 이 header 의 signature / payload 를 검증하지 **않는다** (trust the caller). 내부 운영 / trusted 환경 가정.

### 2.4 Version 정책

- 시작 버전 = **`0.0.1-alpha`** (founding commit 기준)
- SemVer 준수, 단 `0.x.y` 구간은 API / schema 변경 가능 (1.0.0 release 시 안정화)
- 마일스톤 표기 = `M-v<x>.<y>` (예: `M-v0.0.1-alpha`, `M-v0.0.2`, `M-v0.0.3`)
- release line = 독립 운영 (다른 umbrella 와 무관)

### 2.5 Storage 정책

- **file-based (default, M-v0.0.1-alpha+)**: `backend/var/raw/` + `backend/var/concepts/` + `backend/var/cross-link/` + `backend/var/audit/` 4-디렉터리 layout. 봉투 암호화 (M-v0.0.2+ 옵션).
- **DB-based (M-v0.0.4+ 옵션)**: SQLite / PostgreSQL 듀얼 모드. file-based default 유지하면서 read-side cache 로 활용.

### 2.6 API versioning 정책

- 시작 = `/api/v0-2/` prefix (FURL-stable path)
- dual endpoint 운영 = `/api/v0-2/` + `/api/v0-3/` 동시 운영 (M-v0.0.5+ 도입)
- 12개월 deprecation policy: 신규 endpoint 는 `v0-3/` 부터, `v0-2/` 는 12개월 후 제거

### 2.7 Source plugin 정책

- 5종 기본 = `mock` + Gitea 4
- 신규 source plugin 추가 시 `SourcePlugin` ABC 상속 + 4 method (meta / pull / normalize / health) 구현
- plugin 등록 = `backend/src/sources/<plugin>.py` + `SOURCES` enum (web) + env var (backend)
- plugin external 의존은 모두 옵션 (env var 비어 있으면 해당 plugin disable)

## 3. 결과

### 3.1 긍정적 결과

- **독립 release line**: 본 repo 의 결정이 외부 umbrella 와 drift 가능 → ADR supersession 정공법 (§7) 으로 해소
- **vendor-neutral**: 어떤 cloud / 회사에 deploy 해도 동일 동작
- **GitHub public 정합**: 사외 tier → MIT license + public repo 가 자연스러움
- **PoC / standalone 운영 적합**: 외부 의존 0 → researcher / 개인 contributor 도 즉시 clone 후 동작 가능

### 3.2 부정적 결과 / 트레이드오프

- **사내 시스템 통합 시 별도 결정 필요**: 특정 사내 vault / network / 인증 도입 시 §2.2 위반 → tier 정책 self-check + 별도 ADR 로 처리
- **OIDC 미지원**: enterprise SSO 연동 안 함 → caller-side 인증 필요
- **DB 듀얼 모드는 옵션**: file-based default 가 충분치 않을 수 있는 large-scale 운영 시 별도 평가

### 3.3 독립 release line

본 repo 는 umbrella 의 child project 가 **아니다**. umbrella / monorepo / vendor import pattern 의 vendored re-introduce 가능 (downstream consumer 가 결정), 단 본 repo 의 release cadence / scope 는 upstream 의 결정에 bound 되지 않는다.

## 4. 운영 spec

### 4.1 디렉터리 layout

```
ai_library/
├── README.md                          # 본 repo 의 1차 입구 (1-line description + quick start)
├── AGENTS.md                          # AI 워커 workflow 진입 규칙 (모든 agent 가 먼저 읽음)
├── LICENSE                            # MIT
├── .gitignore
├── web/                               # SvelteKit 2 frontend
│   ├── package.json
│   ├── svelte.config.js / vite.config.ts / vitest.config.ts / tsconfig.json
│   └── src/
│       ├── app.html / app.css / app.d.ts
│       ├── lib/                       # types / api / path-y / components
│       └── routes/                    # +layout / +page / audit / bundles / concepts / ingest / raw
├── backend/                           # FastAPI backend
│   ├── pyproject.toml                 # name = "ai-library-backend", version = "0.0.1"
│   ├── .env.example
│   ├── README.md
│   ├── src/
│   │   ├── main.py                    # FastAPI app factory + typer CLI
│   │   ├── config.py                  # 4-priority REPO_ROOT auto-detect
│   │   ├── api/v0_2/                  # /api/v0-2/ routers (ingest / bundles / concepts / raw / audit / graph)
│   │   ├── sources/                   # SourcePlugin ABC + 5종 plugin
│   │   ├── okf/                       # OKF bundle engine + envelope + frontmatter
│   │   └── llm/                       # Pi LLM enrich placeholder
│   ├── okf/SPEC.md                    # OKF v0.1 본 repo 사본
│   ├── var/                           # raw / concepts / cross-link / audit (gitignored)
│   └── scripts/                       # dev.sh / smoke.sh
└── docs/
    ├── adr/                           # ADR 0001 (founding) + 0002 (OKF 채택) + 후속 ADR
    └── planning/                      # umbrella roadmap (M-v0.0.x~v0.x.x milestone)
```

### 4.2 Quick start

```bash
# Frontend
cd web && npm ci && npm run dev            # http://localhost:5173

# Backend
cd backend && pip install -e . && ai-library serve    # http://localhost:8000
curl http://localhost:8000/api/v0-2/health

# Smoke test
cd backend && bash scripts/smoke.sh        # 8 smoke test (M-v0.0.1-alpha)
```

### 4.3 Tier self-check (PR 작성 시)

작성자가 다음을 self-verify 해야 한다:

- 신규 code 에 사내 한정 정보 (`DEVHUB_*` / 사내 hostname / private IP / 사내 SSO env) 등장 ❌
- 신규 `.env*` example 에 실제 사내 호스트 ❌ (placeholder 로만)
- 신규 source plugin 이 vendor lock-in 발생 ❌
- ADR / SPEC 변경 시 본 ADR §2 tier / §2.3 standalone 정책 정합

## 5. 대체 옵션 (고려했으나 채택 안 함)

| 옵션 | 이유 |
| --- | --- |
| 외부 umbrella 의 monorepo child 로 머무름 | 본 repo 의 release cadence 가 upstream bound 됨 + tier 정책 drift 위험 |
| Private GitHub repo + Gitea mirror 유지 | 사외 tier 정책상 public 정합, public 만으로 충분 |
| 1.0.0 부터 시작 | 사전 placeholder skeleton + frontend shell 운영 중, 0.0.1-alpha 가 정직한 시작점 |
| OKF 자체 spec 작성 (Google 형식 거부) | vendor-neutral 보존 + spec 작성 비용 절감 |

## 6. Cross-reference

- [`docs/adr/0002-okf-adoption.md`](0002-okf-adoption.md) — OKF v0.1 채택 결정 (본 ADR §2.1 scope 의 spec baseline)
- [`docs/planning/v0.0.1-ai-library-roadmap.md`](../planning/v0.0.1-ai-library-roadmap.md) — 본 ADR 의 마일스톤 전개 (M-v0.0.1-alpha~v0.x.x)
- [`backend/okf/SPEC.md`](../../backend/okf/SPEC.md) — OKF v0.1 본 repo 사본 (1차 출처)
- [`AGENTS.md`](../../AGENTS.md) — 본 repo 의 AI 워커 workflow 진입 규칙 (tier 정책 self-check 통합)

## 7. Supersession

본 ADR 은 **founding charter** 이므로 supersede-source 자체가 없다. 후속 ADR 이 본 ADR 의 §2 tier / §2.3 standalone 정책을 변경하려면:

1. 신규 ADR 작성 (`NNNN-<topic>.md`)
2. 본 ADR 의 §8 변경 이력에 row 추가 (supersede 정보)
3. 본 ADR §2.2 / §2.3 변경 시 **major version bump** 필요 (0.x.y → 0.x+1.0)

historical supersession (이전 lineage):
- 본 repo 가 이전에 외부 umbrella 프로젝트의 child 였던 시기의 결정은 **historical supersession** 으로 처리됨 (git history 보존, ADR 문서에서는 미언급).

## 8. 변경 이력

| 날짜 | 변경 | 결정 |
| --- | --- | --- |
| 2026-06-26 | 본 ADR-0001 작성 (founding charter) | 사용자 결정 "0.0.1로 하자 아직은 0.1.0으로 할 단계는 아니야" + "이전 프로젝트의 잔재는 완전히 없애줘" |

## 9. Related

- 본 ADR §2.4 version 정책 = `docs/planning/v0.0.1-ai-library-roadmap.md` 의 milestone table 과 1:1 정합
- 본 ADR §2.2 tier 정책 = `AGENTS.md` §3 작업 원칙의 "Tier 분리" 와 1:1 정합
- 본 ADR §2.3 standalone 정책 = `AGENTS.md` §6 운영 정책 + §2.6 network 정책 과 1:1 정합