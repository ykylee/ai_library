"""Source plugin package (M-v0.3.0-alpha placeholder).

7종 source plugin (DevHub ADR-0038 + umbrella §1.2 G3 정합):
- gitea_repo_pull : Gitea repo 메타 + README + 파일 tree
- gitea_issue     : Gitea issue tracker (5 카테고리 중 이슈)
- gitea_wiki      : Gitea wiki page
- gitea_action    : Gitea Actions workflow run
- homelab         : HomeLab 통합 시점 (homelab_dashboard 메트릭)
- metrics         : Prometheus / VictoriaMetrics 시계열
- hrdb            : 사내 HR DB (M-v0.3.2+)

M-v0.3.0+ 부터 base.SourcePlugin 상속 + src.sources.<plugin>.py 작성.
"""
from __future__ import annotations
