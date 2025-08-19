# Identity Card Photo Creator

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)

Eine Desktop-Anwendung zur schnellen Erstellung von Portraitfotos für Klassen und Gruppen.

## Inhaltsverzeichnis
- [🚀 Features](#-features)
- [📦 Installation](#-installation)
- [▶️ Nutzung](#-nutzung)
- [⌨️ Tastenkürzel](#-tastenkürzel)
- [🧪 Tests](#-tests)
- [🖥️ Windows-EXE aus GitHub Actions](#-windows-exe-aus-github-actions)
- [📄 Lizenz](#-lizenz)

## 🚀 Features
- 📁 Automatische Bündelung der Fotos zu ZIP-Archiven pro Klasse
- ⚙️ Individuell konfigurierbare Kamera, Excel-Spalten und Overlay-Bild
- 🖼️ Live-Vorschau mit skalierbarem PNG-Overlay
- 🔍 Schnelle Klassensuche direkt in der Oberfläche
- 📷 Unterstützung für DSLR-Kameras via `gphoto2` oder Canon EDSDK

## 📦 Installation
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

## ▶️ Nutzung
```bash
python -m app.main
```

Beim Abschluss werden alle Fotos einer Klasse automatisch zu einem ZIP-Archiv zusammengefasst und der Zielordner geöffnet.

## ⌨️ Tastenkürzel
- ␠ **Leertaste** – Foto aufnehmen bzw. im Review-Dialog übernehmen
- ⎋ **Esc** – Aufnahme verwerfen und erneut fotografieren
- 🔁 **S** – Lernende überspringen
- ✅ **F** – Klasse abschließen
- ➕ **A** – Person hinzufügen
- 🔄 **C** – Kamera wechseln

## 🧪 Tests
```bash
pytest
```

## 🖥️ Windows-EXE aus GitHub Actions
Ein GitHub-Workflow baut automatisch eine Windows-Exe, sobald ein neuer Branch im entfernten Repository angelegt wird.

1. Erstelle lokal einen neuen Branch:
   ```bash
   git checkout -b mein-branch
   git push -u origin mein-branch
   ```
2. Öffne auf GitHub den Tab **Actions** und wähle den Lauf **Build EXE on branch creation**.
3. Unter **Artifacts** kannst du das Archiv **LegicCardCreator** herunterladen. Darin befindet sich die Datei `LegicCardCreator.exe` aus dem `dist/`-Ordner.

Die EXE kann anschließend wie gewohnt auf Windows ausgeführt werden.

## 📄 Lizenz
Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).
