from __future__ import annotations

import json
import subprocess
import sys
import webbrowser
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from nce2_core.batch import batch_import_book2
from nce2_core.models import lesson_from_dict
from nce2_export.generator import export_lesson_html

ROOT = Path(__file__).resolve().parents[1]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NCE2 Sentence Components")
        self.resize(900, 600)
        self.lessons_dir = ROOT / "data" / "lessons"
        self.output_dir = ROOT / "output"
        self.titles_path = ROOT / "data" / "titles.json"
        self.txt_dir = ROOT / "nce_txt" / "第二册"

        self.list_widget = QListWidget()
        for n in range(1, 97):
            self.list_widget.addItem(f"Lesson {n:02d}")
        self.list_widget.setCurrentRow(0)

        self.info_label = QLabel("选择课文，然后导出或演示。")
        self.info_label.setWordWrap(True)

        import_btn = QPushButton("导入 TXT → JSON（全部96课）")
        import_btn.clicked.connect(self.on_import_all)

        export_btn = QPushButton("导出 HTML")
        export_btn.clicked.connect(self.on_export)

        demo_btn = QPushButton("浏览器演示")
        demo_btn.clicked.connect(self.on_demo)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(import_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(demo_btn)

        right = QVBoxLayout()
        right.addWidget(self.info_label)
        right.addLayout(btn_layout)
        right.addStretch()

        layout = QHBoxLayout()
        layout.addWidget(self.list_widget, 1)
        layout.addLayout(right, 2)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _selected_lesson_num(self) -> int | None:
        row = self.list_widget.currentRow()
        if row < 0:
            return None
        return row + 1

    def on_import_all(self) -> None:
        try:
            batch_import_book2(self.txt_dir, self.titles_path, self.lessons_dir)
            QMessageBox.information(self, "完成", "已导入 96 课 JSON。")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def on_export(self) -> None:
        n = self._selected_lesson_num()
        if n is None:
            QMessageBox.warning(self, "提示", "请先选择一课。")
            return
        json_path = self.lessons_dir / f"{n:02d}.json"
        if not json_path.exists():
            QMessageBox.warning(self, "提示", f"找不到 {json_path.name}，请先导入。")
            return
        lesson = lesson_from_dict(json.loads(json_path.read_text(encoding="utf-8")))
        out_path = self.output_dir / f"lesson_{n:02d}.html"
        export_lesson_html(lesson, out_path)
        self.info_label.setText(
            f"已导出: {out_path}\n共 {len(lesson.sentences)} 句"
        )
        QMessageBox.information(self, "完成", f"已导出到\n{out_path}")

    def on_demo(self) -> None:
        n = self._selected_lesson_num()
        if n is None:
            QMessageBox.warning(self, "提示", "请先选择一课。")
            return
        html_path = self.output_dir / f"lesson_{n:02d}.html"
        if not html_path.exists():
            self.on_export()
            if not html_path.exists():
                return
        webbrowser.open(html_path.resolve().as_uri())


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
