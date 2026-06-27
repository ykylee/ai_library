# M-v0.0.2-c Backlog (2026-06-27)

## Active (이번 세션)

- [ ] `storage/raw.py` — raw CRUD (list by source, read, delete)
- [ ] `storage/audit.py` — audit log (append, list, file persist)
- [ ] `api/v1/concepts.py` — search + detail
- [ ] `api/v1/raw.py` — list + delete
- [ ] `api/v1/audit.py` — GET /audit
- [ ] `api/v1/graph.py` — GET + POST /reindex
- [ ] `api/v1/monitoring.py` — GET /alerts
- [ ] `api/v1/__init__.py` — 5 router 등록
- [ ] 신규 test 5 file (~20 test)
- [ ] smoke 3종 교체 (#4 search, #5 raw cycle, #6 audit+graph)
- [ ] commit + push

## Open follow-up (별도 backlog, M-v0.0.3+)

1. **pi-coding-agent drift** — `backend/pyproject.toml` 에 `pi-coding-agent>=0.79.6` 박혀있는데 pip 에 존재하지 않는 버전. M-v0.0.3+ 에서 `optional-dependencies` 로 이동.
2. **Vitest env drift** — `web/node_modules` 에 jsdom 없음 + `btoa()` Unicode 핸들링 버그 + `@ts-expect-error` unused 3건. frontend test 회귀 fix.
3. **`envelope.py` 의 `data: Any`** — Pydantic v2 + Generic typing 으로 generic Envelope[T] 가능하면 강타입 wrap helper 추가.
4. **web frontend ↔ backend integration test** — vitest mock 만 검증, 실제 backend 호출 e2e 없음.
5. **graph reindex 구현** — 현재 stub (concept_count * 2). M-v0.0.5+ 부터 real cross-link index.