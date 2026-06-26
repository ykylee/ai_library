# ai_library — AGENTS.md

- 문서 목적: 본 repo (`ykylee/ai_library`) 의 모든 AI 에이전트 (어떤 워커든) 가 먼저 읽어야 할 workflow 진입 규칙 + 작업 원칙.
- 범위: ai_library repo 자체 운영 + wiki mirror (`~/wiki/raw/projects/ai_library/`) 운영.
- 대상 독자: 모든 AI 워커 (Claude / Codex / Gemini / Reasonix / OpenCode / Sisyphus / Mavis / 기타), ai_library maintainer, contributor.
- 상태: active
- 최종 수정일: 2026-06-26 (founding)

## 1. Provenance (1차 출처)

본 repo 의 spec baseline:

1. [Google Cloud `Open Knowledge Format v0.1`](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md) (Apache 2.0) → [`backend/okf/SPEC.md`](backend/okf/SPEC.md) + [ADR-0002](docs/adr/0002-okf-adoption.md)
2. [본 repo ADR-0001 founding charter](docs/adr/0001-founding-charter.md) (2026-06-26, tier / standalone / version 정책)
3. [본 repo roadmap v0.0.1](docs/planning/v0.0.1-ai-library-roadmap.md) (7 마일스톤: M-v0.0.1-alpha~v0.1.0)

본 repo 는 **standalone** — upstream / downstream 관계 없음. vendor import 패턴으로 downstream consumer 가 vendored re-introduce 가능 (역방향 vendor import).

## 2. 항상 먼저 읽을 문서

1. 현재 git 브랜치 확인: `git branch --show-current`
2. 브랜치 prefix 별 memory 디렉터리 (`ai-workflow/memory/<agent>/<branch>/` 또는 `ai-workflow/memory/<role>/<branch>/`)
3. **본 AGENTS.md + [`docs/planning/v0.0.1-ai-library-roadmap.md`](docs/planning/v0.0.1-ai-library-roadmap.md) + [`docs/adr/0001-founding-charter.md`](docs/adr/0001-founding-charter.md)**

## 3. 작업 원칙

- 작업을 시작하기 전에 목적 / 범위 / 영향 doc 짧게 정리.
- 작업 상태: `planned` / `in_progress` / `blocked` / `done`.
- 검증하지 않은 결과는 완료로 확정 ❌. 모든 신규 기능은 unit test + e2e smoke 작성.
- 세션 종료 전: 본 AGENTS.md + roadmap §x.y + ADR-0001 §4.3 영향 section 갱신 + state.json (`ai-workflow/memory/<role>/<branch>/state.json`) 갱신.
- **추적성**: 모든 PR 은 umbrella doc + ADR 영향 section + `docs/traceability/report.md` 매트릭스 갱신 + PR body 의 "추적성 영향" 섹션.
- **Tier 분리**: 본 repo 는 **사외 tier**. 사내 한정 정보 (예: `DEVHUB_*` / `kc.internal.example.com` / `devhub.example.com` / `172.16.0.0/12` / `internal-registry.example.com` / 특정 NAS hostname) 의 단일 occurrence ❌. PR 작성 시 self-check 필수.
- **Standalone 정책 (ADR-0001 §2.3)**: 다른 backend 연결 ❌ + OIDC ❌ + 외부 시스템만 단방향 + caller-provided user context (Path Y, optional). §2.4 standalone 검증 매트릭스 (10 row) + §2.6 network 정책 (dev 사외 / staging 사내 / production 사내 3 단계) 준수.

## 4. 언어와 컨텍스트 원칙

- 사용자에게 직접 보이는 작업 보고 / handoff / backlog / 사용자 안내 문구 = 기본 **한국어**.
- 코드 / 명령어 / 파일 경로 / 외부 시스템 고유 명칭 = 필요할 때 원문 그대로 유지.
- commit message = 1-2 줄 + body 5-10 줄 bullet ("왜" + "검증 결과"). 한국어 prose + 영어 technical term.
- handoff / backlog = 다음 세션에 필요한 핵심 사실만.

## 5. 프로젝트 실행 기본값

- 설치: `cd web && npm ci` (frontend), `cd backend && pip install -e .` (backend, M-v0.0.2+)
- 로컬 실행 frontend: `cd web && npm run dev` (SvelteKit dev server)
- 로컬 실행 backend: `cd backend && bash scripts/dev.sh` (FastAPI, M-v0.0.2+, http://localhost:8000)
- 빠른 테스트 frontend: `cd web && npm run test:unit` (vitest)
- 격리 테스트 backend: `cd backend && python -m pytest` (M-v0.0.2+)
- 실행 확인 frontend: `curl http://localhost:5173/`
- 실행 확인 backend: `curl http://localhost:8000/api/v0-2/health` (M-v0.0.2+)

## 6. 문서 작업 기준

- 문서 위키 홈: `README.md`
- 운영 문서 위치: `docs/planning/` + `docs/adr/`
- backlog 위치: `ai-workflow/memory/<agent>/<branch>/backlog/`
- session handoff 위치: `ai-workflow/memory/<agent>/<branch>/session_handoff.md`
- state.json 위치: `ai-workflow/memory/<agent>/<branch>/state.json`
- 문서 포맷: Markdown(`.md`) 유지, HTML은 보고/취합용 파생 산출물로만.
- **문서 tier 라벨**: `docs/` 하위 신규/수정 문서는 `Tier: 사외` 명시 필수 (본 repo 는 모두 사외).

## 7. 워커 분업 (cross-project)

- 본 AGENTS.md 의 워커별 전용 메모는 historical 보존.
- 모든 신규 작업은 어느 에이전트로든 자유롭게 진행 가능.
- 단, 식별성을 위해 `<role>/work_<YYMMDD>-<sprint-seq>-<issue-num>-<short-key>` 패턴 권장.

## 8. Wiki mirror (1:1 byte-identical)

- `~/wiki/raw/projects/ai_library/` 의 mirror scope = 본 repo 의 source code + workflow + scripts + branch memory + traceability + domain/architecture/infrastructure/validation mass ingest.
- 모든 신규 PR은 mirror scope 갱신 요청 (mirror-list.md + lint-config.toml + scripts/wiki-sync-ai_library.sh 화이트리스트 정합) 필수.
- PR 머지 후 `bash scripts/wiki-sync-ai_library.sh` 1회 실행 (real mode) 으로 mirror 갱신.
- 상세 SOP: `docs/llm-wiki/operation-sop.md` (M-v0.0.2+ 작성).

## 9. 본 repo 내부 cross-reference

| # | 위치 | 설명 |
| --- | --- | --- |
| 1 | `README.md` | 1-line description + quick start + 디렉터리 구조 |
| 2 | `docs/adr/0001-founding-charter.md` | founding charter (tier / standalone / version 정책) |
| 3 | `docs/adr/0002-okf-adoption.md` | OKF v0.1 채택 결정 (Google Cloud 1차 출처) |
| 4 | `docs/planning/v0.0.1-ai-library-roadmap.md` | 7 마일스톤 roadmap |
| 5 | `backend/okf/SPEC.md` | OKF v0.1 in-repo 사본 (Apache 2.0) |
| 6 | `backend/README.md` | backend standalone 운영 |
| 7 | wiki mirror `~/wiki/raw/projects/ai_library/` | 본 repo 의 1:1 byte-identical mirror |