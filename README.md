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
und ein Hinweis mit Link zum Ordner erscheint. Die Live-Vorschau zeigt ein
Overlay mit Drittellinien.

Unter Windows wird die eingebaute Webcam via OpenCV verwendet. Wenn `gphoto2`
vorhanden ist, kann alternativ eine DSLR genutzt werden; sonst startet ein
Simulator.

## Tests

```bash
pytest
```
