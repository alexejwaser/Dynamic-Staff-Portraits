# Dynamic Staff Portraits

Eine Desktop-Anwendung zur effizienten Erstellung von Portraitfotos.

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Starten

```bash
python -m app.main
```

Fotos einer Klasse werden beim Abschluss automatisch zu ZIP-Archiven gebündelt
und ein Hinweis mit Link zum Ordner erscheint. Über das Zahnrad können die
Einstellungen geöffnet werden. Dort lässt sich die Kameraart, die Excel-Spalten
und ein optionales Overlay-Bild (PNG) für die Live-Vorschau konfigurieren. Das
gewählte Overlay wird gespeichert und beim nächsten Start automatisch geladen.
Die Live-Vorschau skaliert automatisch zum Kamerabild, das Overlay passt sich
dabei an. Unter Windows wird standardmässig die zweite erkannte Webcam
via OpenCV verwendet.
Ist `gphoto2` vorhanden, kann alternativ eine DSLR genutzt werden. Fuer
hoechste Qualitaet laesst sich unter Windows die Canon-EDSDK Anbindung ueber die
Einstellung **Canon SDK** aktivieren; sonst startet ein Simulator.

## Tests

```bash
pytest
```
