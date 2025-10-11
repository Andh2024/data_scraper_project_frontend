from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

CSV_FILE = "data.csv"

# Falls CSV noch nicht existiert: Kopfzeile anlegen
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Produkt", "Produktewahl", "Preis", "Region"])


@app.route("/", methods=["GET", "POST"])
def index():
    message = None  # Standard: keine Meldung

    if request.method == "POST":
        produkt = request.form.get("produkt")
        produktewahl = request.form.get("produktewahl")
        preis = request.form.get("preis")
        region = request.form.get("region")

        # einfache Validierung
        if not produkt or not produktewahl or not preis or not region:
            message = "❌ Bitte alle Felder ausfüllen!"
            return render_template("form.html", message=message, success=False)

        try:
            preis = int(preis)
        except ValueError:
            message = "❌ Preis muss eine ganze Zahl sein!"
            return render_template("form.html", message=message, success=False)

        # Daten in CSV schreiben
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([produkt, produktewahl, preis, region])

        # Erfolgsmeldung
        message = "✅ Daten erfolgreich gespeichert!"
        return render_template("form.html", message=message, success=True)

    return render_template("form.html", message=message, success=None)


if __name__ == "__main__":
    app.run(debug=True)


"""from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")  # lädt /templates/index.html


if __name__ == "__main__":
    app.run(debug=True)  # http://127.0.0.1:5000

"""
