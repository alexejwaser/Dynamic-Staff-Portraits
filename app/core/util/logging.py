# app/core/util/logging.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'app.log'
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5, encoding='utf-8')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        handlers=[handler, logging.StreamHandler()]
    )
