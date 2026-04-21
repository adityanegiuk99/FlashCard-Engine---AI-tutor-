"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { createDeck } from "@/lib/api";

export function UploadForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!title || !file) {
      setError("Add a deck name and a PDF to continue.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("file", file);
      const deck = await createDeck(formData);
      router.push(`/decks/${deck.id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="panel upload-panel" onSubmit={handleSubmit}>
      <div>
        <p className="eyebrow">Create a deck</p>
        <h2>Turn a PDF into active recall practice</h2>
        <p className="muted">
          We extract structure, generate concept-rich cards, and schedule review automatically.
        </p>
      </div>
      <label className="field">
        <span>Deck name</span>
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Human Physiology - Unit 3"
        />
      </label>
      <label className="field">
        <span>PDF</span>
        <input
          type="file"
          accept="application/pdf"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
      </label>
      {error ? <p className="error-text">{error}</p> : null}
      <button className="primary-button" disabled={loading} type="submit">
        {loading ? "Generating deck..." : "Upload and generate"}
      </button>
    </form>
  );
}

