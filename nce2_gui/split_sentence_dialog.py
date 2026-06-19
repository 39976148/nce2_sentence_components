from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout


class SplitSentenceDialog(QDialog):
    def __init__(self, original: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("拆分句子")
        self.resize(520, 200)

        hint = QLabel(f"原句：{original}")
        hint.setWordWrap(True)

        self.part1_edit = QLineEdit()
        self.part2_edit = QLineEdit()
        self.part1_edit.setPlaceholderText("第一部分（含标点）")
        self.part2_edit.setPlaceholderText("第二部分（含标点）")

        form = QFormLayout()
        form.addRow("句 1", self.part1_edit)
        form.addRow("句 2", self.part2_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(hint)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def parts(self) -> tuple[str, str]:
        return self.part1_edit.text().strip(), self.part2_edit.text().strip()
