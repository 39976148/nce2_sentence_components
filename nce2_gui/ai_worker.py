from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from nce2_core.ai_annotate import annotate_sentence
from nce2_core.ai_config import AiConfig
from nce2_core.models import Lesson


class AnnotateLessonWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished_ok = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, lesson: Lesson, cfg: AiConfig, sentence_indices: list[int]) -> None:
        super().__init__()
        self.lesson = lesson
        self.cfg = cfg
        self.sentence_indices = sentence_indices

    def run(self) -> None:
        total = len(self.sentence_indices)
        try:
            for i, idx in enumerate(self.sentence_indices, start=1):
                if self.isInterruptionRequested():
                    return
                sentence = self.lesson.sentences[idx]
                self.progress.emit(i, total, f"({sentence.id}) {sentence.original[:40]}...")
                annotate_sentence(sentence, self.cfg)
            self.finished_ok.emit()
        except Exception as e:
            self.failed.emit(str(e))
