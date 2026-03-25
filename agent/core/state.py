from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ConceptStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    TAUGHT = "taught"
    QUIZZED = "quizzed"
    MASTERED = "mastered"
    NEEDS_RETRY = "needs_retry"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ConceptProgress(BaseModel):
    concept_name: str
    status: ConceptStatus = ConceptStatus.NOT_STARTED
    quiz_taken: bool = False
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    retry_count: int = Field(default=0, ge=0)
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    taught_at: Optional[datetime] = None
    quizzed_at: Optional[datetime] = None

    def mark_taught(self) -> None:
        self.status = ConceptStatus.TAUGHT
        self.taught_at = datetime.now()

    def mark_quizzed(self, score: float) -> None:
        self.quiz_taken = True
        self.score = score
        self.quizzed_at = datetime.now()
        if score >= 0.8:
            self.status = ConceptStatus.MASTERED
        elif score >= 0.6:
            self.status = ConceptStatus.QUIZZED
        else:
            self.status = ConceptStatus.NEEDS_RETRY
            self.retry_count += 1

    def increment_retry(self) -> None:
        self.retry_count += 1
        self.status = ConceptStatus.NEEDS_RETRY

    def update_difficulty(self, level: DifficultyLevel) -> None:
        self.difficulty_level = level

    def reset_for_retry(self) -> None:
        self.quiz_taken = False
        self.score = None
        self.quizzed_at = None
        self.status = ConceptStatus.IN_PROGRESS


class StudySessionState(BaseModel):
    session_id: str
    topic: str
    concepts: dict[str, ConceptProgress] = Field(default_factory=dict)
    current_concept: Optional[str] = None
    session_start_time: datetime = Field(default_factory=datetime.now)
    overall_difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    concepts_planned: list[str] = Field(default_factory=list)
    loaded_content: Optional[dict[str, Any]] = Field(
        default=None,
        description="Serialised LoadedContent from user-uploaded study materials",
    )

    def add_concept(self, concept_name: str, difficulty: DifficultyLevel = DifficultyLevel.BEGINNER) -> None:
        if concept_name not in self.concepts:
            self.concepts[concept_name] = ConceptProgress(
                concept_name=concept_name,
                difficulty_level=difficulty
            )

    def set_current_concept(self, concept_name: str) -> None:
        if concept_name in self.concepts:
            self.current_concept = concept_name
            if self.concepts[concept_name].status == ConceptStatus.NOT_STARTED:
                self.concepts[concept_name].status = ConceptStatus.IN_PROGRESS

    def mark_concept_taught(self, concept_name: str) -> None:
        if concept_name in self.concepts:
            self.concepts[concept_name].mark_taught()

    def mark_concept_quizzed(self, concept_name: str, score: float) -> None:
        if concept_name in self.concepts:
            self.concepts[concept_name].mark_quizzed(score)

    def get_concept_progress(self, concept_name: str) -> Optional[ConceptProgress]:
        return self.concepts.get(concept_name)

    def get_taught_concepts(self) -> list[str]:
        return [
            name for name, progress in self.concepts.items()
            if progress.status in [ConceptStatus.TAUGHT, ConceptStatus.QUIZZED, ConceptStatus.MASTERED]
        ]

    def get_mastered_concepts(self) -> list[str]:
        return [
            name for name, progress in self.concepts.items()
            if progress.status == ConceptStatus.MASTERED
        ]

    def get_concepts_needing_retry(self) -> list[str]:
        return [
            name for name, progress in self.concepts.items()
            if progress.status == ConceptStatus.NEEDS_RETRY
        ]

    def update_overall_difficulty(self, level: DifficultyLevel) -> None:
        self.overall_difficulty = level

    def get_progress_percentage(self) -> float:
        if not self.concepts:
            return 0.0
        mastered = len(self.get_mastered_concepts())
        total = len(self.concepts)
        return mastered / total if total > 0 else 0.0

    def get_average_score(self) -> Optional[float]:
        scores = [p.score for p in self.concepts.values() if p.score is not None]
        if not scores:
            return None
        return sum(scores) / len(scores)

    # -- Content loader helpers ------------------------------------------------

    def set_loaded_content(self, content_dict: dict[str, Any]) -> None:
        """Store serialised LoadedContent from the content loader."""
        self.loaded_content = content_dict

    def has_loaded_content(self) -> bool:
        """Return True if user-uploaded material is available."""
        return self.loaded_content is not None

    def get_content_context(self, max_chars: int = 2000) -> str:
        """Return a truncated string of the loaded material for LLM prompts."""
        if self.loaded_content is None:
            return ""
        raw = self.loaded_content.get("raw_text", "")
        if len(raw) <= max_chars:
            return raw
        return raw[:max_chars] + "\n\n[... content truncated ...]"

