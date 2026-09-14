# Human-in-the-Loop AI Document & Task Processor

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11x-009688?logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-e92063?logo=pydantic&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Automatyzacja przetwarzania dokumentów biznesowych (PDF / e-mail) za pomocą LLM
ze **structured outputs** (Pydantic / JSON Schema), z obowiązkową bramką
**zatwierdzenia przez człowieka (Human-in-the-Loop)** przed wykonaniem
jakiejkolwiek akcji.

## 💼 Business Value

Firmy automatyzujące obieg dokumentów (faktury, zgłoszenia, e-maile klientów)
stają przed dylematem: pełna automatyzacja LLM jest szybka, ale ryzykowna —
błąd modelu może wygenerować nieprawidłową akcję (np. błędną kwotę do zapłaty,
złą kategorię zgłoszenia). Ten projekt pokazuje wzorzec **AI-assisted, human-
approved automation**:

- **Szybkość LLM** — dokument jest automatycznie analizowany i zamieniany na
  ustrukturyzowane dane (Pydantic Structured Outputs), gotowe do dalszego
  przetwarzania.
- **Bezpieczeństwo procesu** — żadna akcja (np. zaksięgowanie, odpowiedź,
  eskalacja) nie wykonuje się automatycznie. Człowiek widzi propozycję modelu
  i ją zatwierdza, edytuje lub odrzuca.
- **Audytowalność** — każda decyzja (modelu i człowieka) jest rejestrowana,
  co ułatwia zgodność (compliance) i debugowanie.

Efekt: redukcja czasu ręcznego przetwarzania dokumentów przy zachowaniu pełnej
kontroli i odpowiedzialności po stronie człowieka.

## 🔄 Przepływ danych (Data Flow & Human Verification)

```mermaid
flowchart TD
    A[Dokument wejściowy<br/>PDF / E-mail] --> B[Serwis ekstrakcji<br/>FastAPI endpoint]
    B --> C[LLM: OpenAI / Anthropic<br/>Structured Output]
    C --> D[Walidacja Pydantic<br/>JSON Schema]
    D --> E{Kolejka zatwierdzeń<br/>Human-in-the-Loop}
    E -->|Zatwierdzone| F[Wykonanie akcji<br/>np. zapis, powiadomienie]
    E -->|Odrzucone / edycja| G[Powrót do korekty<br/>lub odrzucenie]
    F --> H[Log audytowy]
    G --> H
```

## 🚀 Quick Start

```bash
# 1. Klonowanie repozytorium
git clone https://github.com/<twoj-user>/projekt-ai-automatyzacja.git
cd projekt-ai-automatyzacja

# 2. Środowisko wirtualne
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

# 3. Instalacja zależności
pip install -r requirements.txt

# 4. Konfiguracja zmiennych środowiskowych
cp .env.example .env
# uzupełnij klucze API (OpenAI i/lub Anthropic)

# 5. Uruchomienie serwera deweloperskiego
uvicorn src.api.main:app --reload

# 6. Testy
pytest
```

## 🗂️ Struktura projektu

```
src/
├── api/        # Endpointy FastAPI
├── core/       # Konfiguracja, logowanie, wyjątki
├── models/     # Schematy Pydantic (structured outputs)
└── services/   # Logika biznesowa (ekstrakcja, kolejka HITL)
tests/          # Testy pytest
```

Szczegółowe zasady pracy i konwencje kodowania: zobacz [CLAUDE.md](CLAUDE.md).

## 🛠️ Stack

FastAPI · Pydantic v2 · Uvicorn · OpenAI API / Anthropic API · pytest

## 📄 Licencja

MIT
