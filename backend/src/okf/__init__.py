"""OKF bundle engine (M-v0.3.0-alpha placeholder).

DevHub umbrella §3 (OKF 정의) + ADR-0037 (1차 출처: Google SPEC.md / README.md, Apache 2.0) 정합.

M-v0.3.0+ 부터 실제 구현:
- envelope.py: make_envelope() / parse_envelope() (bundle wrapping)
- frontmatter.py: YAML frontmatter parse/emit
- normalize.py: data normalization pipeline (§3.7)
- link_graph.py: cross-link reverse index (§3.5.6)
- audit.py: governance audit log (§3.6.6)
"""
from __future__ import annotations
