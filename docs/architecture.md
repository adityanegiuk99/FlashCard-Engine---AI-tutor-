# System architecture

## End-to-end flow

1. User uploads a PDF from the Next.js frontend.
2. FastAPI parses text and heading-like blocks with PyMuPDF.
3. Parsed content is sent to the LLM to generate structured flashcards.
4. Deck and cards are stored in SQLite.
5. Study mode prioritizes cards due for review.
6. Known/Unknown updates each card's Leitner box and next due date.
7. Metrics aggregate mastery, due count, accuracy, and weak areas.

## Why this architecture works for the challenge

- It optimizes for a usable MVP with real persistence and deployability.
- It keeps AI focused on the highest-value moments instead of overusing it.
- It leaves a clean migration path from SQLite to Postgres and from heuristics to richer document understanding.
