# Dynamic Staff Portraits

Eine Desktop-Anwendung zur effizienten Erstellung von Portraitfotos.

## Installation Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Installation MacOS

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Starten

```bash
python -m app.main
```

Fotos einer Klasse werden beim Abschluss automatisch zu ZIP-Archiven gebündelt
und ein Hinweis mit Link zum Ordner erscheint. Die Live-Vorschau zeigt ein
Overlay mit Drittellinien. Ein Zahnrad-Button öffnet die Einstellungen, in
denen sich die Kameraart und Excel-Spalten konfigurieren lassen.
Unter Windows wird standardmässig die eingebaute Webcam via OpenCV verwendet.
Ist `gphoto2` vorhanden, kann alternativ eine DSLR genutzt werden; sonst startet
ein Simulator.

## Tests

```bash
pytest
```
