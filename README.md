# Flashcard Engine

Flashcard Engine is a full-stack study app that turns PDFs into reusable flashcard decks, then helps learners retain material through active recall, spaced repetition, and lightweight AI tutoring.

## What was built

- PDF upload and parsing with heading-aware structure extraction
- AI flashcard generation focused on definitions, relationships, and examples
- Study mode with flip interaction, Known/Unknown review, and due-card prioritization
- Simple Leitner-style spaced repetition with difficulty-aware scheduling
- Progress tracking for due cards, mastery, accuracy, and weak areas
- Deck persistence with SQLite so users can revisit previous sessions
- AI actions for card explanation and card improvement

## Architecture

### Frontend

- Framework: Next.js App Router
- Role: upload PDFs, browse decks, run study sessions, show progress
- API integration: `NEXT_PUBLIC_API_URL`

### Backend

- Framework: FastAPI
- Storage: SQLite via SQLAlchemy
- PDF parsing: PyMuPDF
- AI layer: Google AI Studio Gemini API
- Core logic:
  - `pdf_service.py`: extracts headings and content blocks from PDFs
  - `ai_service.py`: generates, explains, and regenerates flashcards
  - `review_service.py`: applies Leitner-style review updates and computes metrics

## Folder structure

```text
cuemath/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── .env.example
│   └── package.json
└── docs/
```

## Local setup

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill `backend/.env`:

```env
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-2.5-flash
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///./data/app.db
```

Free Gemini model options you can swap into `GEMINI_MODEL`:

- `gemini-3-flash-preview`
- `gemini-3.1-flash-lite-preview`
- `gemini-3.1-flash-live-preview`
- `gemini-2.5-pro`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`

The code defaults to `gemini-2.5-flash` because it is a solid stable choice for this workload.

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env.local
```

Set:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the app:

```bash
npm run dev
```

## Deployment guide

### Frontend on Vercel

1. Push the repo to GitHub.
2. Import the `frontend` directory as a Vercel project.
3. Set `NEXT_PUBLIC_API_URL` to your deployed backend URL.
4. Deploy.

### Backend on Render

1. Create a new Web Service from the same GitHub repo.
2. Set the root directory to `backend`.
3. Build command:

```bash
pip install -r requirements.txt
```

4. Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Add environment variables:
  - `GEMINI_API_KEY`
  - `GEMINI_MODEL`
   - `FRONTEND_URL`
   - `DATABASE_URL`

Use a persistent disk if you want SQLite data to survive restarts. If you want more reliable production persistence later, switch to Postgres.

## Key decisions and tradeoffs

- SQLite keeps setup and deployment fast for an MVP, but Postgres would be better for multi-user scale.
- The heading extraction is heuristic, which is fast and practical, but not as robust as a full document understanding pipeline.
- The Leitner system is intentionally simple so the review behavior is easy to trust and debug.
- AI is used where it matters most for learning quality: card generation, explanation, and improvement.

## Testing suggestions

- Backend:
  - verify PDF upload rejects non-PDF files
  - verify a deck persists cards and summary blocks
  - verify Known/Unknown changes box and due date correctly
  - mock Gemini responses for generation and explanation tests
- Frontend:
  - test upload flow
  - test card flip and review actions
  - test empty-state and failed-request handling
- Product QA:
  - upload short, long, and messy PDFs
  - check whether cards feel concept-based rather than extractive
  - review if weak areas actually reflect misses

## What I would improve next

- user accounts and cross-device sync
- richer study analytics over time
- card editing in bulk before first study session
- stronger PDF structure extraction with OCR fallback
- semantic duplicate-card removal and better source citations

## Short write-up

This MVP focuses on the learning loop, not just the upload moment. The product tries to make studying feel directed and useful: generate better cards, surface what is due, explain confusing concepts, and show progress that motivates another session.

The biggest tradeoff was choosing speed and reliability over sophistication. I used a simple review algorithm, heuristic PDF structure parsing, and SQLite persistence so the app can be built and deployed quickly under time constraints while still feeling like a real product.

## Video walkthrough outline

Use this 2 to 5 minute structure:

1. Problem: students reread PDFs but forget quickly.
2. Solution: upload once, get concept-based cards, and come back to due reviews.
3. Demo:
   - upload a PDF
   - open generated deck
   - flip a card
   - mark Known/Unknown
   - show explanation and regenerate
   - show progress and weak areas
4. Decisions:
   - why concept-rich cards matter
   - why spaced repetition is built into the MVP
   - why SQLite + FastAPI + Next.js kept delivery fast
