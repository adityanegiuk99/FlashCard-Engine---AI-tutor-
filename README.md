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
- AI layer: OpenRouter-compatible chat completions
- Core logic:
  - `pdf_service.py`: extracts headings and content blocks from PDFs
  - `ai_service.py`: generates, explains, and regenerates flashcards
  - `review_service.py`: applies Leitner-style review updates and computes metrics

## Folder structure

```text
flashcard-engine/
|-- backend/
|   |-- app/
|   |   |-- services/
|   |   |-- config.py
|   |   |-- database.py
|   |   |-- main.py
|   |   |-- models.py
|   |   `-- schemas.py
|   |-- .env.example
|   `-- requirements.txt
|-- frontend/
|   |-- app/
|   |-- components/
|   |-- lib/
|   |-- .env.example
|   `-- package.json
|-- render.yaml
`-- vercel.json
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
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-3.5-turbo
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///C:/absolute/path/to/backend/data/app.db
```

If `DATABASE_URL` is omitted, the app defaults to `backend/data/app.db`.

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

1. Import the GitHub repo into Vercel.
2. Either set the project root to `frontend/` in the Vercel UI or keep the repo root and use the included root `vercel.json`.
3. Add `NEXT_PUBLIC_API_URL=https://your-backend-service.onrender.com`.
4. Deploy.

### Backend on Render

1. Create a new Web Service from the same GitHub repo.
2. Use the included `render.yaml`, or manually set the root directory to `backend`.
3. Build command:

```bash
pip install -r requirements.txt
```

4. Start command:

```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT app.main:app
```

5. Add environment variables:
   - `OPENROUTER_API_KEY`
   - `OPENROUTER_MODEL`
   - `FRONTEND_URL`
   - `DATABASE_URL`

For Render + SQLite, mount a persistent disk and point `DATABASE_URL` at that disk, for example `sqlite:////var/data/app.db`. The included `render.yaml` already does this.

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
  - mock OpenRouter responses for generation and explanation tests
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
