"""Source plugin package (M-v0.0.1-alpha placeholder).

5종 source plugin:
- mock           : 외부 의존 0 mock source (PoC / 테스트 / standalone 운영 기본)
- gitea_repo_pull: Gitea repo 메타 + README + 파일 tree
- gitea_issue    : Gitea issue tracker
- gitea_wiki     : Gitea wiki page
- gitea_action   : Gitea Actions workflow run

M-v0.0.2+ 부터 base.SourcePlugin 상속 + src.sources.<plugin>.py 작성.
"""
from __future__ import annotations
