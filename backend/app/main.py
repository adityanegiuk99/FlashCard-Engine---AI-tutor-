from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import Deck, Flashcard
from app.schemas import DeckListItem, DeckRead, ExplanationResponse, FlashcardRead, RegenerateResponse, ReviewRequest
from app.services.ai_service import explain_flashcard, generate_flashcards, regenerate_flashcard
from app.services.pdf_service import extract_pdf_structure
from app.services.review_service import apply_review, compute_metrics


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Configure CORS origins
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://flash-card-engine-ai-tutor.vercel.app",  # Deployed frontend
]
frontend_url_clean = settings.frontend_url_clean
if frontend_url_clean and frontend_url_clean not in cors_origins:
    cors_origins.append(frontend_url_clean)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize_deck(deck: Deck) -> DeckRead:
    return DeckRead(
        id=deck.id,
        title=deck.title,
        source_filename=deck.source_filename,
        source_excerpt=deck.source_excerpt,
        summary=deck.summary,
        created_at=deck.created_at,
        metrics=compute_metrics(deck),
        cards=[FlashcardRead.model_validate(card) for card in deck.cards],
    )


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.get("/api/decks", response_model=list[DeckListItem])
def list_decks(db: Session = Depends(get_db)):
    decks = db.query(Deck).order_by(Deck.created_at.desc()).all()
    return [
        DeckListItem(
            id=deck.id,
            title=deck.title,
            source_filename=deck.source_filename,
            created_at=deck.created_at,
            metrics=compute_metrics(deck),
        )
        for deck in decks
    ]


@app.get("/api/decks/{deck_id}", response_model=DeckRead)
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return serialize_deck(deck)


@app.post("/api/decks/from-pdf", response_model=DeckRead)
async def create_deck_from_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    pdf_bytes = await file.read()
    structure = extract_pdf_structure(pdf_bytes)

    try:
        generated_cards = generate_flashcards(title, structure["excerpt"], structure["summary"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {exc}") from exc

    deck = Deck(
        title=title,
        source_filename=file.filename,
        source_excerpt=structure["excerpt"],
        summary=structure["summary"],
    )
    db.add(deck)
    db.flush()

    for card_data in generated_cards:
        db.add(
            Flashcard(
                deck_id=deck.id,
                question=card_data["question"],
                answer=card_data["answer"],
                concept=card_data.get("concept", ""),
                difficulty=card_data.get("difficulty", "medium"),
            )
        )

    db.commit()
    db.refresh(deck)
    return serialize_deck(deck)


@app.post("/api/cards/{card_id}/review", response_model=FlashcardRead)
def review_card(card_id: int, payload: ReviewRequest, db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    event = apply_review(card, payload.result)
    card.reviews.append(event)
    db.add(card)
    db.commit()
    db.refresh(card)
    return FlashcardRead.model_validate(card)


@app.post("/api/cards/{card_id}/explain", response_model=ExplanationResponse)
def explain_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    if not card.explanation_cache:
        try:
            card.explanation_cache = explain_flashcard(card.question, card.answer)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Explanation failed: {exc}") from exc
        db.add(card)
        db.commit()
        db.refresh(card)

    return ExplanationResponse(explanation=card.explanation_cache)


@app.post("/api/cards/{card_id}/regenerate", response_model=RegenerateResponse)
def regenerate_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    try:
        improved = regenerate_flashcard(card.question, card.answer, card.concept)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Regeneration failed: {exc}") from exc

    card.question = improved["question"]
    card.answer = improved["answer"]
    card.concept = improved.get("concept", card.concept)
    card.difficulty = improved.get("difficulty", card.difficulty)
    card.explanation_cache = None
    db.add(card)
    db.commit()
    db.refresh(card)
    return RegenerateResponse(card=FlashcardRead.model_validate(card))

