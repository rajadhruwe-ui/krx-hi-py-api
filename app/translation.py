import csv
import re
from typing import Dict, List, Tuple

TOKEN_RE = re.compile(r"""
    ([\w\u0900-\u097F]+)            # words (latin or Devanagari)
    |([.,!?;:()\[\]{}"'“”‘’—–-])     # punctuation
    |(\s+)                          # whitespace
""", re.VERBOSE)

# Fallback simple tokenizer for environments without regex property support
WORD_RE = re.compile(r"[\w\u0900-\u097F]+", re.UNICODE)
PUNCT_RE = re.compile(r"[.,!?;:()\[\]{}\"'“”‘’—–-]", re.UNICODE)

class Lexicon:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.surface2hi: Dict[str, str] = {}
        self.max_phrase_len = 1
        self.reload()

    def reload(self):
        self.surface2hi.clear()
        self.max_phrase_len = 1
        try:
            with open(self.csv_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    k = (row.get("kurukh") or "").strip().lower()
                    h = (row.get("hindi") or "").strip()
                    if not k or not h:
                        continue
                    # normalize multiple spaces
                    k_norm = " ".join(k.split())
                    self.surface2hi[k_norm] = h
                    tok_len = len(k_norm.split())
                    if tok_len > self.max_phrase_len:
                        self.max_phrase_len = tok_len
        except FileNotFoundError:
            # allow empty lexicon initially
            pass

    def lookup(self, surface: str) -> str | None:
        return self.surface2hi.get(surface.lower())

def simple_tokenize(text: str) -> List[str]:
    # Robust tokenization without unicode properties (keep words & punctuation separate)
    tokens: List[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if PUNCT_RE.match(ch):
            tokens.append(ch)
            i += 1
        elif ch.isspace():
            # collapse any run of whitespace into a single space token
            while i < len(text) and text[i].isspace():
                i += 1
            tokens.append(" ")
        else:
            m = WORD_RE.match(text, i)
            if m:
                tokens.append(m.group(0))
                i = m.end()
            else:
                tokens.append(ch)
                i += 1
    return tokens

def detokenize(tokens: List[str]) -> str:
    out = []
    prev = ""
    for t in tokens:
        if t == " ":
            if out and out[-1] != " ":
                out.append(" ")
            prev = t
            continue
        # no space before closing punctuation
        if t in ")]}.,!?;:\"'“”‘’—–-":
            if out and out[-1] == " ":
                out.pop()
        out.append(t)
        prev = t
    # trim leading/trailing spaces
    s = "".join(out).strip()
    s = re.sub(r"\s+", " ", s)
    return s


def greedy_phrase_translate(tokens: List[str], lex: Lexicon, debug: bool=False) -> Tuple[List[str], dict]:
    # Greedy longest match over whitespace-delimited tokens, preserving punctuation tokens
    out: List[str] = []
    words: List[str] = []
    idx_map: List[int] = []  # map word index -> original token index

    # Build word list (treat " " and punctuation as separators)
    for i, t in enumerate(tokens):
        if t == " " or PUNCT_RE.match(t or "") or not t.strip():
            continue
        words.append(t)
        idx_map.append(i)

    i = 0
    matches = []
    while i < len(words):
        matched = False
        # try max -> 1
        for span in range(min(lex.max_phrase_len, len(words)-i), 0, -1):
            surface = " ".join(words[i:i+span]).lower()
            hit = lex.lookup(surface)
            if hit is not None:
                # place translation as a single token at position of first word
                tokens[idx_map[i]] = hit
                # clear tokens of the rest words in the span
                for j in range(1, span):
                    tokens[idx_map[i+j]] = ""  # mark removed
                matches.append({"surface": surface, "hindi": hit, "start_word": i, "len": span})
                i += span
                matched = True
                break
        if not matched:
            i += 1

    # Remove cleared tokens and collapse spaces
    cleaned: List[str] = []
    for t in tokens:
        if t == "" or t is None:
            continue
        # dictionary-hit tokens may contain spaces (phrases). Surround with spaces to keep boundaries
        if " " in t and not PUNCT_RE.match(t[0]):
            if cleaned and cleaned[-1] != " ":
                cleaned.append(" ")
            cleaned.append(t)
            cleaned.append(" ")
        else:
            cleaned.append(t)

    # Final fallbacks: single-word substitutions that were missed (e.g., punctuation-separated words)
    final_tokens: List[str] = []
    for t in cleaned:
        if t == " " or PUNCT_RE.match(t or "") or not t.strip():
            final_tokens.append(t)
            continue
        alt = lex.lookup(t)
        final_tokens.append(alt if alt is not None else t)

    debug_info = {"matches": matches} if debug else {}
    return final_tokens, debug_info
