# Session Handoff — 2026-06-27 (M-v0.0.2-c 진행)

## Repo

- **위치**: `/Users/yklee/repos/ai_library`
- **Origin**: GitHub public (`https://github.com/ykylee/ai_library`)
- **Branch**: `main` (직접 운영, PR 없음)
- **Tier**: 사외 (vendor-neutral + OIDC ❌ + standalone)
- **Version**: `0.0.1-alpha` (founding commit 기준)

## 이전 세션 (2026-06-26) 완료

M-v0.0.1-alpha + 2 commit (founding + cleanup + retrofit) + M-v0.0.2-a/b (17 endpoint 중 9):
- 9 endpoint 등록 (1 root + 8 v1: health, ingest×3, bundles×4)
- 40 pytest pass, 8 smoke pass
- Commit c319992 까지

## 현재 세션 목표 (M-v0.0.2-c)

8 endpoint + 3 smoke 교체로 M-v0.0.2 마무리 (총 17 endpoint):

| Endpoint | Module | Notes |
| --- | --- | --- |
| `GET /api/v1/search` | concepts.py | inverted index, query-based |
| `GET /api/v1/concepts/{type}/{name}` | concepts.py | detail with bundle filter |
| `GET /api/v1/raw` | raw.py | source filter, pagination |
| `DELETE /api/v1/raw/{raw_id}` | raw.py | file remove + audit |
| `GET /api/v1/audit` | audit.py | in-memory + file persist |
| `GET /api/v1/graph` | graph.py | cross-link graph read |
| `POST /api/v1/graph/reindex` | graph.py | rebuild from bundles |
| `GET /api/v1/monitoring/alerts` | monitoring.py | 3-tier alert stub |

신규 module: `storage/raw.py` + `storage/audit.py`.

## 작업 원칙

- Commit message: 1-2 줄 subject + body 5-10 줄 bullet ("왜" + "검증 결과"). 한국어 prose + 영어 technical term.
- Test: `TestXxx` class + `test_xxx_yyy` method, pytest pattern 정합.
- Smoke: 8 test 고정, 3종 교체 (#4 search, #5 raw cycle, #6 audit+graph).
- CRITICAL: FastAPI 0.120+ pin 회피 (`fastapi>=0.115.0,<0.120.0`).

## Tier 정책

- 본 repo = **사외** (vendor-neutral + OIDC ❌ + standalone)
- 사내 한정 정보 (DEVHUB_*, internal-registry, NAS hostname) 일절 ❌