# OKF v0.1 — In-repo SPEC (Open Knowledge Format)

> **본 문서는 OKF v0.1 spec 의 ai_library 적용판**. 1차 출처 = Google Cloud `Open Knowledge Format v0.1` (2026-06-12 발표, Apache 2.0).
> DevHub 측 결정 = [ADR-0037 OKF v0.1 채택](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0037-okf-adoption.md) (1차 출처 + DevHub 적응). 본 repo 의 흡수 ADR = [`../../docs/adr/0002-okf-adoption.md`](../../docs/adr/0002-okf-adoption.md).

## 0. License + Provenance

- **License**: Apache 2.0 (1차 출처 = Google Cloud)
- **1차 출처 (Provenance)**:
  - [Google Cloud `Open Knowledge Format v0.1` SPEC.md](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md) (2026-06-12 발표)
  - [Google Cloud `Open Knowledge Format v0.1` README.md](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/README.md)
- **DevHub 적응**: `x_devhub_*` prefix 확장 (DevHub 의 5종 PII field / path Y / governance field 등) — 본 repo 에서는 `x_ai_library_*` prefix 로 적응
- **본 repo 적용판 작성자**: ykylee, 2026-06-23

## 1. OKF 정의

**OKF (Open Knowledge Format)** = vendor-neutral + git-friendly + agent-friendly 한 지식 표현 형식.

핵심 결정:
- **1 concept = 1 .md** (file-based, vendor-neutral)
- **frontmatter `type` 1개 필수** (8종 type enum)
- **cross-link** 자동 추출 (5 카테고리 매핑, `x_devhub_category` / `x_ai_library_category`)

## 2. 8종 type enum (OKF v0.1 spec §2)

| Type | 의미 | DevHub 적용 |
| --- | --- | --- |
| `concept` | 일반 concept 정의 (3종 = 5 category) | devhub/system / devhub/process / devhub/data / devhub/runbook / devhub/decisions |
| `runbook` | 운영 runbook (incident 대응 SOP) | §11.1 incident runbook |
| `decision` | ADR / 결정 record | §3.8 decision record |
| `reference` | 외부 시스템 reference (API spec, schema) | source plugin 7종 reference |
| `cross-link` | concept 간 cross-link 명시 | §3.5.6 reverse index |
| `tutorial` | onboarding tutorial | §2.4 standalone 검증 매트릭스 + Operator training |
| `release-notes` | release 기록 | §14 M-v0.2.0 release notes draft |
| `archive` | archived concept (deprecated) | §3.9.4 archive 거부 정책 |

## 3. frontmatter spec (OKF v0.1 spec §3)

### 3.1 필수 field

```yaml
---
type: concept           # 8종 enum 중 1
title: "Concept 제목"
id: "namespace/name"    # 1:1 매핑 (path Y 정합)
created: 2026-06-23
updated: 2026-06-23
---
```

### 3.2 권장 field (governance)

```yaml
owner: "team-name"      # curation 권한 추적 (§3.6.6.2)
status: "draft|active|deprecated"
category: "system|process|data|runbook|decisions"  # DevHub 5 category / 본 repo 동일
tags: ["tag1", "tag2"]
```

### 3.3 본 repo 확장 (x_ai_library_*) — M-v0.3.0+

```yaml
x_ai_library_source: "gitea_repo_pull"  # 어떤 source plugin 으로 ingest 됐는지
x_ai_library_bundle: "devhub-gitea"     # 어떤 bundle 에 속하는지
x_ai_library_license: "Apache-2.0|MIT|..."  # 라이선스 (OKF Apache 2.0 정합)
x_ai_library_pii: false                  # PII field 자동 detection (§3.6.6.5)
x_ai_library_audit_log: "var/audit/..."  # governance audit log 경로
```

## 4. cross-link spec (OKF v0.1 spec §4)

OKF v0.1 의 cross-link 는 5 category 매핑:

| Category | 의미 | Source plugin | bundle 예시 |
| --- | --- | --- | --- |
| `system` | 시스템 아키텍처, 인프라 | homelab / metrics | devhub-homelab, devhub-metrics |
| `process` | 운영 process / SOP | (manual) | (operator 작성) |
| `data` | 데이터 모델 / schema | hrdb | devhub-hrdb |
| `runbook` | incident 대응 runbook | (manual) | (operator 작성) |
| `decisions` | 결정 record (ADR) | (manual) | (operator 작성) |

본 repo 의 cross-link 추출 정공법 = DevHub umbrella §3.5.6 reverse index 정합. 자동 추출 (Pi LLM M-v0.3.1+) + operator confirm.

## 5. bundle 디렉터리 구조 (OKF v0.1 spec §5)

```
bundle/
├── index.md              # 자동 생성, bundle metadata + entry list
├── concepts/             # OKF concept file
│   ├── system/
│   │   └── devhub-overview.md
│   └── process/
│       └── ingest-pipeline.md
├── raw/                  # 1차 raw data (source plugin output)
│   └── 2026-06-23-gitea-repo-pull.jsonl
├── cross-link/           # cross-link reverse index (§3.5.6)
│   └── graph.json
└── audit/                # governance audit log (§3.6.6)
    └── 2026-06-23.jsonl
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

### 6.2 DevHub 의 `x_devhub_*` → 본 repo 의 `x_ai_library_*`

| DevHub prefix | 본 repo prefix | 의미 |
| --- | --- | --- |
| `x_devhub_source` | `x_ai_library_source` | source plugin 식별 |
| `x_devhub_bundle` | `x_ai_library_bundle` | bundle 식별 |
| `x_devhub_path_y` | `x_ai_library_path` | path Y user context (M-v0.3.0+ 동일) |
| `x_devhub_category` | `x_ai_library_category` | 5 category |
| `x_devhub_pii` | `x_ai_library_pii` | PII field detection |

### 6.3 본 repo 의 차이점 (DevHub 와)

- **DevHub = umbrella 의 child project**: DevHub 의 다른 backend (backend-core 등) 와 통합 가능 (단, §1.2 G7 standalone 정책 정합)
- **본 repo = standalone**: 다른 backend 연결 ❌, vendored re-introduce 가능
- **OIDC ❌**: 본 repo 는 인증/인가를 갖지 않음 (외부 vault 의 PAT/API key 만 사용)

## 7. References

- [Google Cloud OKF v0.1 SPEC.md (1차 출처)](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md) (Apache 2.0)
- [Google Cloud OKF v0.1 README.md (1차 출처)](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/README.md) (Apache 2.0)
- [DevHub ADR-0037 OKF v0.1 채택 (1차 출처의 DevHub 적응)](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0037-okf-adoption.md)
- [DevHub umbrella `release_v0-2_roadmap.md` §3 OKF 결정](https://github.com/ykylee/Devhub_example/blob/main/docs/planning/release_v0-2_roadmap.md)
- [본 repo ADR-0002 OKF v0.1 채택 (`../../docs/adr/0002-okf-adoption.md`)](../../docs/adr/0002-okf-adoption.md)
