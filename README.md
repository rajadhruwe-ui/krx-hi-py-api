# Kurukh → Hindi Rule-Based MT API (CSV-powered)

This is a lightweight **FastAPI** server that performs rule-based, dictionary-first translation
from **Kurukh** to **Hindi**, backed by a simple CSV lexicon. It supports single and batch translation,
phrase matching (greedy longest), and basic text normalization.

## Features
- CSV-powered lexicon with **phrases** and **single-word** entries
- Greedy **longest-phrase** matching (e.g., multiword idioms)
- Basic normalization: lowercasing, punctuation-aware tokenization
- OOV handling: pass-through (keeps unknown tokens)
- Debug mode to inspect tokenization and matches
- Hot reload lexicon via `POST /reload`
- Endpoints:
  - `GET /health`
  - `POST /translate` → `{ "text": "...", "debug": true/false }`
  - `POST /translate/batch` → `{ "texts": ["...", "..."], "debug": true/false }`
  - `POST /reload`

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000/docs for the interactive Swagger UI.

## CSV format

Place your lexicon in `data/lexicon.csv`. Sample columns:

```csv
kurukh,hindi,pos,notes
namaskar,नमस्कार,INTJ,greeting
dhanyabad,धन्यवाद,INTJ,thank you
apa,मैं,PRON,1st person singular
apaen,हम,PRON,1st person plural
tum,तुम,PRON,2nd person
buro,अच्छा,ADJ,good
buru,बुरा,ADJ,bad
jal,पानी,NOUN,water
school jabu,स्कूल जाऊँगा,PHRASE,go to school (1sg fut)
biya laga,शादी करना,PHRASE,marry/do marriage
```

Notes:
- **Phrases** are supported: just write spaces in the `kurukh` column (e.g., `school jabu`).
- Extra columns are optional; only the first (`kurukh`) and second (`hindi`) are used by the engine.
- Rows with empty `kurukh` or `hindi` are ignored.

## Extending rules
This starter focuses on lexicon + phrase matching. You can add rule hooks inside `app/translation.py`
(e.g., suffix stripping, agreement, reordering), guided by your linguistic needs.

## Docker (optional)

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY data ./data
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build & run:
```bash
docker build -t kurukh-hindi-rbmt .
docker run -p 8000:8000 kurukh-hindi-rbmt
```
