# CLAUDE.md

Wewnętrzny podręcznik inżynieryjny projektu **Human-in-the-Loop AI Document &
Task Processor** — zasady architektoniczne, konwencje kodowania i workflow
deweloperski obowiązujące w tym repozytorium.

## Zakres systemu

Usługa automatyzuje przetwarzanie dokumentów biznesowych (faktury,
korespondencja e-mail) przy użyciu modeli językowych wymuszających
ustrukturyzowany format wyjścia (Pydantic Structured Outputs / JSON Schema).
Warstwa Human-in-the-Loop gwarantuje, że **żadna akcja zaproponowana przez
model nie jest wykonywana bez jawnego zatwierdzenia przez uprawnionego
operatora**.

## Stack technologiczny

- **Python 3.11+**
- **FastAPI** — warstwa API
- **Pydantic v2** — walidacja danych i structured outputs
- **Uvicorn** — serwer ASGI
- **pytest** — testy jednostkowe i integracyjne
- **ruff** — statyczna analiza kodu (lint)
- **Docker / docker-compose** — konteneryzacja i uruchomienie środowiskowe
- Dostawcy LLM: OpenAI i Anthropic, konfigurowalni przez zmienną `LLM_PROVIDER`

## Zasady kodowania

- Zgodność z **PEP 8**; lint egzekwowany przez `ruff` (konfiguracja w
  `pyproject.toml`), obowiązkowo zielony w CI.
- Type hints wszędzie (`from __future__ import annotations` w każdym module).
- Docstringi (Google style) dla wszystkich publicznych klas i funkcji.
- Moduły utrzymywane w zasadzie pojedynczej odpowiedzialności (SRP).
- Żadna logika nie wykonuje akcji zewnętrznej (zapis, powiadomienie,
  integracja) bez przejścia przez bramkę zatwierdzenia (Human-in-the-Loop).
- Storage jest wstrzykiwany przez interfejs (`BaseApprovalStorage`) — brak
  twardego powiązania logiki domenowej z konkretną implementacją bazy danych.
- Sekrety wyłącznie przez zmienne środowiskowe (`.env`); nigdy w repozytorium.
- Commity w konwencji [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).

## Struktura katalogów

```
.
├── src/
│   ├── api/          # Warstwa HTTP: aplikacja FastAPI, routery v1, DI
│   ├── core/         # Konfiguracja (pydantic-settings), logowanie, wyjątki
│   ├── models/       # Schematy domenowe (Pydantic) i DTO API
│   └── services/     # Logika biznesowa: klient LLM, parser, kolejka HITL
├── tests/            # Testy pytest (jednostkowe + integracyjne)
├── scripts/          # Skrypty pomocnicze (np. weryfikacja E2E)
├── .github/workflows/ # Definicje CI (GitHub Actions)
├── Dockerfile         # Obraz produkcyjny (multi-stage)
├── docker-compose.yml # Uruchomienie lokalne/serwerowe jedną komendą
└── pyproject.toml     # Konfiguracja narzędzi (ruff)
```

## Komendy uruchomieniowe

```bash
# Instalacja zależności (środowisko lokalne)
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Serwer deweloperski
uvicorn src.api.main:app --reload

# Testy jednostkowe i integracyjne
pytest

# Lint
ruff check .

# Konteneryzacja
docker compose up --build

# Weryfikacja end-to-end (wymaga działającego serwera i skonfigurowanego .env)
python scripts/demo_e2e.py
```

## Workflow deweloperski

- Zmiany wprowadzane iteracyjnie, w izolowanych, atomowych commitach.
- Modyfikacje ograniczone do sekcji kodu bezpośrednio dotyczących zadania —
  brak przypadkowych refaktoryzacji poza zakresem zmiany.
- Każdy push do `main` oraz każdy pull request uruchamia CI (lint + pełny
  zestaw testów); scalanie zmian bez przechodzącego CI jest niedozwolone.
- Rozszerzenia architektoniczne (np. nowy storage, nowy dostawca LLM)
  realizowane przez dodanie implementacji istniejącego interfejsu, bez
  modyfikacji logiki konsumującej ten interfejs.
