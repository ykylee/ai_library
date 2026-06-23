# ADR-0001: ai_library extraction (vendor import pattern 역방향)

- **Status**: accepted (2026-06-23)
- **Date**: 2026-06-23
- **Authors**: ykylee (사용자 결정 1차 출처)
- **Supersedes**: DevHub ADR-0038 (`backend-knowledge` 신설) 의 결정 자체는 변경 ❌. 본 ADR 은 *외부 repo 흡수 결정* (DevHub §15 ADR supersession 정공법 정합, historical supersession, extraction).
- **Superseded-by**: (none)
- **본 repo 의 위치**: `docs/adr/0001-ai-library-extraction.md`
- **DevHub 측 cross-reference**: [DevHub ADR-0038 §6 Supersession 신규 row](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0038-backend-knowledge-creation.md) (본 ADR 의 supersede 가 아닌 외부 repo 흡수 결정)

## 0. Provenance (1차 출처)

본 ADR 의 결정 (1. d가 맞아. 2. ~/repos/ai_library. 3. 완전 독립. 4. cross-ref 정합. 5. 1 참고 정리) 은 **사용자 2026-06-23 결정** (verbatim).

관련 1차 출처:
1. [DevHub ADR-0037 OKF v0.1 채택](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0037-okf-adoption.md) (subsumed by 본 repo ADR-0002)
2. [DevHub ADR-0038 backend-knowledge 신설](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0038-backend-knowledge-creation.md) (본 ADR 의 supersede source)
3. [DevHub umbrella `release_v0-2_roadmap.md` §1.2 G1~G7 + §3 OKF 결정](https://github.com/ykylee/Devhub_example/blob/main/docs/planning/release_v0-2_roadmap.md)
4. [DevHub child doc `external-integrations-agentic-rag-roadmap.md` §3 (Phase 1 adapter pattern) + §4 (Phase 2 agentic RAG)](https://github.com/ykylee/Devhub_example/blob/main/docs/planning/external-integrations-agentic-rag-roadmap.md)
5. DevHub `AGENTS.md` line 29 redirect

## 1. Context

DevHub 의 v0.2.0 umbrella doc (2026-06-17 accepted) 는 `backend-knowledge/` 디렉터리 신설 결정. 2026-06-17~2026-06-22 in-repo 운영 (M-v0.2.0~v0.2.3 PoC + frontend shell + 영향 doc 4종 + ADR-0037/0038).

2026-06-23 사용자 결정: `backend-knowledge/` 를 **외부 repo 로 extraction** — 본 repo (`ykylee/ai_library`, Gitea private, https://homelab.ddn777.synology.me/gitea/yklee/ai_library) 신설. vendor import pattern 의 **역방향 정공법** — 외부 발매자 (= 본 repo) 가 DevHub 의 결정을 흡수.

## 2. 결정

### 2.1 boundary = **d-1 정공법**

본 repo 의 흡수 범위 = **frontend web/ (SvelteKit 2 + Svelte 5 + vitest 21 src file, 27 file) + 영향 doc 4종 통째 이식**.

- frontend shell 통째 이식 (DevHub `backend-knowledge/web/` 의 27 source file + node_modules 제외)
- backend code 자체는 **이식 ❌** (DevHub 의 `backend-knowledge/` 가 spec 단계였고, 실제 Python code 0 file) — 본 repo 의 `backend/` 는 **placeholder skeleton** (FastAPI app + OKF envelope + source plugin abstract base)
- 영향 doc 4종 redirect 1:1:
  1. umbrella doc `release_v0-2_roadmap.md` §1.2 G1 cell + §9 2026-06-23 row
  2. ADR-0037 §6 supersession row
  3. ADR-0038 §6 supersession row
  4. child doc `external-integrations-agentic-rag-roadmap.md` §8 변경 이력 row
  5. DevHub `AGENTS.md` line 29 redirect

### 2.2 standalone 정책

본 repo (`ai_library`) 는 **완전 standalone** 운영:

- 다른 backend (DevHub `backend-core` 등) 연결 ❌
- OIDC ❌ (외부 vault 의 PAT/API key 만 사용)
- Network: §2.6.1 3 단계 (dev 사외 / staging 사내 / production 사내)
- Storage: file-based (M-v0.3.0+ default) + DB-based 듀얼 모드 (M-v0.3.2+ 옵션)
- Tier: 사외 (사내 한정 정보 0)
- API versioning: §16 정책 (M-v0.3.0+ `/api/v0-2/` prefix, 12개월 deprecation policy)

### 2.3 vendor import pattern 역방향

본 repo = 외부 발매자. DevHub 측은 본 repo 를 **vendored re-introduce** 가능 (vendor import pattern). 본 repo 의 결정 (OKF v0.1 채택 + 7종 source plugin + standalone 운영) 은 DevHub 의 umbrella doc §1.2 G1~G7 standalone 정책과 **1:1 정합**.

## 3. M-v0.3.0 마일스톤

| M | 상태 | scope |
| --- | --- | --- |
| M-v0.3.0-alpha | ✅ done (2026-06-23) | 본 ADR + ADR-0002 + roadmap + frontend shell 이식 + backend skeleton + standalone 운영 |
| M-v0.3.0 | ⏳ planned (2026-Q3) | FastAPI app + 6 router 등록 (17 endpoint) + 8 smoke test + pyproject.toml editable install |
| M-v0.3.1 | ⏳ planned (2026-Q3) | Pi LLM enrich agent 활성화 (sdk mode default, 3 mode confirm workflow) |
| M-v0.3.2 | ⏳ planned (2026-Q4) | DB-based raw + Pi periodic ingest pipeline (DevHub umbrella §10 + §11 정합) |
| M-v0.3.3 | ⏳ planned (2026-Q4) | cross-link reverse index + governance audit log dashboard |
| M-v0.3.4 | ⏳ planned (2027-Q1) | API versioning v0-3 도입 (§16.2 dual endpoint support) |

## 4. Cross-reference (4-way)

| 위치 | 변경 |
| --- | --- |
| [DevHub umbrella `release_v0-2_roadmap.md` §1.2 G1 cell](https://github.com/ykylee/Devhub_example/blob/main/docs/planning/release_v0-2_roadmap.md) | redirect 1줄 |
| [DevHub umbrella `release_v0-2_roadmap.md` §9 변경 이력 2026-06-23 row](https://github.com/ykylee/Devhub_example/blob/main/docs/planning/release_v0-2_roadmap.md) | 신규 row |
| [DevHub ADR-0037 §6 Supersession section 신규 row](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0037-okf-adoption.md) | subsumed by 본 repo ADR-0002 |
| [DevHub ADR-0038 §6 Supersession section 신규 row](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0038-backend-knowledge-creation.md) | superseded by 본 ADR-0001 |
| [DevHub child doc `external-integrations-agentic-rag-roadmap.md` §8 변경 이력 row](https://github.com/ykylee/Devhub_example/blob/main/docs/planning/external-integrations-agentic-rag-roadmap.md) | 2026-06-23 row 신규 |
| [DevHub `AGENTS.md` line 29](https://github.com/ykylee/Devhub_example/blob/main/AGENTS.md) | redirect 1줄 |
| 본 repo `AGENTS.md` line 7 + 23 | provenance + scope redirect |
| 본 repo `README.md` provenance table | 흡수 source 4 row |

## 5. Consequences

### 5.1 Positive

- 본 repo = 외부 발매자 — DevHub 의 umbrella 가 본 repo 의 결정 흡수 가능 (vendor import pattern)
- standalone 운영으로 DevHub 의 다른 backend 와 decoupled
- frontend shell + backend spec + 영향 doc 4종이 한 repo 에서 1:1 byte-identical 운영
- M-v0.3.0+ 부터 독립 release line 가능 (DevHub umbrella 와 무관)

### 5.2 Negative (trade-off)

- DevHub 측에서 본 repo 의 변경을 자동 반영 ❌ (vendor import 패턴이 vendored re-introduce 필요)
- cross-reference 4-way 동시 갱신 부담 (umbrella + ADR-0037 + ADR-0038 + child + AGENTS 5 file)
- 본 repo 의 결정이 DevHub 의 결정과 drift 가능 → ADR supersession 정공법 (§6) 으로 해소

### 5.3 Risks

- 본 repo 의 standalone 운영이 DevHub 의 standalone 정책과 drift 가능 → M-v0.3.0+ 부터 weekly cross-reference 검증
- 본 repo 의 standalone 운영이 DevHub 의 운영 (OIDC, 사내 network) 과 무관 → Tier 분리 정책 (사외/사내/공용) 정합

## 6. Supersession History

| Date | Event | Reference |
| --- | --- | --- |
| 2026-06-23 | 본 ADR-0001 작성 (외부 repo 흡수 결정, DevHub ADR-0038 의 supersede 가 아닌 *외부 repo 흡수 결정*) | 사용자 결정 "1. d가 맞아. 2. ~/repos/ai_library. 3. 완전 독립. 4. cross-ref 정합. 5. 1 참고 정리" |

## 7. References

- [DevHub ADR-0038 `backend-knowledge` 신설](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0038-backend-knowledge-creation.md) (본 ADR 의 supersede source)
- [DevHub umbrella `release_v0-2_roadmap.md`](https://github.com/ykylee/Devhub_example/blob/main/docs/planning/release_v0-2_roadmap.md) (§1.2 G1~G7 + §3 OKF + §15 ADR supersession 정공법)
- [DevHub `AGENTS.md`](https://github.com/ykylee/Devhub_example/blob/main/AGENTS.md) (line 29 redirect)
- [DevHub child doc `external-integrations-agentic-rag-roadmap.md`](https://github.com/ykylee/Devhub_example/blob/main/docs/planning/external-integrations-agentic-rag-roadmap.md)
- [DevHub `docs/governance/worker_division.md` §4.2 ADR supersession 정공법](https://github.com/ykylee/Devhub_example/blob/main/docs/governance/worker_division.md) (12개월 deprecation policy + 5 step 정공법)
- 본 repo `AGENTS.md` (workflow 진입 규칙)
- 본 repo [`docs/adr/0002-okf-adoption.md`](0002-okf-adoption.md) (sibling ADR, OKF v0.1 채택)
- 본 repo [`docs/planning/v0.3.0-ai-library-roadmap.md`](../planning/v0.3.0-ai-library-roadmap.md) (umbrella 흡수)
- 본 repo [`backend/okf/SPEC.md`](../../backend/okf/SPEC.md) (OKF v0.1 in-repo 적응)
