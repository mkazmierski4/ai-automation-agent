# Roadmapa projektu

**Human-in-the-Loop AI Document & Task Processor** — plan realizacji w 6 fazach.
Każda faza jest niezależnym, możliwym do zaliczenia etapem; checkboxy `[x]`
oznaczają ukończone taski.

---

## Faza 1: Architektura i Dokumentacja ✅

- [x] `CLAUDE.md` — zasady projektu, stack, konwencje kodowania
- [x] `README.md` — badge'e, sekcja Business Value, diagram Mermaid, Quick Start
- [x] `.env.example`, `.gitignore`, `requirements.txt`
- [x] Struktura katalogów `src/` (`api/`, `core/`, `models/`, `services/`) i `tests/`

## Faza 2: Konfiguracja i Modele Pydantic v2 ✅

- [x] Dodanie `pydantic-settings` do `requirements.txt`
- [x] `src/core/config.py` — klasa `Settings` (`BaseSettings`) ładująca `.env`
      (provider LLM, klucze API, timeout HITL)
- [x] `src/models/document.py` — `DocumentType`, `InvoiceLineItem`, `InvoiceData`,
      `ExtractedDocument` (structured output ekstrakcji dokumentu)
- [x] `src/models/document.py` — `ApprovalStatus`, `ApprovalRequest`
      (schemat akcji oczekującej na decyzję człowieka)
- [x] `tests/test_models.py` — walidacja poprawnych i niepoprawnych danych
- [x] `tests/test_config.py` — test wczytywania ustawień
- [x] `pytest` przechodzi bez błędów (9/9)

## Faza 3: Integracja z LLM (Service Parser) ✅

- [x] `src/services/llm_client.py` — abstrakcja nad OpenAI / Anthropic,
      wybór providera na podstawie `LLM_PROVIDER`
- [x] Wymuszenie structured output (JSON Schema generowany z modeli Pydantic)
- [x] `src/services/document_parser.py` — pipeline: dokument → tekst → LLM →
      `ExtractedDocument`
- [x] Obsługa błędów walidacji i retry przy niezgodnej odpowiedzi modelu
- [x] Testy z mockiem klienta LLM (bez realnych wywołań API) — 8 nowych testów

## Faza 4: Silnik HITL i Przechowywanie ✅

- [x] `src/services/approval_queue.py` — `BaseApprovalStorage` (DI) +
      `InMemoryApprovalStorage`, docelowo podmienialna na SQLite/Postgres
- [x] Operacje: `process_extraction` (z auto-approve wg progu confidence),
      `list_pending`, `get_request`, `approve`, `reject`
- [x] Log audytowy decyzji (`decided_at`, `decided_by`, `decision_notes`)
- [x] Testy jednostkowe kolejki zatwierdzeń — 8 nowych testów

## Faza 5: API REST w FastAPI ✅

- [x] `src/api/main.py` — inicjalizacja FastAPI (tytuł/opis/wersja pod `/docs`),
      CORS middleware, exception handlery (`ApprovalRequestNotFoundError` → 404,
      `InvalidApprovalStateError` → 409)
- [x] `POST /api/v1/documents/process` — przyjęcie tekstu i uruchomienie
      pipeline'u `DocumentParser` → `ApprovalQueueService`
- [x] `GET /api/v1/approvals/pending` — lista akcji oczekujących na zatwierdzenie
- [x] `POST /api/v1/approvals/{id}/approve` i `/reject` — decyzje z metadanymi recenzenta
- [x] `GET /health` — healthcheck (status + środowisko)
- [x] Testy integracyjne endpointów (FastAPI `TestClient`) — 8 nowych testów,
      pełny przepływ upload → pending → approve/reject

## Faza 6: Konteneryzacja, CI/CD i szlif produkcyjny ✅

- [x] `Dockerfile` (multi-stage, `python:3.11-slim`, non-root user, healthcheck)
      i `docker-compose.yml` do uruchomienia jedną komendą
- [x] Skrypt end-to-end (`scripts/demo_e2e.py`): upload → pending → approve →
      weryfikacja statusu końcowego na żywym API
- [x] CI: GitHub Actions (`ruff check` + `pytest` na każdy push/PR do `main`)
- [x] Finalizacja `README.md` i `CLAUDE.md` w formie dokumentacji produktowej
      (architektura, specyfikacja API, konfiguracja, wdrożenie kontenerowe)
