from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from binaryninjaui import (
    SidebarContextSensitivity,
    SidebarWidget,
    SidebarWidgetLocation,
    SidebarWidgetType,
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
)


SIDEBAR_TITLE = "Sludge Content"
PLUGIN_DIR = Path(__file__).resolve().parent
MEDIA_DIR = PLUGIN_DIR / "media"
DEFAULT_FRAME_INTERVAL_MS = 33


def build_sidebar_icon() -> QImage:
    icon = QImage(56, 56, QImage.Format_ARGB32)
    icon.fill(QColor("#111827"))

    painter = QPainter(icon)
    painter.setRenderHint(QPainter.Antialiasing, True)

    painter.fillRect(0, 0, 56, 18, QColor("#f97316"))
    painter.fillRect(0, 18, 56, 38, QColor("#0f172a"))

    pen = QPen(QColor("#e5e7eb"))
    pen.setWidth(3)
    painter.setPen(pen)
    painter.drawLine(14, 8, 14, 48)
    painter.drawLine(28, 8, 28, 48)
    painter.drawLine(42, 8, 42, 48)

    pen.setColor(QColor("#38bdf8"))
    pen.setWidth(5)
    painter.setPen(pen)
    painter.drawLine(12, 34, 44, 22)
    painter.end()
    return icon


def discover_frame_paths() -> List[Path]:
    if not MEDIA_DIR.is_dir():
        return []
    return sorted(
        path for path in MEDIA_DIR.iterdir() if path.is_file() and path.suffix.lower() == ".png"
    )


@lru_cache(maxsize=64)
def load_pixmap(path_str: str) -> QPixmap:
    return QPixmap(path_str)


class FrameDisplayLabel(QLabel):
    def __init__(self):
        super().__init__()
        self._pixmap: Optional[QPixmap] = None
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: transparent; border: none;")
        self.setText("No frames loaded")

    def set_frame(self, pixmap: Optional[QPixmap]):
        self._pixmap = pixmap
        self._refresh()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self):
        if self._pixmap is None or self._pixmap.isNull():
            self.setPixmap(QPixmap())
            if not self.text():
                self.setText("No frames loaded")
            return

        scaled = self._pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.setText("")
        self.setPixmap(scaled)


class SludgeContentSidebarWidget(SidebarWidget):
    def __init__(self, name: str, frame, data):
        super().__init__(name)
        self.frame = frame
        self.data = data
        self.frame_paths: List[Path] = []
        self.current_frame_index = 0

        self.timer = QTimer(self)
        self.timer.setInterval(DEFAULT_FRAME_INTERVAL_MS)
        self.timer.timeout.connect(self.advance_frame)

        self.frame_display = FrameDisplayLabel()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.frame_display)
        self.setLayout(layout)

        self.reload_frames()

    def showEvent(self, event):
        super().showEvent(event)
        self.reload_frames()

    def closing(self):
        self.timer.stop()

    def reload_frames(self):
        self.timer.stop()
        self.frame_paths = discover_frame_paths()
        self.current_frame_index = 0
        load_pixmap.cache_clear()

        if not self.frame_paths:
            self.frame_display.set_frame(None)
            self.frame_display.setText(
                "No PNG frames found.\nExtract sequential frames into the media directory."
            )
            return

        self.render_current_frame()
        self.timer.start()

    def render_current_frame(self):
        if not self.frame_paths:
            return

        current_path = self.frame_paths[self.current_frame_index]
        pixmap = load_pixmap(str(current_path))
        self.frame_display.set_frame(pixmap)

    def advance_frame(self):
        if not self.frame_paths:
            return

        self.current_frame_index = (self.current_frame_index + 1) % len(self.frame_paths)
        self.render_current_frame()


class SludgeContentSidebarWidgetType(SidebarWidgetType):
    def __init__(self):
        super().__init__(build_sidebar_icon(), SIDEBAR_TITLE)

    def createWidget(self, frame, data):
        return SludgeContentSidebarWidget(SIDEBAR_TITLE, frame, data)

    def contextSensitivity(self):
        return SidebarContextSensitivity.GlobalSidebarContext

    def defaultLocation(self):
        return SidebarWidgetLocation.RightContent
