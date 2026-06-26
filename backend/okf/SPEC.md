# OKF v0.1 — In-repo SPEC (Open Knowledge Format)

> **본 문서는 OKF v0.1 spec 의 ai_library 적용판**. 1차 출처 = Google Cloud `Open Knowledge Format v0.1` (2026-06-12 발표, Apache 2.0). 본 repo 의 채택 ADR = [`../../docs/adr/0002-okf-adoption.md`](../../docs/adr/0002-okf-adoption.md).

## 0. License + Provenance

- **License**: Apache 2.0 (1차 출처 = Google Cloud)
- **1차 출처 (Provenance)**:
  - [Google Cloud `Open Knowledge Format v0.1` SPEC.md](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md) (2026-06-12 발표)
  - [Google Cloud `Open Knowledge Format v0.1` README.md](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/README.md)
- **본 repo 적용판 작성자**: ykylee, 2026-06-26
- **본 repo prefix**: `x_ai_library_*` (OKF v0.1 의 `x_<publisher>_*` extension namespace 표준 패턴 따름)

## 1. OKF 정의

**OKF (Open Knowledge Format)** = vendor-neutral + git-friendly + agent-friendly 한 지식 표현 형식.

핵심 결정:
- **1 concept = 1 .md** (file-based, vendor-neutral)
- **frontmatter `type` 1개 필수** (8종 type enum)
- **cross-link** 자동 추출 (5 카테고리 매핑, `x_ai_library_category`)

## 2. 8종 type enum (OKF v0.1 spec §2)

| Type | 의미 | 본 repo 적용 |
| --- | --- | --- |
| `concept` | 일반 concept 정의 (5 category) | main content (system/process/data/runbook/decisions) |
| `runbook` | 운영 runbook (incident 대응 SOP) | incident 대응 SOP |
| `decision` | ADR / 결정 record | 본 ADR / ADR-0001 |
| `reference` | 외부 시스템 reference (API spec, schema) | source plugin reference |
| `cross-link` | concept 간 cross-link 명시 | reverse index |
| `tutorial` | onboarding tutorial | standalone 검증 매트릭스 + Operator training |
| `release-notes` | release 기록 | M-v0.0.x release line |
| `archive` | archived concept (deprecated) | archive 거부 정책 |

## 3. frontmatter spec (OKF v0.1 spec §3)

### 3.1 필수 field

```yaml
---
type: concept           # 8종 enum 중 1
title: "Concept 제목"
id: "namespace/name"    # 1:1 매핑 (path Y 정합)
created: 2026-06-26
updated: 2026-06-26
---
```

### 3.2 권장 field (governance)

```yaml
owner: "team-name"      # curation 권한 추적
status: "draft|active|deprecated"
category: "system|process|data|runbook|decisions"  # 5 category (concept type sub-classification)
tags: ["tag1", "tag2"]
```

### 3.3 본 repo 확장 (x_ai_library_*) — M-v0.0.2+

```yaml
x_ai_library_source: "gitea_repo_pull"  # 어떤 source plugin 으로 ingest 됐는지
x_ai_library_bundle: "gitea-bundle"     # 어떤 bundle 에 속하는지
x_ai_library_license: "Apache-2.0|MIT|..."  # 라이선스 (OKF Apache 2.0 정합)
x_ai_library_pii: false                  # PII field 자동 detection
x_ai_library_audit_log: "var/audit/..."  # governance audit log 경로
```

## 4. cross-link spec (OKF v0.1 spec §4)

OKF v0.1 의 cross-link 는 5 category 매핑:

| Category | 의미 | Source plugin | bundle 예시 |
| --- | --- | --- | --- |
| `system` | 시스템 아키텍처, 인프라 | mock / metrics (옵션) | mock-bundle, metrics-bundle |
| `process` | 운영 process / SOP | (manual) | (operator 작성) |
| `data` | 데이터 모델 / schema | hrdb (옵션, M-v0.0.4+) | hrdb-bundle |
| `runbook` | incident 대응 runbook | (manual) | (operator 작성) |
| `decisions` | 결정 record (ADR) | (manual) | (operator 작성) |

본 repo 의 cross-link 추출 정공법 = reverse index 기반. 자동 추출 (Pi LLM M-v0.0.3+) + operator confirm.

## 5. bundle 디렉터리 구조 (OKF v0.1 spec §5)

```
bundle/
├── index.md              # 자동 생성, bundle metadata + entry list
├── concepts/             # OKF concept file
│   ├── system/
│   │   └── overview.md
│   └── process/
│       └── ingest-pipeline.md
├── raw/                  # 1차 raw data (source plugin output)
│   └── 2026-06-26-gitea-repo-pull.jsonl
├── cross-link/           # cross-link reverse index
│   └── graph.json
└── audit/                # governance audit log
    └── 2026-06-26.jsonl
```

## 6. 본 repo 적용 정공법

### 6.1 8종 type enum 의 본 repo 적응

본 repo 는 8종 type 모두 사용 가능 (vendor-neutral). 단, 다음 우선순위로 운영:

1. `concept` (5 category) = main content
2. `runbook` = incident 대응
3. `decision` = ADR
4. `reference` = source plugin reference (외부 API spec)
5. `cross-link` = graph 정합
6. `tutorial` = onboarding
7. `release-notes` = release 기록
8. `archive` = deprecated

### 6.2 본 repo 의 prefix (`x_ai_library_*`)

| 본 repo prefix | 의미 |
| --- | --- |
| `x_ai_library_source` | source plugin 식별 (mock / gitea_repo_pull / gitea_issue / gitea_wiki / gitea_action) |
| `x_ai_library_bundle` | bundle 식별 |
| `x_ai_library_path` | path Y user context (M-v0.0.2+ 동일) |
| `x_ai_library_category` | 5 category (system/process/data/runbook/decisions) |
| `x_ai_library_pii` | PII field detection |
| `x_ai_library_license` | license (Apache 2.0 / MIT / etc) |
| `x_ai_library_audit_log` | governance audit log 경로 |

### 6.3 standalone 운영 특성

- **standalone**: 다른 backend 연결 ❌, vendored re-introduce 가능 (downstream consumer 결정)
- **OIDC ❌**: 본 repo 는 인증/인가를 갖지 않음 (외부 vault 의 PAT/API key 만 사용)
- **Path Y caller-provided user context (optional)**: 인증 게이트웨이 대신 caller 가 직접 주입

## 7. References

- [Google Cloud OKF v0.1 SPEC.md (1차 출처)](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md) (Apache 2.0)
- [Google Cloud OKF v0.1 README.md (1차 출처)](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/README.md) (Apache 2.0)
- 본 repo ADR-0002 OKF v0.1 채택 ([`../../docs/adr/0002-okf-adoption.md`](../../docs/adr/0002-okf-adoption.md))
- 본 repo ADR-0001 founding charter ([`../../docs/adr/0001-founding-charter.md`](../../docs/adr/0001-founding-charter.md))