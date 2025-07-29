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

Fotos einer Klasse werden beim Abschluss automatisch zu ZIP-Archiven gebündelt.
Für echte Kameras wird `gphoto2` verwendet, andernfalls startet ein Simulator.

## Tests

```bash
pytest
```
