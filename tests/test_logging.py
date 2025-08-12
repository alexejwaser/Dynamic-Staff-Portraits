"""Tests for the logging setup utility."""

import logging

from app.core.util.logging import setup_logging


def test_setup_logging_creates_log_file(tmp_path):
    logging.getLogger().handlers.clear()
    setup_logging(tmp_path)
    log_file = tmp_path / "app.log"
    logging.getLogger("test").info("hello world")
    logging.shutdown()
    assert log_file.exists()
    assert "hello world" in log_file.read_text()
