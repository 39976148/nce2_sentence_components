from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from nce2_core.models import Lesson, Sentence


class SlidePreviewWidget(QFrame):
    """In-app preview matching exported slide layout (4 or 5 lines)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.setMinimumHeight(220)

        mono = QFont("Consolas")
        mono.setPointSize(11)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #4060a0; font-size: 13px;")

        self.original_label = QLabel()
        self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_label.setFont(mono)

        self.expanded_label = QLabel()
        self.expanded_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.expanded_label.setFont(mono)
        self.expanded_label.setStyleSheet("color: #b8860b;")

        self.analysis_container = QWidget()
        self.analysis_layout = QHBoxLayout(self.analysis_container)
        self.analysis_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.analysis_layout.setSpacing(4)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        layout.addWidget(self.original_label)
        layout.addWidget(self.expanded_label)
        layout.addWidget(self.analysis_container)

    def show_sentence(self, lesson: Lesson | None, sentence: Sentence | None) -> None:
        self._clear_analysis()
        if lesson is None or sentence is None:
            self.title_label.setText("（预览）")
            self.original_label.setText("")
            self.expanded_label.setText("")
            self.expanded_label.hide()
            return

        self.title_label.setText(f"Lesson {lesson.lesson}: {lesson.title}")
        self.original_label.setText(f"({sentence.id}) {sentence.original}")
        if sentence.has_contraction:
            self.expanded_label.setText(f"({sentence.id}) {sentence.expanded}")
            self.expanded_label.show()
        else:
            self.expanded_label.hide()

        mono = QFont("Consolas")
        mono.setPointSize(11)
        for token in sentence.tokens:
            group = QWidget()
            v = QVBoxLayout(group)
            v.setSpacing(2)
            v.setContentsMargins(6, 0, 6, 0)

            word = QLabel(token.text)
            word.setAlignment(Qt.AlignmentFlag.AlignCenter)
            word.setFont(mono)

            line = QFrame()
            line.setFixedHeight(2)
            line.setStyleSheet("background: #06a060;")

            role = QLabel(token.role if token.role else "—")
            role.setAlignment(Qt.AlignmentFlag.AlignCenter)
            role.setFont(mono)
            role.setStyleSheet("color: #06a060; font-size: 10px;")

            v.addWidget(word, alignment=Qt.AlignmentFlag.AlignHCenter)
            v.addWidget(line)
            v.addWidget(role, alignment=Qt.AlignmentFlag.AlignHCenter)
            self.analysis_layout.addWidget(group)

    def _clear_analysis(self) -> None:
        while self.analysis_layout.count():
            item = self.analysis_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
