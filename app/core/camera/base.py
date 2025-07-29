# app/core/camera/base.py
from abc import ABC, abstractmethod
from pathlib import Path

class CameraError(Exception):
    pass

class BaseCamera(ABC):
    @abstractmethod
    def start_liveview(self):
        pass

    @abstractmethod
    def stop_liveview(self):
        pass

    @abstractmethod
    def capture(self, dest: Path) -> None:
        pass


    @abstractmethod
    def capture_preview(self, dest: Path) -> None:
        """Capture a single preview frame to ``dest``."""
        pass

