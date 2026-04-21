# Flashcard Engine Write-up

## What was built

Flashcard Engine is a lightweight learning product that transforms PDFs into study decks designed for active recall. Instead of stopping at document extraction, the product focuses on three learning outcomes: high-quality card creation, repeat exposure to weak material, and visible progress over time.

## Key decisions and tradeoffs

- I used a FastAPI plus Next.js split because it is fast to build, easy to deploy, and keeps AI and file handling off the client.
- I used SQLite for speed and simplicity. It is the right MVP choice, but I would switch to Postgres for production multi-user use.
- I chose a simple Leitner-style review engine instead of a more advanced spaced repetition formula because it is easier to explain, easier to debug, and still clearly improves practice quality.
- I added AI explanation and card regeneration because they improve trust in deck quality without requiring a complicated authoring workflow.
- I included a local fallback card generator so the app still works in a degraded mode if an API key is missing during development.

## What I would improve next

- Stronger PDF parsing for scanned files and messy layouts
- User accounts and cloud persistence
- Better AI validation, retries, and structured output guarantees
- Session history, streaks, and more detailed mastery reporting
- Deck editing tools for teachers and power users

## 2-5 minute walkthrough outline

1. Open with the problem: students read PDFs passively and forget quickly.
2. Show the upload flow and explain how structure extraction and AI card generation work together.
3. Open a deck and show flip, known, unknown, explain, and regenerate.
4. Point out due cards, mastered cards, weak areas, and accuracy.
5. Close with the product thinking: the goal is retention, not just PDF conversion.
