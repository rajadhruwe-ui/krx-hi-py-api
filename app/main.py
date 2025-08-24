from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import TranslateRequest, TranslateResponse, BatchTranslateRequest, BatchTranslateResponse
from .translation import Lexicon, simple_tokenize, greedy_phrase_translate, detokenize
import os

LEXICON_PATH = os.getenv("LEXICON_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "lexicon.csv"))

app = FastAPI(title="Kurukh → Hindi Rule-Based MT API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

lex = Lexicon(csv_path=os.path.abspath(LEXICON_PATH))

@app.get("/health")
def health():
    return {"status": "ok", "entries": len(lex.surface2hi), "max_phrase_len": lex.max_phrase_len}

@app.post("/reload")
def reload_lexicon():
    lex.reload()
    return {"status": "reloaded", "entries": len(lex.surface2hi), "max_phrase_len": lex.max_phrase_len}

@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    text = req.text or ""
    tokens = simple_tokenize(text)
    out_tokens, dbg = greedy_phrase_translate(tokens, lex, debug=req.debug or False)
    translated = detokenize(out_tokens)
    return TranslateResponse(translated_text=translated, debug=dbg if req.debug else None)

@app.post("/translate/batch", response_model=BatchTranslateResponse)
def translate_batch(req: BatchTranslateRequest):
    items = []
    for t in req.texts:
        tokens = simple_tokenize(t or "")
        out_tokens, dbg = greedy_phrase_translate(tokens, lex, debug=req.debug or False)
        translated = detokenize(out_tokens)
        items.append({"translated_text": translated, "debug": dbg if req.debug else None})
    return BatchTranslateResponse(items=items)
