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

## Faza 4: Silnik HITL i Przechowywanie

- [ ] `src/services/approval_queue.py` — warstwa przechowywania akcji
      oczekujących (start: in-memory, docelowo SQLite)
- [ ] Operacje: `create_pending`, `list_pending`, `approve`, `reject`
- [ ] Log audytowy decyzji (kto/kiedy/co zatwierdził lub odrzucił)
- [ ] Testy jednostkowe kolejki zatwierdzeń

## Faza 5: API REST w FastAPI

- [ ] `src/api/main.py` — inicjalizacja aplikacji FastAPI
- [ ] `POST /documents/upload` — przyjęcie pliku (PDF/e-mail) i uruchomienie ekstrakcji
- [ ] `GET /approvals/pending` — lista akcji oczekujących na zatwierdzenie
- [ ] `POST /approvals/{id}/decision` — decyzja Approve / Reject
- [ ] `GET /health` — healthcheck
- [ ] Testy integracyjne endpointów (FastAPI `TestClient`)

## Faza 6: Konteneryzacja, Testy E2E i finalna dokumentacja

- [ ] `Dockerfile` (+ opcjonalnie `docker-compose.yml`)
- [ ] Testy end-to-end: upload → pending → approve → efekt akcji
- [ ] CI: GitHub Actions (lint + pytest na każdy push/PR)
- [ ] Finalizacja `README.md` pod CV (zrzuty ekranu / GIF, wyniki, ograniczenia)
- [ ] Tag wersji / release
