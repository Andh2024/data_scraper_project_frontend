from flask import Flask, render_template, request, redirect, url_for, session
from pathlib import Path
import csv

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"  # ⚠️ für Produktion ändern

# ===== CSV-Konfiguration (separat) =====
CSV_PATH = Path("data_bootstrap.csv")
CSV_FIELDS = ["Produkt", "Preis", "Region"]


def ensure_csv_with_header():
    """Erstellt CSV mit Header, falls sie fehlt oder leer ist."""
    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()


def append_row(produkt_url: str, preis: str, region: str):
    """Hängt eine neue Zeile an die CSV an."""
    ensure_csv_with_header()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(
            {
                "Produkt": (produkt_url or "").strip(),
                "Preis": str(preis or "").strip(),
                "Region": (region or "").strip(),
            }
        )


def load_rows_for_table():
    """Liest CSV und liefert Zeilen im Format für die Tabelle (zeile.*)."""
    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        return []
    rows = []
    with CSV_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            produkt_url = (r.get("Produkt") or "").strip()
            preis = (r.get("Preis") or "").strip()
            region = (r.get("Region") or "").strip()
            rows.append(
                {
                    "produkt": produkt_url,
                    "preis": preis,
                    "region": region,
                    "link": produkt_url,
                }
            )
    return rows


# ============== ROUTES ==============


# / und /bootstrap zeigen beide die Startseite
@app.route("/")
@app.route("/bootstrap")
def home_bootstrap():
    return render_template("index_bootstrap.html", active_page="home")


@app.route("/submit", methods=["POST"])
def submit_bootstrap():
    """Form empfangen → CSV schreiben → neuen Eintrag einmalig zeigen (PRG)."""
    produkt = request.form.get("produkt", "")
    preis = request.form.get("preis", "")
    region = request.form.get("region", "")

    if not produkt or not preis or not region:
        return render_template(
            "index_bootstrap.html",
            message="Bitte alle Felder ausfüllen.",
            success=False,
            active_page="home",
        )

    append_row(produkt, preis, region)

    # neuen Eintrag in Session parken → wird auf /neueste einmalig angezeigt
    session["new_row"] = {
        "produkt": produkt,
        "preis": preis,
        "region": region,
        "link": produkt,
    }
    return redirect(url_for("neueste_bootstrap"))


@app.route("/neueste")
def neueste_bootstrap():
    """Zeigt nur den zuletzt hinzugefügten Eintrag + Erfolgsmeldung."""
    new_row = session.pop("new_row", None)  # nur einmal anzeigen
    if not new_row:
        return redirect(url_for("seite2_bootstrap"))
    return render_template(
        "seite2_bootstrap.html",
        daten=[new_row],
        message="1 neuer Eintrag wurde gespeichert.",
        success=True,
        show_all_link=True,
        active_page="results",
    )


@app.route("/seite2_bootstrap")
def seite2_bootstrap():
    """Alle gespeicherten Einträge anzeigen."""
    daten = load_rows_for_table()
    return render_template("seite2_bootstrap.html", daten=daten, active_page="results")


@app.route("/suchresultat_bootstrap")
def suchresultat_bootstrap():
    """Alternative Ergebnis-Seite (optional, gleiche Daten)."""
    daten = load_rows_for_table()
    return render_template(
        "suchresultat_bootstrap.html", daten=daten, active_page="results"
    )


if __name__ == "__main__":
    # bei Parallelbetrieb mit anderer App optional: port=5001 setzen
    # app.run(debug=True, port=5001)
    app.run(debug=True)
