const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Flashcard = {
  id: number;
  question: string;
  answer: string;
  concept: string;
  difficulty: "easy" | "medium" | "hard";
  box: number;
  interval_days: number;
  due_at: string;
  review_count: number;
  correct_count: number;
  last_result: string;
  explanation_cache?: string | null;
};

export type Deck = {
  id: number;
  title: string;
  source_filename: string;
  source_excerpt: string;
  created_at: string;
  summary: { heading: string; points: string[] }[];
  metrics: {
    total_cards: number;
    due_cards: number;
    mastered_cards: number;
    accuracy: number;
    weak_areas: string[];
  };
  cards: Flashcard[];
};

export type DeckListItem = {
  id: number;
  title: string;
  source_filename: string;
  created_at: string;
  metrics: Deck["metrics"];
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    cache: "no-store"
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Request failed");
  }

  return response.json();
}

export function listDecks() {
  return request<DeckListItem[]>("/api/decks");
}

export function getDeck(id: string) {
  return request<Deck>(`/api/decks/${id}`);
}

export function createDeck(formData: FormData) {
  return request<Deck>("/api/decks/from-pdf", {
    method: "POST",
    body: formData
  });
}

export function reviewCard(cardId: number, result: "known" | "unknown") {
  return request<Flashcard>(`/api/cards/${cardId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ result })
  });
}

export function explainCard(cardId: number) {
  return request<{ explanation: string }>(`/api/cards/${cardId}/explain`, {
    method: "POST"
  });
}

export function regenerateCard(cardId: number) {
  return request<{ card: Flashcard }>(`/api/cards/${cardId}/regenerate`, {
    method: "POST"
  });
}
