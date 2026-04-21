"use client";

import { useMemo, useState, useTransition } from "react";

import { Deck, Flashcard, explainCard, regenerateCard, reviewCard } from "@/lib/api";

type Props = {
  initialDeck: Deck;
};

function difficultyTone(difficulty: Flashcard["difficulty"]) {
  if (difficulty === "hard") {
    return "tag danger";
  }
  if (difficulty === "easy") {
    return "tag success";
  }
  return "tag";
}

export function StudyClient({ initialDeck }: Props) {
  const [deck, setDeck] = useState(initialDeck);
  const [cardIndex, setCardIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [explanation, setExplanation] = useState("");
  const [feedback, setFeedback] = useState("");
  const [isPending, startTransition] = useTransition();

  const dueCards = useMemo(
    () => deck.cards.filter((card) => new Date(card.due_at).getTime() <= Date.now()),
    [deck.cards]
  );
  const activeCards = dueCards.length ? dueCards : deck.cards;
  const activeCard = activeCards[Math.min(cardIndex, Math.max(activeCards.length - 1, 0))];

  function replaceCard(updatedCard: Flashcard) {
    setDeck((current) => ({
      ...current,
      cards: current.cards.map((card) => (card.id === updatedCard.id ? updatedCard : card)),
      metrics: {
        ...current.metrics,
        due_cards: current.cards.filter((card) => {
          const candidate = card.id === updatedCard.id ? updatedCard : card;
          return new Date(candidate.due_at).getTime() <= Date.now();
        }).length,
        mastered_cards: current.cards.filter((card) => {
          const candidate = card.id === updatedCard.id ? updatedCard : card;
          return candidate.box >= 4;
        }).length
      }
    }));
  }

  function moveNext() {
    setRevealed(false);
    setExplanation("");
    setFeedback("");
    setCardIndex((current) => (activeCards.length ? (current + 1) % activeCards.length : 0));
  }

  async function handleReview(result: "known" | "unknown") {
    if (!activeCard) return;
    startTransition(async () => {
      const updated = await reviewCard(activeCard.id, result);
      replaceCard(updated);
      setFeedback(result === "known" ? "Nice. This card moved forward in the review queue." : "Marked for another pass soon.");
      moveNext();
    });
  }

  async function handleExplain() {
    if (!activeCard) return;
    startTransition(async () => {
      const response = await explainCard(activeCard.id);
      setExplanation(response.explanation);
    });
  }

  async function handleRegenerate() {
    if (!activeCard) return;
    startTransition(async () => {
      const response = await regenerateCard(activeCard.id);
      replaceCard(response.card);
      setFeedback("This card was improved to test understanding more clearly.");
      setRevealed(false);
      setExplanation("");
    });
  }

  if (!activeCard) {
    return (
      <section className="panel">
        <h2>No cards yet</h2>
        <p className="muted">This deck has not generated any cards. Re-upload or inspect the backend logs.</p>
      </section>
    );
  }

  return (
    <div className="study-layout">
      <section className="panel hero-panel">
        <p className="eyebrow">Study session</p>
        <h1>{deck.title}</h1>
        <div className="stats-row">
          <span>{deck.metrics.total_cards} total</span>
          <span>{dueCards.length} due now</span>
          <span>{deck.metrics.mastered_cards} mastered</span>
          <span>{deck.metrics.accuracy}% accuracy</span>
        </div>
        <div className="weak-area-list">
          {(deck.metrics.weak_areas.length ? deck.metrics.weak_areas : ["No weak areas yet"]).map((item) => (
            <span className="tag" key={item}>
              {item}
            </span>
          ))}
        </div>
      </section>

      <section className="flashcard-shell">
        <div className="flashcard panel">
          <div className="deck-card-header">
            <span className={difficultyTone(activeCard.difficulty)}>{activeCard.difficulty}</span>
            <span className="muted">Concept: {activeCard.concept || "General"}</span>
          </div>
          <div className="flashcard-content">
            <p className="eyebrow">{revealed ? "Answer" : "Question"}</p>
            <h2>{revealed ? activeCard.answer : activeCard.question}</h2>
          </div>
          <button className="ghost-button" onClick={() => setRevealed((current) => !current)} type="button">
            {revealed ? "Hide answer" : "Reveal answer"}
          </button>
        </div>

        <div className="action-row">
          <button className="danger-button" disabled={isPending} onClick={() => handleReview("unknown")} type="button">
            Unknown
          </button>
          <button className="primary-button" disabled={isPending} onClick={() => handleReview("known")} type="button">
            Known
          </button>
        </div>

        <div className="action-row secondary-actions">
          <button className="ghost-button" disabled={isPending} onClick={handleExplain} type="button">
            Explain this card
          </button>
          <button className="ghost-button" disabled={isPending} onClick={handleRegenerate} type="button">
            Improve card
          </button>
        </div>

        {feedback ? <p className="muted">{feedback}</p> : null}
        {explanation ? (
          <section className="panel">
            <p className="eyebrow">Tutor mode</p>
            <p>{explanation}</p>
          </section>
        ) : null}
      </section>

      <section className="panel">
        <p className="eyebrow">Deck structure</p>
        <div className="summary-list">
          {deck.summary.map((section) => (
            <article key={section.heading}>
              <h3>{section.heading}</h3>
              <ul>
                {section.points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

