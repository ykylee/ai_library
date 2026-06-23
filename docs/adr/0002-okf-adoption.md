# ADR-0002: OKF v0.1 채택 (Open Knowledge Format)

- **Status**: accepted (2026-06-23)
- **Date**: 2026-06-23
- **Authors**: ykylee (사용자 결정 1차 출처)
- **Subsumes**: DevHub ADR-0037 OKF v0.1 채택 (OKF 결정 자체는 변경 ❌, *외부 repo 흡수 결정*)
- **Superseded-by**: (none)
- **본 repo 의 위치**: `docs/adr/0002-okf-adoption.md`
- **DevHub 측 cross-reference**: [DevHub ADR-0037 §6 Supersession 신규 row](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0037-okf-adoption.md) (본 ADR 의 subsume 가 아닌 외부 repo 흡수 결정)

## 0. Provenance (1차 출처)

본 ADR 의 결정 = **DevHub ADR-0037 의 OKF v0.1 채택 결정** 흡수 (1차 출처 동일).

1차 출처 (1차 검증, Apache 2.0):
- [Google Cloud `Open Knowledge Format v0.1` SPEC.md](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md) (2026-06-12 발표)
- [Google Cloud `Open Knowledge Format v0.1` README.md](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/README.md)

DevHub 적응:
- [DevHub ADR-0037 OKF v0.1 채택](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0037-okf-adoption.md) (`x_devhub_*` prefix 확장)

본 repo 적응:
- 본 ADR-0002 = DevHub ADR-0037 의 외부 repo 흡수 (vendor import pattern 역방향)
- prefix 적응: `x_devhub_*` → `x_ai_library_*` (5 field 매핑, [`backend/okf/SPEC.md` §6.2](../../backend/okf/SPEC.md))

## 1. Context

OKF (Open Knowledge Format) = vendor-neutral + git-friendly + agent-friendly 한 지식 표현 형식 (Google Cloud 발표, Apache 2.0). 본 repo 는 DevHub 의 OKF v0.1 채택 결정을 흡수하여 standalone 운영.

## 2. 결정

본 repo 의 모든 knowledge bundle 은 **OKF v0.1 형식** 으로 작성:

1. **1 concept = 1 .md** (file-based, vendor-neutral)
2. **frontmatter `type` 1개 필수** (8종 type enum)
3. **cross-link** 자동 추출 (5 category 매핑, `x_ai_library_category`)
4. **bundle 디렉터리 구조** (index.md + concepts/ + raw/ + cross-link/ + audit/)

OKF v0.1 spec 의 본 repo 적용판 = [`backend/okf/SPEC.md`](../../backend/okf/SPEC.md) (Apache 2.0 + 본 repo 적응).

## 3. 8종 type enum

| Type | 의미 | 본 repo 적용 |
| --- | --- | --- |
| `concept` | 일반 concept 정의 (5 category) | main content (system/process/data/runbook/decisions) |
| `runbook` | 운영 runbook (incident 대응 SOP) | §11.1 incident runbook |
| `decision` | ADR / 결정 record | 본 ADR / ADR-0001 |
| `reference` | 외부 시스템 reference (API spec, schema) | source plugin 7종 reference |
| `cross-link` | concept 간 cross-link 명시 | §3.5.6 reverse index |
| `tutorial` | onboarding tutorial | §2.4 standalone 검증 매트릭스 + Operator training |
| `release-notes` | release 기록 | M-v0.3.0+ release line |
| `archive` | archived concept (deprecated) | §3.9.4 archive 거부 정책 |

## 4. frontmatter spec

### 4.1 필수 field

```yaml
---
type: concept           # 8종 enum 중 1
title: "Concept 제목"
id: "namespace/name"    # 1:1 매핑 (path Y 정합)
created: 2026-06-23
updated: 2026-06-23
---
```

### 4.2 권장 field (governance)

```yaml
owner: "team-name"
status: "draft|active|deprecated"
category: "system|process|data|runbook|decisions"
tags: ["tag1", "tag2"]
```

### 4.3 본 repo 확장 (x_ai_library_*) — M-v0.3.0+

```yaml
x_ai_library_source: "gitea_repo_pull"
x_ai_library_bundle: "devhub-gitea"
x_ai_library_license: "Apache-2.0|MIT|..."
x_ai_library_pii: false
x_ai_library_audit_log: "var/audit/..."
```

상세: [`backend/okf/SPEC.md` §3](../../backend/okf/SPEC.md).

## 5. cross-link spec

OKF v0.1 의 cross-link = 5 category 매핑 (§3.5.6 reverse index 정합, DevHub umbrella §4.7 정합):

| Category | Source plugin | bundle 예시 |
| --- | --- | --- |
| `system` | homelab / metrics | devhub-homelab, devhub-metrics |
| `process` | (manual) | (operator 작성) |
| `data` | hrdb | devhub-hrdb |
| `runbook` | (manual) | (operator 작성) |
| `decisions` | (manual) | (operator 작성) |

## 6. Supersession History

| Date | Event | Reference |
| --- | --- | --- |
| 2026-06-23 | 본 ADR-0002 작성 (DevHub ADR-0037 의 subsume, *외부 repo 흡수 결정*) | DevHub ADR-0037 (subsumed) + 사용자 결정 |

## 7. References

- [Google Cloud OKF v0.1 SPEC.md (1차 출처, Apache 2.0)](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md)
- [Google Cloud OKF v0.1 README.md (1차 출처, Apache 2.0)](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/README.md)
- [DevHub ADR-0037 OKF v0.1 채택 (subsumed)](https://github.com/ykylee/Devhub_example/blob/main/docs/adr/0037-okf-adoption.md)
- [DevHub umbrella `release_v0-2_roadmap.md` §3 OKF 결정](https://github.com/ykylee/Devhub_example/blob/main/docs/planning/release_v0-2_roadmap.md)
- 본 repo [`backend/okf/SPEC.md`](../../backend/okf/SPEC.md) (in-repo 적응)
- 본 repo [ADR-0001 ai_library extraction](0001-ai-library-extraction.md) (sibling ADR)
- 본 repo [`docs/planning/v0.3.0-ai-library-roadmap.md`](../planning/v0.3.0-ai-library-roadmap.md) (umbrella 흡수)
