from __future__ import annotations

import sys
import webbrowser
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from nce2_core.ai_config import load_ai_config
from nce2_core.app_paths import app_root
from nce2_core.auto_annotate import auto_annotate_lesson, auto_annotate_sentence
from nce2_core.batch import batch_import_book2
from nce2_core.catalog import default_book, lessons_dir, nce_txt_dir, titles_path
from nce2_core.lesson_io import load_lesson, save_lesson
from nce2_core.models import Lesson, Sentence, Token
from nce2_core.roles import ROLE_LABELS
from nce2_core.sentence_ops import merge_with_next, split_sentence, update_sentence_original
from nce2_core.token_ops import apply_expanded, merge_tokens, split_token
from nce2_export.batch_export import export_all_lessons
from nce2_export.generator import export_lesson_html
from nce2_gui.ai_settings_dialog import AiSettingsDialog
from nce2_gui.ai_worker import AnnotateLessonWorker
from nce2_gui.preview_widget import SlidePreviewWidget
from nce2_gui.split_sentence_dialog import SplitSentenceDialog

ROOT = app_root()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NCE2 Sentence Components")
        self.resize(1200, 720)
        self.book = default_book()
        self.lessons_dir = lessons_dir(ROOT)
        self.output_dir = ROOT / "output"
        self.titles_path = titles_path(ROOT)
        self.txt_dir = nce_txt_dir(ROOT)
        self.ai_config = load_ai_config(ROOT)
        self._ai_worker: AnnotateLessonWorker | None = None

        self.current_lesson: Lesson | None = None
        self.current_sentence_index: int = -1
        self._loading_ui = False

        self.lesson_list = QListWidget()
        for n in range(1, 97):
            self.lesson_list.addItem(f"Lesson {n:02d}")
        self.lesson_list.setCurrentRow(0)
        self.lesson_list.currentRowChanged.connect(self.on_lesson_changed)

        self.sentence_list = QListWidget()
        self.sentence_list.currentRowChanged.connect(self.on_sentence_changed)

        self.original_edit = QLineEdit()
        self.original_edit.setPlaceholderText("原文（可编辑）")
        self.original_edit.editingFinished.connect(self.on_original_edited)

        self.expanded_edit = QLineEdit()
        self.expanded_edit.setPlaceholderText("展开句（去缩写）")
        self.expanded_edit.editingFinished.connect(self.on_expanded_edited)

        self.contraction_label = QLabel("")

        self.token_table = QTableWidget(0, 2)
        self.token_table.setHorizontalHeaderLabels(["文本", "成分"])
        self.token_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.token_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.token_table.cellChanged.connect(self.on_token_cell_changed)

        merge_btn = QPushButton("合并词 ↓")
        merge_btn.clicked.connect(self.on_merge_tokens)
        split_word_btn = QPushButton("拆分词")
        split_word_btn.clicked.connect(self.on_split_token)
        split_sent_btn = QPushButton("拆分句子")
        split_sent_btn.clicked.connect(self.on_split_sentence)
        merge_sent_btn = QPushButton("合并下句")
        merge_sent_btn.clicked.connect(self.on_merge_sentence)
        auto_one_btn = QPushButton("自动填成分")
        auto_one_btn.clicked.connect(self.on_auto_fill_sentence)
        auto_lesson_btn = QPushButton("自动填本课")
        auto_lesson_btn.clicked.connect(self.on_auto_fill_lesson)
        save_btn = QPushButton("保存本课")
        save_btn.clicked.connect(self.on_save_lesson)
        ai_cfg_btn = QPushButton("AI 设置")
        ai_cfg_btn.clicked.connect(self.on_ai_settings)
        ai_one_btn = QPushButton("AI 标注本句")
        ai_one_btn.clicked.connect(self.on_ai_sentence)
        ai_lesson_btn = QPushButton("AI 标注本课")
        ai_lesson_btn.clicked.connect(self.on_ai_lesson)

        token_btn_row = QHBoxLayout()
        token_btn_row.addWidget(merge_btn)
        token_btn_row.addWidget(split_word_btn)
        token_btn_row.addWidget(split_sent_btn)
        token_btn_row.addWidget(merge_sent_btn)
        token_btn_row.addWidget(auto_one_btn)
        token_btn_row.addWidget(auto_lesson_btn)
        token_btn_row.addWidget(ai_one_btn)
        token_btn_row.addWidget(ai_lesson_btn)
        token_btn_row.addWidget(ai_cfg_btn)
        token_btn_row.addStretch()
        token_btn_row.addWidget(save_btn)

        self.book_label = QLabel(self.book.label)
        self.book_label.setStyleSheet("color: #555; font-size: 12px;")

        editor_box = QGroupBox("句子编辑")
        editor_layout = QVBoxLayout(editor_box)
        editor_layout.addWidget(QLabel("原文"))
        editor_layout.addWidget(self.original_edit)
        editor_layout.addWidget(QLabel("展开句（去缩写）"))
        editor_layout.addWidget(self.expanded_edit)
        editor_layout.addWidget(self.contraction_label)
        editor_layout.addWidget(self.token_table)
        editor_layout.addLayout(token_btn_row)

        self.preview = SlidePreviewWidget()

        import_btn = QPushButton("导入 TXT → JSON（96课）")
        import_btn.clicked.connect(self.on_import_all)
        export_btn = QPushButton("导出本课 HTML")
        export_btn.clicked.connect(self.on_export)
        export_all_btn = QPushButton("导出全书 HTML")
        export_all_btn.clicked.connect(self.on_export_all)
        demo_btn = QPushButton("浏览器演示")
        demo_btn.clicked.connect(self.on_demo)
        index_btn = QPushButton("打开目录页")
        index_btn.clicked.connect(self.on_open_index)

        action_row = QHBoxLayout()
        action_row.addWidget(import_btn)
        action_row.addWidget(export_btn)
        action_row.addWidget(export_all_btn)
        action_row.addWidget(demo_btn)
        action_row.addWidget(index_btn)

        right = QVBoxLayout()
        right.addWidget(self.book_label)
        right.addWidget(editor_box, 3)
        right.addWidget(QLabel("幻灯片预览"))
        right.addWidget(self.preview, 2)
        right.addLayout(action_row)

        layout = QHBoxLayout()
        layout.addWidget(self.lesson_list, 1)
        layout.addWidget(self.sentence_list, 1)
        layout.addLayout(right, 3)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.on_lesson_changed(self.lesson_list.currentRow())

    def _selected_lesson_num(self) -> int | None:
        row = self.lesson_list.currentRow()
        if row < 0:
            return None
        return row + 1

    def _lesson_path(self, n: int) -> Path:
        return self.lessons_dir / f"{n:02d}.json"

    def _current_sentence(self) -> Sentence | None:
        if self.current_lesson is None or self.current_sentence_index < 0:
            return None
        if self.current_sentence_index >= len(self.current_lesson.sentences):
            return None
        return self.current_lesson.sentences[self.current_sentence_index]

    def on_lesson_changed(self, row: int) -> None:
        if row < 0:
            self.current_lesson = None
            self.sentence_list.clear()
            self._clear_editor()
            return
        n = row + 1
        path = self._lesson_path(n)
        if not path.exists():
            self.current_lesson = None
            self.sentence_list.clear()
            self._clear_editor()
            return
        self.current_lesson = load_lesson(path)
        self._refresh_sentence_list(keep_index=0)

    def _refresh_sentence_list(self, keep_index: int | None = None) -> None:
        if self.current_lesson is None:
            self.sentence_list.clear()
            self._clear_editor()
            return
        prev = self.current_sentence_index if keep_index is None else keep_index
        self.sentence_list.blockSignals(True)
        self.sentence_list.clear()
        for s in self.current_lesson.sentences:
            preview = s.original if len(s.original) <= 48 else s.original[:45] + "..."
            self.sentence_list.addItem(f"({s.id}) {preview}")
        self.sentence_list.blockSignals(False)
        if self.current_lesson.sentences:
            idx = min(max(prev, 0), len(self.current_lesson.sentences) - 1)
            self.sentence_list.setCurrentRow(idx)
        else:
            self._clear_editor()

    def on_sentence_changed(self, row: int) -> None:
        self.current_sentence_index = row
        sentence = self._current_sentence()
        if sentence is None:
            self._clear_editor()
            return
        self._populate_editor(sentence)

    def _clear_editor(self) -> None:
        self._loading_ui = True
        self.original_edit.clear()
        self.expanded_edit.clear()
        self.contraction_label.setText("")
        self.token_table.setRowCount(0)
        self._loading_ui = False
        self.preview.show_sentence(self.current_lesson, None)

    def _populate_editor(self, sentence: Sentence) -> None:
        self._loading_ui = True
        self.original_edit.setText(sentence.original)
        self.expanded_edit.setText(sentence.expanded)
        flag = f"第 {sentence.id} 句 · " + ("含缩写 → 5行" if sentence.has_contraction else "无缩写 → 4行")
        self.contraction_label.setText(flag)

        self.token_table.blockSignals(True)
        self.token_table.setRowCount(len(sentence.tokens))
        for row, token in enumerate(sentence.tokens):
            text_item = QTableWidgetItem(token.text)
            self.token_table.setItem(row, 0, text_item)
            combo = QComboBox()
            combo.setEditable(True)
            combo.addItems(ROLE_LABELS)
            idx = combo.findText(token.role)
            combo.setCurrentIndex(idx if idx >= 0 else 0)
            if token.role and idx < 0:
                combo.setEditText(token.role)
            combo.currentTextChanged.connect(
                lambda _t, r=row: self.on_role_changed(r)
            )
            self.token_table.setCellWidget(row, 1, combo)
        self.token_table.blockSignals(False)
        self._loading_ui = False
        self.preview.show_sentence(self.current_lesson, sentence)

    def _sync_tokens_from_table(self) -> None:
        sentence = self._current_sentence()
        if sentence is None:
            return
        tokens = []
        for row in range(self.token_table.rowCount()):
            item = self.token_table.item(row, 0)
            combo = self.token_table.cellWidget(row, 1)
            text = item.text() if item else ""
            role = combo.currentText() if combo else ""
            tokens.append(Token(text=text.strip(), role=role.strip()))
        sentence.tokens = [t for t in tokens if t.text]

    def _ensure_ai_ready(self) -> bool:
        self.ai_config = load_ai_config(ROOT)
        if self.ai_config.is_ready():
            return True
        QMessageBox.information(
            self,
            "AI 未配置",
            "请先点击「AI 设置」，填写 OpenAI 兼容 API 的 Base URL、API Key 和 Model，并勾选启用。",
        )
        self.on_ai_settings()
        self.ai_config = load_ai_config(ROOT)
        return self.ai_config.is_ready()

    def on_ai_settings(self) -> None:
        dlg = AiSettingsDialog(ROOT, self.ai_config, self)
        if dlg.exec():
            self.ai_config = dlg.result_config()

    def _run_ai_worker(self, indices: list[int]) -> None:
        if self.current_lesson is None or not indices:
            return
        if self._ai_worker and self._ai_worker.isRunning():
            QMessageBox.warning(self, "提示", "AI 标注正在进行中，请稍候。")
            return

        progress = QProgressDialog("AI 预标注中...", "取消", 0, len(indices), self)
        progress.setWindowTitle("AI 预标注")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)

        worker = AnnotateLessonWorker(self.current_lesson, self.ai_config, indices)
        self._ai_worker = worker

        def on_progress(done: int, total: int, msg: str) -> None:
            progress.setMaximum(total)
            progress.setValue(done)
            progress.setLabelText(msg)

        def on_ok() -> None:
            progress.close()
            self._populate_editor(self._current_sentence())
            QMessageBox.information(self, "完成", f"AI 已标注 {len(indices)} 句。")

        def on_fail(msg: str) -> None:
            progress.close()
            QMessageBox.critical(self, "AI 错误", msg)

        worker.progress.connect(on_progress)
        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_fail)
        progress.canceled.connect(worker.requestInterruption)
        worker.start()

    def on_ai_sentence(self) -> None:
        if not self._ensure_ai_ready():
            return
        if self.current_sentence_index < 0:
            QMessageBox.warning(self, "提示", "请先选择一句。")
            return
        self._sync_tokens_from_table()
        self._run_ai_worker([self.current_sentence_index])

    def on_ai_lesson(self) -> None:
        if not self._ensure_ai_ready():
            return
        if self.current_lesson is None or not self.current_lesson.sentences:
            return
        if (
            QMessageBox.question(
                self,
                "确认",
                f"将对本课全部 {len(self.current_lesson.sentences)} 句调用 AI 预标注，是否继续？",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self._sync_tokens_from_table()
        indices = list(range(len(self.current_lesson.sentences)))
        self._run_ai_worker(indices)

    def on_token_cell_changed(self, row: int, column: int) -> None:
        if self._loading_ui or column != 0:
            return
        self._sync_tokens_from_table()
        self.preview.show_sentence(self.current_lesson, self._current_sentence())

    def on_role_changed(self, row: int) -> None:
        if self._loading_ui:
            return
        self._sync_tokens_from_table()
        self.preview.show_sentence(self.current_lesson, self._current_sentence())

    def on_original_edited(self) -> None:
        sentence = self._current_sentence()
        if sentence is None or self._loading_ui:
            return
        new_text = self.original_edit.text().strip()
        if new_text == sentence.original:
            return
        if (
            any(t.role for t in sentence.tokens)
            and QMessageBox.question(
                self,
                "确认",
                "修改原文将重新分词并清空成分，是否继续？",
            )
            != QMessageBox.StandardButton.Yes
        ):
            self.original_edit.setText(sentence.original)
            return
        update_sentence_original(sentence, new_text)
        auto_annotate_sentence(sentence)
        self._populate_editor(sentence)

    def on_split_sentence(self) -> None:
        if self.current_lesson is None or self.current_sentence_index < 0:
            return
        sentence = self._current_sentence()
        if sentence is None:
            return
        dlg = SplitSentenceDialog(sentence.original, self)
        if dlg.exec():
            p1, p2 = dlg.parts()
            try:
                split_sentence(self.current_lesson, self.current_sentence_index, p1, p2)
                for s in self.current_lesson.sentences[
                    self.current_sentence_index : self.current_sentence_index + 2
                ]:
                    auto_annotate_sentence(s)
                self._refresh_sentence_list(keep_index=self.current_sentence_index)
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))

    def on_merge_sentence(self) -> None:
        if self.current_lesson is None or self.current_sentence_index < 0:
            return
        if self.current_sentence_index >= len(self.current_lesson.sentences) - 1:
            QMessageBox.information(self, "提示", "已是本课最后一句，无法合并。")
            return
        try:
            merge_with_next(self.current_lesson, self.current_sentence_index)
            auto_annotate_sentence(self.current_lesson.sentences[self.current_sentence_index])
            self._refresh_sentence_list(keep_index=self.current_sentence_index)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def on_auto_fill_sentence(self) -> None:
        sentence = self._current_sentence()
        if sentence is None:
            return
        self._sync_tokens_from_table()
        auto_annotate_sentence(sentence)
        self._populate_editor(sentence)

    def on_auto_fill_lesson(self) -> None:
        if self.current_lesson is None:
            return
        self._sync_tokens_from_table()
        auto_annotate_lesson(self.current_lesson)
        self._populate_editor(self._current_sentence())
        QMessageBox.information(
            self,
            "完成",
            f"已自动填充本课 {len(self.current_lesson.sentences)} 句成分（可继续手工修改）。",
        )

    def on_expanded_edited(self) -> None:
        sentence = self._current_sentence()
        if sentence is None or self._loading_ui:
            return
        new_text = self.expanded_edit.text().strip()
        if new_text == sentence.expanded:
            return
        if (
            any(t.role for t in sentence.tokens)
            and QMessageBox.question(
                self,
                "确认",
                "修改展开句将重新分词并清空成分标注，是否继续？",
            )
            != QMessageBox.StandardButton.Yes
        ):
            self.expanded_edit.setText(sentence.expanded)
            return
        apply_expanded(sentence, new_text)
        auto_annotate_sentence(sentence)
        self._populate_editor(sentence)

    def on_merge_tokens(self) -> None:
        sentence = self._current_sentence()
        if sentence is None:
            return
        row = self.token_table.currentRow()
        if row < 0:
            row = self.token_table.rowCount() - 2
        sentence.tokens = merge_tokens(sentence.tokens, row)
        self._populate_editor(sentence)

    def on_split_token(self) -> None:
        sentence = self._current_sentence()
        if sentence is None:
            return
        row = self.token_table.currentRow()
        if row < 0:
            return
        sentence.tokens = split_token(sentence.tokens, row)
        self._populate_editor(sentence)

    def on_save_lesson(self) -> None:
        if self.current_lesson is None:
            return
        self._sync_tokens_from_table()
        n = self.current_lesson.lesson
        save_lesson(self.current_lesson, self._lesson_path(n))
        QMessageBox.information(self, "完成", f"已保存 Lesson {n:02d}.json")

    def on_import_all(self) -> None:
        try:
            batch_import_book2(self.txt_dir, self.titles_path, self.lessons_dir)
            self.on_lesson_changed(self.lesson_list.currentRow())
            QMessageBox.information(self, "完成", "已导入 96 课 JSON。")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def on_export(self) -> None:
        if self.current_lesson is None:
            QMessageBox.warning(self, "提示", "请先选择一课。")
            return
        self._sync_tokens_from_table()
        n = self.current_lesson.lesson
        out_path = self.output_dir / f"lesson_{n:02d}.html"
        export_lesson_html(self.current_lesson, out_path)
        QMessageBox.information(
            self, "完成", f"已导出到\n{out_path}\n共 {len(self.current_lesson.sentences)} 句"
        )

    def on_export_all(self) -> None:
        if not self.lessons_dir.exists():
            QMessageBox.warning(self, "提示", "请先导入课文 JSON。")
            return
        self._sync_tokens_from_table()
        if self.current_lesson:
            save_lesson(self.current_lesson, self._lesson_path(self.current_lesson.lesson))
        try:
            index = export_all_lessons(self.lessons_dir, self.output_dir)
            QMessageBox.information(
                self,
                "完成",
                f"已导出 96 课 HTML\n目录页：\n{index}",
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def on_open_index(self) -> None:
        index_path = self.output_dir / "index.html"
        if not index_path.exists():
            self.on_export_all()
        if index_path.exists():
            webbrowser.open(index_path.resolve().as_uri())

    def on_demo(self) -> None:
        n = self._selected_lesson_num()
        if n is None:
            return
        html_path = self.output_dir / f"lesson_{n:02d}.html"
        if not html_path.exists():
            self.on_export()
        if html_path.exists():
            webbrowser.open(html_path.resolve().as_uri())


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
