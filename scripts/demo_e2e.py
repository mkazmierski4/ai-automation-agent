"""Skrypt weryfikacyjny end-to-end dla pełnego przepływu Human-in-the-Loop.

Uruchamiany przeciwko działającej instancji API (domyślnie
``http://localhost:8000``). Wykonuje ekstrakcję z przykładowej faktury,
odczytuje stan kolejki zatwierdzeń, zatwierdza wniosek i weryfikuje
status końcowy.

Wymaga poprawnie skonfigurowanego klucza API dostawcy LLM (`.env`), ponieważ
etap ekstrakcji wykonuje realne wywołanie modelu.

Użycie:
    python scripts/demo_e2e.py [base_url]
"""

from __future__ import annotations

import sys

import httpx

DEFAULT_BASE_URL = "http://localhost:8000"

SAMPLE_INVOICE_TEXT = """
Faktura VAT nr FV/2025/09/042
Sprzedawca: Acme Sp. z o.o.
Data wystawienia: 2025-09-01
Termin płatności: 2025-09-15
Waluta: PLN
Pozycje:
1. Usługa konsultingowa - 1 x 1000.00 PLN = 1000.00 PLN
Suma: 1000.00 PLN
""".strip()


def run(base_url: str) -> int:
    """Wykonuje scenariusz E2E i zwraca kod wyjścia procesu."""
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        health = client.get("/health")
        health.raise_for_status()
        print(f"[1/4] Health check OK: {health.json()}")

        process_response = client.post(
            "/api/v1/documents/process", json={"text": SAMPLE_INVOICE_TEXT}
        )
        process_response.raise_for_status()
        request = process_response.json()
        request_id = request["id"]
        print(
            f"[2/4] Dokument przetworzony (id={request_id}), "
            f"status: {request['status']}"
        )

        if request["status"] != "pending":
            print("Wniosek został auto-zatwierdzony — pomijam krok decyzji.")
            print("\nScenariusz E2E zakończony sukcesem.")
            return 0

        pending = client.get("/api/v1/approvals/pending").json()
        if not any(item["id"] == request_id for item in pending):
            print(f"BŁĄD: wniosek {request_id} nie znajduje się w kolejce PENDING")
            return 1
        print(f"[3/4] Wniosek widoczny w kolejce oczekujących ({len(pending)} pozycji)")

        approve_response = client.post(
            f"/api/v1/approvals/{request_id}/approve",
            json={"reviewer": "demo-e2e", "notes": "Zatwierdzone w scenariuszu E2E"},
        )
        approve_response.raise_for_status()
        approved = approve_response.json()
        if approved["status"] != "approved":
            print(f"BŁĄD: oczekiwano statusu 'approved', otrzymano {approved['status']!r}")
            return 1
        print(f"[4/4] Wniosek zatwierdzony przez '{approved['decided_by']}'")

    print("\nScenariusz E2E zakończony sukcesem.")
    return 0


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL
    sys.exit(run(url))
