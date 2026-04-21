from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from app.models import Deck, Flashcard, ReviewEvent
from app.schemas import DeckMetrics


BOX_INTERVALS = {
    1: 1,
    2: 2,
    3: 4,
    4: 7,
    5: 14,
}


def apply_review(card: Flashcard, result: str) -> ReviewEvent:
    previous_box = card.box
    if result == "known":
        card.box = min(5, card.box + 1)
        card.correct_count += 1
    else:
        card.box = 1

    interval = BOX_INTERVALS[card.box]
    if card.difficulty == "hard":
        interval = max(1, interval - 1)
    elif card.difficulty == "easy":
        interval += 1

    card.interval_days = interval
    card.review_count += 1
    card.last_result = result
    card.due_at = datetime.utcnow() + timedelta(days=interval if result == "known" else 1)

    confidence = round(card.correct_count / max(card.review_count, 1), 2)
    return ReviewEvent(
        result=result,
        previous_box=previous_box,
        new_box=card.box,
        confidence=confidence,
    )


def compute_metrics(deck: Deck) -> DeckMetrics:
    now = datetime.utcnow()
    total_cards = len(deck.cards)
    due_cards = sum(1 for card in deck.cards if card.due_at <= now)
    mastered_cards = sum(1 for card in deck.cards if card.box >= 4)
    total_reviews = sum(card.review_count for card in deck.cards)
    total_correct = sum(card.correct_count for card in deck.cards)
    accuracy = round((total_correct / total_reviews) * 100, 1) if total_reviews else 0.0

    misses = Counter(
        card.concept
        for card in deck.cards
        if card.last_result == "unknown" or card.difficulty == "hard"
    )
    weak_areas = [concept for concept, _ in misses.most_common(3) if concept]

    return DeckMetrics(
        total_cards=total_cards,
        due_cards=due_cards,
        mastered_cards=mastered_cards,
        accuracy=accuracy,
        weak_areas=weak_areas,
    )

