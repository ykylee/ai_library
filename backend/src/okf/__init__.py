"""OKF bundle engine (M-v0.3.0-alpha placeholder).

1차 출처: Google Cloud Open Knowledge Format v0.1 (Apache 2.0, `okf/SPEC.md` 본 repo 사본).

M-v0.3.0+ 부터 실제 구현:
- envelope.py: make_envelope() / parse_envelope() (bundle wrapping)
- frontmatter.py: YAML frontmatter parse/emit
- normalize.py: data normalization pipeline
- link_graph.py: cross-link reverse index
- audit.py: governance audit log
"""
from __future__ import annotations
