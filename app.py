import csv
import os
from pathlib import Path
from typing import List, Dict, Any

from flask import Flask, render_template, request, redirect, url_for, session

# -----------------------------------------------------------------------------
# Flask-App
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# ===== Input Daten =====

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data.csv"
REGION_COLOR_FILE = BASE_DIR / "region_colors.json"

CSV_FIELDS = ["Produkt", "Preis", "Region", "Link"]

# ===== Output Daten =====

CSV_DATA_PATH = Path("data_output.csv")
CSV_DATA_PATH = BASE_DIR / "data_output.csv"
CSV_DATA_FIELDS = ["Produkt", "Link", "Preis", "Region"]


# -----------------------------------------------------------------------------
# CSV Utilities
# -----------------------------------------------------------------------------
def ensure_csv_with_header() -> None:
    """Erstellt data.csv mit Header, falls sie nicht existiert oder leer ist."""
    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()


def append_row(produkt_url: str, preis: str, region: str) -> None:
    """Hängt eine neue Zeile an die CSV an."""
    ensure_csv_with_header()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(
            {
                "Produkt": (produkt_url or "").strip(),
                "Preis": str(preis or "").strip(),
                "Region": (region or "").strip(),
                # Link = Produkt-URL (gemäss aktueller Datenstruktur)
                "Link": "",
            }
        )


def load_rows_for_table():
    """Liest CSV und liefert Zeilen im Format für die Tabelle (zeile.*)."""
    if not CSV_DATA_PATH.exists() or CSV_DATA_PATH.stat().st_size == 0:
        return []
    rows = []
    with CSV_DATA_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            produkt = (r.get("Produkt") or "").strip()
            preis = (r.get("Preis") or "").strip()
            region = (r.get("Region") or "").strip()
            produkt_url = (r.get("Link") or "").strip()
            rows.append(
                {
                    "produkt": produkt,
                    "preis": preis,
                    "region": region,
                    "link": produkt_url,
                }
            )
    return rows


# =========================


# -----------------------------------------------------------------------------
# Weitere Jinja-Filter
# -----------------------------------------------------------------------------
@app.template_filter("chf")
def chf_filter(value):
    """Formatiert Zahlen als Schweizer Franken, z. B. CHF 9'000."""
    try:
        n = int(float(value))
        formatted = f"{n:,}".replace(",", "'")
        return f"CHF {formatted}"
    except Exception:
        return value


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html", active_page="home")


@app.route("/submit", methods=["POST"])
def submit():
    # Form-Felder (Namen müssen zu deinem index.html passen)
    produkt = request.form.get("produkt", "").strip()
    preis = request.form.get("preis", "").strip()
    region = request.form.get("region", "").strip()

    # in CSV schreiben
    append_row(produkt_url=produkt, preis=preis, region=region)

    # neuen Eintrag für einmalige Anzeige zwischenspeichern
    session["new_row"] = {
        "produkt": produkt,
        "preis": preis,
        "region": region,
        "link": produkt,
    }
    return redirect(url_for("suchresultat_aktuell"))


@app.route("/suchresultat/aktuell")
def suchresultat_aktuell():
    """Zeigt nur den zuletzt gespeicherten Eintrag + Erfolgsmeldung."""
    new_row = session.pop("new_row", None)  # nur einmal anzeigen
    if not new_row:
        return redirect(url_for("suchresultat_total"))
    return render_template(
        "suchresultat_aktuell.html",
        daten=[new_row],
        message="1 neuer Eintrag wurde gespeichert.",
        success=True,
        active_page="results",
    )


@app.route("/suchresultat")
def suchresultat_total():
    """Alle gespeicherten Einträge anzeigen."""
    daten = load_rows_for_table()
    return render_template(
        "suchresultat_total.html",
        daten=daten,
        active_page="results",
    )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
