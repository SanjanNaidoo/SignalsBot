"""Course configuration loading.

Adapting the tutor to a new course must mean writing a new YAML file, not
changing code. Everything course-specific is read from here.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Topic:
    id: str
    name: str


@dataclass(frozen=True)
class Policy:
    socratic_on_assessed_work: bool = True
    require_citations: bool = True
    refuse_out_of_scope: bool = True
    notation_source: str = "course_notes"


@dataclass(frozen=True)
class Retrieval:
    chunk_tokens: int = 800
    chunk_overlap_tokens: int = 150
    top_k: int = 8


@dataclass(frozen=True)
class Model:
    """Default model settings. Conditions may override id, provider and effort.

    `provider` selects the backend: "anthropic" for the hosted frontier arm,
    "local" for a self-hosted open-weights model. The `local_*` fields are read
    only by the local provider and ignored otherwise.
    """

    id: str = "claude-opus-5"
    provider: str = "anthropic"
    max_tokens: int = 16000
    effort: str = "high"

    # Local provider only. Greedy by default: unlike the hosted models, local
    # inference does expose temperature and a seed, so the open arm can be made
    # exactly reproducible and needs no variance runs.
    local_max_new_tokens: int = 1024
    local_load_in_4bit: bool = True
    local_temperature: float = 0.0
    local_seed: int = 0


@dataclass(frozen=True)
class CourseConfig:
    code: str
    name: str
    institution: str
    level: int
    convener: str | None
    topics: tuple[Topic, ...]
    policy: Policy
    retrieval: Retrieval
    model: Model
    path: Path
    digest: str = field(compare=False, default="")

    @property
    def topic_ids(self) -> set[str]:
        return {t.id for t in self.topics}

    def topic_name(self, topic_id: str) -> str:
        for t in self.topics:
            if t.id == topic_id:
                return t.name
        return topic_id


def load_config(path: str | Path) -> CourseConfig:
    """Read a course YAML file into a CourseConfig.

    The digest is recorded in every run manifest so a result can always be traced
    back to the exact configuration that produced it.
    """
    path = Path(path)
    raw_bytes = path.read_bytes()
    raw = yaml.safe_load(raw_bytes)

    course = raw.get("course") or {}
    if not course.get("code"):
        raise ValueError(f"{path}: course.code is required")

    topics = tuple(
        Topic(id=t["id"], name=t.get("name", t["id"])) for t in raw.get("topics") or []
    )
    if not topics:
        raise ValueError(f"{path}: at least one topic is required")

    return CourseConfig(
        code=course["code"],
        name=course.get("name", course["code"]),
        institution=course.get("institution", ""),
        level=int(course.get("level", 0)),
        convener=course.get("convener"),
        topics=topics,
        policy=Policy(**(raw.get("policy") or {})),
        retrieval=Retrieval(**(raw.get("retrieval") or {})),
        model=Model(**(raw.get("model") or {})),
        path=path,
        digest=hashlib.sha256(raw_bytes).hexdigest()[:16],
    )
