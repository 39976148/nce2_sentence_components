from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
)

from nce2_core.ai_config import AiConfig, save_ai_config


class AiSettingsDialog(QDialog):
    def __init__(self, root, cfg: AiConfig, parent=None) -> None:
        super().__init__(parent)
        self.root = root
        self.setWindowTitle("AI 预标注设置")
        self.resize(480, 200)

        self.base_edit = QLineEdit(cfg.api_base)
        self.key_edit = QLineEdit(cfg.api_key)
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.model_edit = QLineEdit(cfg.model)
        self.enabled_cb = QCheckBox("启用 AI 预标注")
        self.enabled_cb.setChecked(cfg.enabled)

        form = QFormLayout(self)
        form.addRow("API Base", self.base_edit)
        form.addRow("API Key", self.key_edit)
        form.addRow("Model", self.model_edit)
        form.addRow("", self.enabled_cb)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _on_save(self) -> None:
        cfg = self.result_config()
        if cfg.enabled and not cfg.api_key.strip():
            QMessageBox.warning(self, "提示", "启用 AI 时需要填写 API Key。")
            return
        save_ai_config(self.root, cfg)
        self.accept()

    def result_config(self) -> AiConfig:
        return AiConfig(
            api_base=self.base_edit.text().strip().rstrip("/"),
            api_key=self.key_edit.text().strip(),
            model=self.model_edit.text().strip() or "gpt-4o-mini",
            enabled=self.enabled_cb.isChecked(),
        )
