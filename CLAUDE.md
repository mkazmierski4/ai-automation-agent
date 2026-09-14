# CLAUDE.md

Wytyczne dla pracy nad projektem **Human-in-the-Loop AI Document & Task Processor**.

## Cel projektu

Automatyzacja przetwarzania dokumentów biznesowych (PDF, e-mail) przy użyciu LLM
ze structured outputs (Pydantic / JSON Schema), gdzie **każda zaproponowana akcja
wymaga zatwierdzenia przez człowieka** przed wykonaniem. Projekt portfolio pod
rekrutację AI Engineer / Automation Engineer.

## Stack technologiczny

- **Python 3.11+**
- **FastAPI** — warstwa API
- **Pydantic v2** — walidacja danych i structured outputs z LLM
- **Uvicorn** — serwer ASGI
- **pytest** — testy
- LLM providerzy: OpenAI i/lub Anthropic (konfigurowalne przez `.env`)

## Zasady kodowania

- Zgodność z **PEP 8**, formatowanie i lint przez `black` + `ruff`.
- Type hints wszędzie (`from __future__ import annotations` gdy potrzebne).
- Krótkie, jednoznaczne docstringi (Google style) dla publicznych funkcji/klas.
- Moduły trzymamy małe i jednoodpowiedzialne (single responsibility).
- Żadna logika nie wykonuje akcji zewnętrznej (wysyłka maila, zapis do systemu,
  itp.) bez przejścia przez warstwę zatwierdzenia (Human-in-the-Loop gate).
- Sekrety wyłącznie przez zmienne środowiskowe (`.env`, nigdy hardcodowane).
- Commity w konwencji [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).

## Struktura katalogów

```
projekt-ai-automatyzacja/
├── src/
│   ├── api/        # Routery FastAPI (endpointy HTTP)
│   ├── core/       # Konfiguracja, logowanie, wyjątki, ustawienia
│   ├── models/     # Schematy Pydantic (structured outputs, DTO)
│   └── services/   # Logika biznesowa (ekstrakcja LLM, kolejka HITL, integracje)
├── tests/          # Testy pytest (lustro struktury src/)
├── .env.example    # Wzorzec zmiennych środowiskowych
├── requirements.txt
└── README.md
```

## Komendy uruchomieniowe

```bash
# Instalacja zależności
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Uruchomienie API (dev)
uvicorn src.api.main:app --reload

# Testy
pytest

# Lint / format
ruff check .
black .
```

## Sposób pracy w tym repo

- Pracujemy iteracyjnie, krok po kroku — bez generowania dużych partii kodu naraz.
- Przed modyfikacją plików edytujemy tylko niezbędne sekcje.
- Każdy krok kończy się commitem opisującym zakres zmiany.
