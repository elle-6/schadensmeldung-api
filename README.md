# 🏗️ Schadensmeldung API - Mit Live-Karte

Eine **lokale Demo-Anwendung** zur Erfassung von Infrastrukturschäden mit Echtzeit-Kartenansicht. 
**Hinweis: Diese App ist für den lokalen Betrieb konzipiert und läuft auf deinem eigenen Computer.**

![Schadensmeldung Screenshot](https://via.placeholder.com/800x400/3498db/ffffff?text=Schadensmeldung+Demo+App)

## ⚠️ Wichtiger Hinweis

**Diese Anwendung ist eine Demo-Version und läuft ausschliesslich lokal auf deinem Computer.** 
Sie verwendet eine Mock-Datenbank im Arbeitsspeicher und ist nicht für Production-Einsatz vorgesehen.

## ✨ Features

### 🌐 Web Interface
- **Live-Karte** mit OpenStreetMap Integration
- **Echtzeit-Schadensanzeige** als farbige Marker
- **Intuitive Formulare** für Schadensmeldungen
- **Responsive Design** für alle Geräte
- **Koordinaten-Validierung** für Schweizer Gebiet

### 🔧 Technische Features
- **Flask Backend** mit Python
- **Mock-Datenbank** (In-Memory)
- **API-Key Authentifizierung** (Demo-Keys)
- **Vollständig lokal** - keine Internetverbindung nötig (ausser für Karten)

## 🚀 Lokale Installation & Start

### Voraussetzungen
- Python 3.9 oder höher
- pip (Python Package Manager)

### Schnellstart (3 Minuten)

1. **Repository klonen**
```bash
git clone https://github.com/dein-username/schadensmeldung-api.git
cd schadensmeldung-api



# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate


pip install -r requirements.txt


python app.py


http://localhost:5000



🎯 Verwendung der Demo

Web Interface nutzen

Karte verwenden: Klicke auf die Karte um Koordinaten automatisch zu setzen
Schaden melden:

Schadenstyp auswählen
Beschreibung eingeben
Optional: Foto hinzufügen
Absenden
Schäden anzeigen: Alle gemeldeten Schäden erscheinen live auf der Karte
Demo-Features testen

✅ Neue Schäden melden (werden im Memory gespeichert)
✅ Live-Karte mit OpenStreetMap
✅ Koordinaten-Validierung (nur Schweizer Koordinaten)
✅ Responsive Design (funktioniert auf Mobile)
⚠️ Daten gehen verloren bei Server-Neustart
