import Link from "next/link";

import { DeckListItem } from "@/lib/api";

type Props = {
  decks: DeckListItem[];
};

export function DeckGrid({ decks }: Props) {
  if (!decks.length) {
    return (
      <section className="panel">
        <p className="eyebrow">No decks yet</p>
        <h3>Your first upload becomes a reusable study system</h3>
        <p className="muted">Once a deck exists, you will see due cards, mastery, and weak areas here.</p>
      </section>
    );
  }

  return (
    <section className="deck-grid">
      {decks.map((deck) => (
        <Link className="panel deck-card" href={`/decks/${deck.id}`} key={deck.id}>
          <div className="deck-card-header">
            <div>
              <p className="eyebrow">Deck</p>
              <h3>{deck.title}</h3>
            </div>
            <span className="tag">{deck.metrics.due_cards} due</span>
          </div>
          <p className="muted">{deck.source_filename}</p>
          <div className="stats-row">
            <span>{deck.metrics.total_cards} cards</span>
            <span>{deck.metrics.mastered_cards} mastered</span>
            <span>{deck.metrics.accuracy}% accuracy</span>
          </div>
        </Link>
      ))}
    </section>
  );
}
