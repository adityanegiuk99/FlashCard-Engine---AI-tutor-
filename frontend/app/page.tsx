import { DeckGrid } from "@/components/deck-grid";
import { UploadForm } from "@/components/upload-form";
import { listDecks } from "@/lib/api";

export default async function HomePage() {
  const decks = await listDecks().catch(() => []);

  return (
    <main className="page-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Flashcard Engine</p>
          <h1>Study from PDFs with active recall, not passive rereading.</h1>
          <p className="hero-copy">
            Upload a PDF, generate higher-quality flashcards, and keep returning to the cards that need work most.
          </p>
        </div>
        <div className="hero-metrics">
          <div className="metric-tile">
            <strong>{decks.length}</strong>
            <span>Decks created</span>
          </div>
          <div className="metric-tile">
            <strong>{decks.reduce((sum, deck) => sum + deck.metrics.total_cards, 0)}</strong>
            <span>Total cards</span>
          </div>
          <div className="metric-tile">
            <strong>{decks.reduce((sum, deck) => sum + deck.metrics.due_cards, 0)}</strong>
            <span>Due now</span>
          </div>
        </div>
      </section>

      <div className="home-grid">
        <UploadForm />
        <div className="home-list">
          <DeckGrid decks={decks} />
        </div>
      </div>
    </main>
  );
}

