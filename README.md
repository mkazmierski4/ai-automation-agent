# Human-in-the-Loop AI Document & Task Processor

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11x-009688?logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-e92063?logo=pydantic&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Usługa do automatyzacji przetwarzania dokumentów biznesowych (faktury,
korespondencja e-mail) z wykorzystaniem modeli językowych (LLM) wymuszających
ustrukturyzowany format wyjścia (Pydantic Structured Outputs / JSON Schema).
Każda akcja zaproponowana przez model przechodzi przez obowiązkową bramkę
zatwierdzenia przez człowieka (Human-in-the-Loop) przed wykonaniem.

## Problem biznesowy

Pełna automatyzacja przetwarzania dokumentów za pomocą LLM jest szybka, ale
niesie ryzyko operacyjne — błąd ekstrakcji może wygenerować nieprawidłową
akcję (błędną kwotę do zapłaty, złą kategorię zgłoszenia, nieprawidłowego
odbiorcę). System implementuje wzorzec **AI-assisted, human-approved
automation**, łączący przepustowość modelu z kontrolą operatora:

- **Ekstrakcja danych** — dokument jest analizowany i przekształcany w
  ustrukturyzowane dane (structured output) gotowe do dalszego przetwarzania.
- **Kontrola ryzyka** — żadna akcja (zaksięgowanie, odpowiedź, eskalacja) nie
  wykonuje się automatycznie bez przekroczenia zdefiniowanego progu ufności
  lub jawnej decyzji operatora.
- **Audytowalność** — każda decyzja, systemowa i ludzka, jest rejestrowana z
  pełnym kontekstem (kto, kiedy, jaki był powód), co wspiera zgodność
  (compliance) i możliwość późniejszej analizy.

## Architektura systemu

```mermaid
flowchart TD
    A[Dokument wejściowy<br/>PDF / e-mail] --> B[API: POST /documents/process]
    B --> C[LLM Client<br/>OpenAI / Anthropic]
    C --> D[Walidacja Pydantic<br/>JSON Schema]
    D --> E{Approval Queue<br/>próg confidence}
    E -->|confidence ≥ próg| F[AUTO_APPROVED]
    E -->|confidence < próg| G[PENDING<br/>oczekuje na operatora]
    G -->|POST /approvals/{id}/approve| H[APPROVED]
    G -->|POST /approvals/{id}/reject| I[REJECTED]
    F --> J[Log audytowy]
    H --> J
    I --> J
```

**Warstwy systemu:**

| Warstwa | Odpowiedzialność |
|---|---|
| `src/api` | Aplikacja FastAPI, routery REST, walidacja żądań, obsługa błędów |
| `src/core` | Konfiguracja środowiskowa (pydantic-settings), ustawienia współdzielone |
| `src/models` | Schematy domenowe (structured outputs, kolejka zatwierdzeń) i DTO API |
| `src/services` | Klient LLM (abstrakcja nad dostawcami), parser dokumentów, silnik kolejki HITL |

Storage kolejki zatwierdzeń jest wstrzykiwany przez interfejs
(`BaseApprovalStorage`) — domyślna implementacja in-memory może być podmieniona
na SQLite/PostgreSQL bez zmian w logice domenowej.

## Specyfikacja API

Interaktywna dokumentacja OpenAPI: `/docs` (Swagger UI) i `/redoc` po
uruchomieniu serwera.

| Metoda | Endpoint | Opis |
|---|---|---|
| `GET` | `/health` | Status aplikacji i aktywne środowisko |
| `POST` | `/api/v1/documents/process` | Ekstrakcja danych z tekstu dokumentu i utworzenie wpisu w kolejce zatwierdzeń |
| `GET` | `/api/v1/approvals/pending` | Lista wniosków oczekujących na decyzję operatora |
| `POST` | `/api/v1/approvals/{request_id}/approve` | Zatwierdzenie wniosku (`reviewer`, opcjonalnie `notes`) |
| `POST` | `/api/v1/approvals/{request_id}/reject` | Odrzucenie wniosku (`reviewer`, `reason`) |

## Konfiguracja

Zmienne środowiskowe (pełny wzorzec w [.env.example](.env.example)):

| Zmienna | Opis | Domyślnie |
|---|---|---|
| `LLM_PROVIDER` | Aktywny dostawca LLM: `openai` lub `anthropic` | `anthropic` |
| `OPENAI_API_KEY` / `OPENAI_MODEL` | Konfiguracja dostawcy OpenAI | — |
| `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL` | Konfiguracja dostawcy Anthropic | — |
| `HITL_AUTO_APPROVE_THRESHOLD` | Próg confidence, od którego wniosek jest auto-zatwierdzany | `0.9` |
| `HITL_APPROVAL_TIMEOUT_SECONDS` | Maksymalny czas oczekiwania na decyzję operatora | `3600` |
| `APP_ENV` / `LOG_LEVEL` | Środowisko i poziom logowania | `development` / `INFO` |

## Uruchomienie lokalne

```bash
git clone <repository-url>
cd projekt-ai-automatyzacja

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt

cp .env.example .env
# uzupełnij klucz API wybranego dostawcy LLM

uvicorn src.api.main:app --reload
```

## Wdrożenie kontenerowe

```bash
cp .env.example .env
docker compose up --build
```

Obraz produkcyjny (`Dockerfile`) jest budowany wieloetapowo (multi-stage) na
bazie `python:3.11-slim`, uruchamia aplikację jako użytkownik nieprzywilejowany
(non-root) i eksponuje healthcheck na `/health`. Obraz jest kompatybilny z
wdrożeniem w klastrze Kubernetes (jeden proces, konfiguracja przez zmienne
środowiskowe, healthcheck HTTP).

## Testy

```bash
pytest              # testy jednostkowe i integracyjne
ruff check .         # analiza statyczna
python scripts/demo_e2e.py   # weryfikacja end-to-end na żywym serwerze
```

`scripts/demo_e2e.py` wykonuje pełny scenariusz na działającej instancji API:
przesyła przykładową fakturę, odczytuje stan kolejki zatwierdzeń, zatwierdza
wniosek i weryfikuje status końcowy.

## Integracja ciągła

Każdy push do `main` oraz każdy pull request uruchamia pipeline CI
([.github/workflows/ci.yml](.github/workflows/ci.yml)): instalację zależności,
lint (`ruff`) oraz pełny zestaw testów.

## Struktura projektu

```
src/
├── api/        # Aplikacja FastAPI, routery v1, dependency injection
├── core/       # Konfiguracja (pydantic-settings)
├── models/     # Schematy domenowe i DTO API
└── services/   # Klient LLM, parser dokumentów, kolejka HITL
tests/          # Testy pytest
scripts/        # Skrypty weryfikacyjne (E2E)
```

Zasady architektoniczne i konwencje kodowania: [CLAUDE.md](CLAUDE.md).
Plan realizacji i status poszczególnych etapów: [ROADMAP.md](ROADMAP.md).

## Stack technologiczny

FastAPI · Pydantic v2 · Uvicorn · OpenAI API / Anthropic API · Docker ·
GitHub Actions · pytest · ruff

## Licencja

MIT
