import Link from "next/link";
import { notFound } from "next/navigation";

import { StudyClient } from "@/components/study-client";
import { getDeck } from "@/lib/api";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function DeckPage({ params }: Props) {
  const { id } = await params;
  const deck = await getDeck(id).catch(() => null);

  if (!deck) {
    notFound();
  }

  return (
    <main className="page-shell">
      <Link className="back-link" href="/">
        Back to decks
      </Link>
      <StudyClient initialDeck={deck} />
    </main>
  );
}

