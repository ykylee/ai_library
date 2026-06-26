# ADR-0002: OKF v0.1 채택 (Open Knowledge Format)

- **Status**: ✅ Accepted (2026-06-26, founding)
- **Date**: 2026-06-26
- **Authors**: ykylee (founding decision)
- **본 repo 의 위치**: `docs/adr/0002-okf-adoption.md`
- **Tier**: 사외 (vendor-neutral, Apache 2.0 spec)

## 0. Provenance (1차 출처)

본 ADR 의 결정 = **Google Cloud `Open Knowledge Format v0.1` 채택** (vendor-neutral, Apache 2.0).

1차 출처 (Google Cloud):
- [Google Cloud `Open Knowledge Format v0.1` SPEC.md](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md) (2026-06-12 발표)
- [Google Cloud `Open Knowledge Format v0.1` README.md](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/README.md)

본 repo 적응:
- 본 ADR-0002 = OKF v0.1 의 founding 채택 (vendor-neutral + standalone 운영)
- prefix 적응: `x_ai_library_*` (OKF v0.1 의 `x_<publisher>_*` extension namespace 표준 패턴)

## 1. Context

OKF (Open Knowledge Format) = vendor-neutral + git-friendly + agent-friendly 한 지식 표현 형식 (Google Cloud 발표, Apache 2.0). 본 repo 는 OKF v0.1 을 founding spec 으로 채택하여 standalone 운영한다.

## 2. 결정

본 repo 의 모든 knowledge bundle 은 **OKF v0.1 형식** 으로 작성:

1. **1 concept = 1 .md** (file-based, vendor-neutral, git 가능)
2. **frontmatter `type` 1개 필수** (8종 type enum)
3. **cross-link** 자동 추출 (5 category 매핑, `x_ai_library_category`)
4. **bundle 디렉터리 구조** (index.md + concepts/ + raw/ + cross-link/ + audit/)

OKF v0.1 spec 의 본 repo 적용판 = [`backend/okf/SPEC.md`](../../backend/okf/SPEC.md) (Apache 2.0 + 본 repo 적응).

## 3. 8종 type enum

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

## 4. frontmatter spec

### 4.1 필수 field

```yaml
---
type: concept           # 8종 enum 중 1
title: "Concept 제목"
id: "namespace/name"    # 1:1 매핑 (path Y 정합)
created: 2026-06-26
updated: 2026-06-26
---
```

### 4.2 권장 field (governance)

```yaml
owner: "team-name"
status: "draft|active|deprecated"
category: "system|process|data|runbook|decisions"
tags: ["tag1", "tag2"]
```

### 4.3 본 repo 확장 (x_ai_library_*) — M-v0.0.2+

```yaml
x_ai_library_source: "gitea_repo_pull"
x_ai_library_bundle: "gitea-bundle"
x_ai_library_license: "Apache-2.0|MIT|..."
x_ai_library_pii: false
x_ai_library_audit_log: "var/audit/..."
```

상세: [`backend/okf/SPEC.md` §3](../../backend/okf/SPEC.md).

## 5. cross-link spec

OKF v0.1 의 cross-link = 5 category 매핑:

| Category | Source plugin | bundle 예시 |
| --- | --- | --- |
| `system` | mock / metrics (옵션) | mock-bundle, metrics-bundle |
| `process` | (manual) | (operator 작성) |
| `data` | hrdb (옵션, M-v0.0.4+) | hrdb-bundle |
| `runbook` | (manual) | (operator 작성) |
| `decisions` | (manual) | (operator 작성) |

## 6. Supersession History

| Date | Event | Reference |
| --- | --- | --- |
| 2026-06-26 | 본 ADR-0002 작성 (founding: OKF v0.1 채택) | 사용자 결정 + Google Cloud OKF v0.1 spec (1차 출처) |

## 7. References

- [Google Cloud OKF v0.1 SPEC.md (1차 출처, Apache 2.0)](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/SPEC.md)
- [Google Cloud OKF v0.1 README.md (1차 출처, Apache 2.0)](https://github.com/GoogleCloudPlatform/opennative-formats/blob/main/README.md)
- 본 repo [`backend/okf/SPEC.md`](../../backend/okf/SPEC.md) (in-repo 적응)
- 본 repo [ADR-0001 founding charter](0001-founding-charter.md) (sibling ADR)
- 본 repo [`docs/planning/v0.0.1-ai-library-roadmap.md`](../planning/v0.0.1-ai-library-roadmap.md) (umbrella roadmap)