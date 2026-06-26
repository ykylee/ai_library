"""Envelope + Path Y parser unit tests (M-v0.0.2-a)."""
from __future__ import annotations

import base64
import json

import pytest

from src.api.envelope import Envelope, EnvelopeContext, EnvelopeMeta
from src.api.path_y import PathYUserContext, parse_path_y


class TestPathYParser:
    """parse_path_y : X-AiLibrary-User-Context decode."""

    def test_none_input_returns_none(self) -> None:
        assert parse_path_y(None) is None

    def test_empty_string_returns_none(self) -> None:
        assert parse_path_y("") is None

    def test_valid_base64url_decodes(self) -> None:
        ctx = {
            "version": "v0",
            "user_id": "u_001",
            "org_id": "ou_root",
            "org_unit_ids": ["ou_root"],
            "project_ids": [],
            "roles": ["developer"],
            "request_id": "req_001",
            "issued_at": "2026-06-26T00:00:00Z",
        }
        raw = json.dumps(ctx).encode("utf-8")
        encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
        result = parse_path_y(encoded)
        assert result is not None
        assert result.user_id == "u_001"
        assert result.org_id == "ou_root"
        assert result.roles == ["developer"]

    def test_korean_user_id(self) -> None:
        ctx = {
            "version": "v0",
            "user_id": "u_한국",
            "org_id": "ou_root",
            "org_unit_ids": [],
            "project_ids": [],
            "roles": [],
            "request_id": "req_001",
            "issued_at": "2026-06-26T00:00:00Z",
        }
        raw = json.dumps(ctx, ensure_ascii=False).encode("utf-8")
        encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
        result = parse_path_y(encoded)
        assert result is not None
        assert result.user_id == "u_한국"

    def test_invalid_base64_returns_none(self) -> None:
        assert parse_path_y("!!!not-valid-base64!!!") is None

    def test_invalid_json_returns_none(self) -> None:
        raw = b"not-json{"
        encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
        assert parse_path_y(encoded) is None

    def test_missing_required_field_returns_none(self) -> None:
        # 'user_id' missing
        ctx = {
            "version": "v0",
            "org_id": "ou_root",
            "org_unit_ids": [],
            "project_ids": [],
            "roles": [],
            "request_id": "req_001",
            "issued_at": "2026-06-26T00:00:00Z",
        }
        raw = json.dumps(ctx).encode("utf-8")
        encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
        assert parse_path_y(encoded) is None


class TestEnvelopeContext:
    """EnvelopeContext : per-request envelope metadata."""

    def test_new_request_id_is_uuid4(self) -> None:
        ctx = EnvelopeContext.new()
        assert isinstance(ctx.request_id, str)
        assert len(ctx.request_id) == 36  # UUID4 format
        assert ctx.request_id.count("-") == 4

    def test_new_without_path_y(self) -> None:
        ctx = EnvelopeContext.new(path_y=None)
        assert ctx.path_y is None

    def test_meta_with_path_y(self) -> None:
        py = PathYUserContext(
            version="v0",
            user_id="u_001",
            org_id="ou_root",
            org_unit_ids=["ou_root"],
            project_ids=[],
            roles=["developer"],
            request_id="req_001",
            issued_at="2026-06-26T00:00:00Z",
        )
        ctx = EnvelopeContext.new(path_y=py)
        meta = ctx.meta()
        assert isinstance(meta, EnvelopeMeta)
        assert meta.caller_user_id == "u_001"
        assert meta.path_y_validated is True
        assert meta.api_version == "v0-2"

    def test_meta_without_path_y(self) -> None:
        ctx = EnvelopeContext.new(path_y=None)
        meta = ctx.meta()
        assert meta.caller_user_id is None
        assert meta.path_y_validated is False

    def test_wrap_returns_envelope_dict(self) -> None:
        ctx = EnvelopeContext.new(path_y=None)
        wrapped = ctx.wrap({"foo": "bar"})
        assert "envelope" in wrapped
        assert wrapped["data"] == {"foo": "bar"}
        assert wrapped["envelope"]["api_version"] == "v0-2"

    def test_wrap_with_list_data(self) -> None:
        ctx = EnvelopeContext.new(path_y=None)
        wrapped = ctx.wrap([1, 2, 3])
        assert wrapped["data"] == [1, 2, 3]


class TestEnvelopeModel:
    """Envelope / EnvelopeMeta Pydantic model."""

    def test_envelope_serialization(self) -> None:
        meta = EnvelopeMeta(
            request_id="req_001",
            timestamp="2026-06-26T00:00:00Z",
            api_version="v0-2",
            caller_user_id=None,
            path_y_validated=False,
        )
        env = Envelope(envelope=meta, data={"x": 1})
        dumped = env.model_dump(mode="json")
        assert dumped["envelope"]["request_id"] == "req_001"
        assert dumped["data"] == {"x": 1}

    def test_envelope_default_api_version(self) -> None:
        meta = EnvelopeMeta(
            request_id="req_001",
            timestamp="2026-06-26T00:00:00Z",
        )
        assert meta.api_version == "v0-2"