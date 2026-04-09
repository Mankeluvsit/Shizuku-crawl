from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class MatchEvidence:
    source: str
    reason: str
    detail: str | None = None
    file_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MatchEvidence":
        return cls(
            source=str(data.get("source", "unknown")),
            reason=str(data.get("reason", "unknown")),
            detail=data.get("detail"),
            file_path=data.get("file_path"),
        )


@dataclass(slots=True)
class ReleaseInfo:
    has_downloads: bool = False
    release_url: str | None = None
    release_tag: str | None = None
    release_published_at: str | None = None
    apk_assets: list[str] = field(default_factory=list)
    aab_assets: list[str] = field(default_factory=list)
    universal_apk_assets: list[str] = field(default_factory=list)
    split_apk_assets: list[str] = field(default_factory=list)
    checksum_assets: list[str] = field(default_factory=list)
    quality_label: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReleaseInfo":
        return cls(
            has_downloads=bool(data.get("has_downloads", False)),
            release_url=data.get("release_url"),
            release_tag=data.get("release_tag"),
            release_published_at=data.get("release_published_at"),
            apk_assets=list(data.get("apk_assets", [])),
            aab_assets=list(data.get("aab_assets", [])),
            universal_apk_assets=list(data.get("universal_apk_assets", [])),
            split_apk_assets=list(data.get("split_apk_assets", [])),
            checksum_assets=list(data.get("checksum_assets", [])),
            quality_label=str(data.get("quality_label", "unknown")),
        )


@dataclass(slots=True)
class SourceAttribution:
    scanner: str
    source_type: str = "unknown"
    trust_level: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceAttribution":
        return cls(
            scanner=str(data.get("scanner", "unknown")),
            source_type=str(data.get("source_type", "unknown")),
            trust_level=str(data.get("trust_level", "medium")),
        )


@dataclass(slots=True)
class ReviewState:
    status: str = "new"
    review_notes: str | None = None
    reviewed_at: str | None = None
    reviewed_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReviewState":
        return cls(
            status=str(data.get("status", "new")),
            review_notes=data.get("review_notes"),
            reviewed_at=data.get("reviewed_at"),
            reviewed_by=data.get("reviewed_by"),
        )


@dataclass(slots=True)
class AppResult:
    name: str
    urls: list[str]
    scanner: str
    desc: str | None = None
    package_id: str | None = None
    application_id: str | None = None
    last_updated: datetime | None = None
    has_downloads: bool = False
    confidence: str = "low"
    usefulness: str = "low"
    match_reasons: list[str] = field(default_factory=list)
    evidence: list[MatchEvidence] = field(default_factory=list)
    sources: list[SourceAttribution] = field(default_factory=list)
    release_info: ReleaseInfo = field(default_factory=ReleaseInfo)
    first_seen: str | None = None
    last_seen: str | None = None
    status: str = "new"
    review_notes: str | None = None
    reviewed_at: str | None = None
    reviewed_by: str | None = None

    def __hash__(self) -> int:
        return hash(self.identity_key())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AppResult):
            return False
        return self.identity_key() == other.identity_key()

    def identity_key(self) -> tuple[str, str]:
        if self.package_id:
            return ("package", self.package_id.casefold())
        primary = self.urls[0] if self.urls else ""
        return (self.name.casefold(), primary.casefold())

    def identity_key_str(self) -> str:
        key = self.identity_key()
        return f"{key[0]}::{key[1]}"

    def merge(self, other: "AppResult") -> "AppResult":
        merged_urls = sorted(set([*self.urls, *other.urls]))
        merged_reasons = sorted(set([*self.match_reasons, *other.match_reasons]))
        merged_evidence = self.evidence + [ev for ev in other.evidence if ev not in self.evidence]
        merged_sources = self.sources + [src for src in other.sources if src not in self.sources]
        merged_desc = self.desc if self.desc and len(self.desc) >= len(other.desc or "") else other.desc

        last_updated = self.last_updated or other.last_updated
        if self.last_updated and other.last_updated:
            last_updated = max(self.last_updated, other.last_updated)

        release = self.release_info if self.release_info.has_downloads else other.release_info
        has_downloads = self.has_downloads or other.has_downloads or release.has_downloads

        return AppResult(
            name=self.name if len(self.name) >= len(other.name) else other.name,
            urls=merged_urls,
            scanner=self.scanner,
            desc=merged_desc,
            package_id=self.package_id or other.package_id,
            application_id=self.application_id or other.application_id,
            last_updated=last_updated,
            has_downloads=has_downloads,
            confidence=self.confidence,
            usefulness=self.usefulness,
            match_reasons=merged_reasons,
            evidence=merged_evidence,
            sources=merged_sources,
            release_info=release,
            first_seen=self.first_seen or other.first_seen,
            last_seen=other.last_seen or self.last_seen,
            status=self.status,
            review_notes=self.review_notes or other.review_notes,
            reviewed_at=self.reviewed_at or other.reviewed_at,
            reviewed_by=self.reviewed_by or other.reviewed_by,
        )

    def apply_review_state(self, state: ReviewState | None) -> None:
        if not state:
            return
        self.status = state.status
        self.review_notes = state.review_notes
        self.reviewed_at = state.reviewed_at
        self.reviewed_by = state.reviewed_by

    def to_review_state(self) -> ReviewState:
        return ReviewState(
            status=self.status,
            review_notes=self.review_notes,
            reviewed_at=self.reviewed_at,
            reviewed_by=self.reviewed_by,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "urls": self.urls,
            "scanner": self.scanner,
            "desc": self.desc,
            "package_id": self.package_id,
            "application_id": self.application_id,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "has_downloads": self.has_downloads,
            "confidence": self.confidence,
            "usefulness": self.usefulness,
            "match_reasons": self.match_reasons,
            "evidence": [ev.to_dict() for ev in self.evidence],
            "sources": [src.to_dict() for src in self.sources],
            "release_info": self.release_info.to_dict(),
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "status": self.status,
            "review_notes": self.review_notes,
            "reviewed_at": self.reviewed_at,
            "reviewed_by": self.reviewed_by,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppResult":
        last_updated_raw = data.get("last_updated")
        last_updated = None
        if isinstance(last_updated_raw, str) and last_updated_raw:
            try:
                parsed = datetime.fromisoformat(last_updated_raw)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=UTC)
                last_updated = parsed.astimezone(UTC)
            except Exception:
                last_updated = None

        return cls(
            name=str(data.get("name", "")),
            urls=list(data.get("urls", [])),
            scanner=str(data.get("scanner", "unknown")),
            desc=data.get("desc"),
            package_id=data.get("package_id"),
            application_id=data.get("application_id"),
            last_updated=last_updated,
            has_downloads=bool(data.get("has_downloads", False)),
            confidence=str(data.get("confidence", "low")),
            usefulness=str(data.get("usefulness", "low")),
            match_reasons=list(data.get("match_reasons", [])),
            evidence=[MatchEvidence.from_dict(item) for item in data.get("evidence", [])],
            sources=[SourceAttribution.from_dict(item) for item in data.get("sources", [])],
            release_info=ReleaseInfo.from_dict(data.get("release_info", {})),
            first_seen=data.get("first_seen"),
            last_seen=data.get("last_seen"),
            status=str(data.get("status", "new")),
            review_notes=data.get("review_notes"),
            reviewed_at=data.get("reviewed_at"),
            reviewed_by=data.get("reviewed_by"),
        )
