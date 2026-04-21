from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Difficulty = Literal["easy", "medium", "hard"]
ReviewResult = Literal["known", "unknown"]


class SummaryBlock(BaseModel):
    heading: str
    points: list[str] = Field(default_factory=list)


class FlashcardBase(BaseModel):
    question: str
    answer: str
    concept: str
    difficulty: Difficulty


class FlashcardRead(FlashcardBase):
    id: int
    box: int
    interval_days: int
    due_at: datetime
    review_count: int
    correct_count: int
    last_result: str
    explanation_cache: str | None

    class Config:
        from_attributes = True


class DeckMetrics(BaseModel):
    total_cards: int
    due_cards: int
    mastered_cards: int
    accuracy: float
    weak_areas: list[str]


class DeckRead(BaseModel):
    id: int
    title: str
    source_filename: str
    source_excerpt: str
    summary: list[SummaryBlock]
    created_at: datetime
    metrics: DeckMetrics
    cards: list[FlashcardRead]

    class Config:
        from_attributes = True


class DeckListItem(BaseModel):
    id: int
    title: str
    source_filename: str
    created_at: datetime
    metrics: DeckMetrics


class ReviewRequest(BaseModel):
    result: ReviewResult


class ExplanationResponse(BaseModel):
    explanation: str


class RegenerateResponse(BaseModel):
    card: FlashcardRead

