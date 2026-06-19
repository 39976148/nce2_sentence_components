# NCE2 Sentence Components

新概念英语第二册（NCE2）句子成分分析 + HTML 幻灯片演示工具。

## 功能（P1 MVP）

- 从 `nce_txt/第二册/` 解析课文（96 课）
- 自动分句编号、缩写展开
- 导出单文件 HTML 幻灯片（每句一页，键盘 ← → 翻页）
- 有缩写句 5 行 / 无缩写句 4 行
- PyQt6 GUI：选课文、批量导入、导出、浏览器演示

## 安装

```powershell
cd D:\cursor_work\nce2_sentence_components
pip install -r requirements.txt
```

## 准备数据

1. 将 NCE2 课文 TXT 放到 `nce_txt/第二册/`（1.TXT … 96.TXT）
2. 生成标题表：`python scripts/gen_titles.py`
3. 批量导入 JSON：

```powershell
python -c "from pathlib import Path; from nce2_core.batch import batch_import_book2; batch_import_book2(Path('nce_txt/第二册'), Path('data/titles.json'), Path('data/lessons'))"
```

或在 GUI 中点击「导入 TXT → JSON」。

## 启动 GUI

```powershell
python -m nce2_gui.main
```

## 演示

1. 选择课文 → 「导出 HTML」→ `output/lesson_NN.html`
2. 「浏览器演示」或手动打开 HTML
3. 浏览器按 **F11** 全屏，**← →** 翻页

## 测试

```powershell
python -m pytest tests/ -v
```

## 项目结构

```
nce2_core/     解析、分句、缩写、数据模型（无 Qt 依赖）
nce2_export/   HTML 幻灯片生成
nce2_gui/      PyQt6 桌面界面
data/          titles.json + lessons/*.json
docs/          设计规格与实施计划
```

## 路线图

- **P2**：GUI 成分编辑（Token 表格、下拉标签、预览）
- **P3**：可选 AI 预标注、四册扩展
- **远期**：核心库移植 C++/Qt6 小 exe

## 文档

- 设计规格：`docs/superpowers/specs/2026-06-19-nce2-sentence-components-design.md`
- P1 计划：`docs/superpowers/plans/2026-06-19-nce2-sentence-components-p1.md`
